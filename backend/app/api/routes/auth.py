import secrets
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.errors import AppError
from app.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.db.models.api_key import ApiKey
from app.db.models.client_app import ClientApp
from app.db.models.client_service_scope import ClientServiceScope
from app.db.models.observation_analysis import ObservationAnalysis
from app.db.models.password_reset_token import PasswordResetToken
from app.db.models.refresh_token import RefreshToken
from app.db.models.request_log import ApiRequestLog
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.auth import (
    EmailChange,
    ForgotPasswordRequest,
    LogoutRequest,
    PasswordChange,
    RefreshRequest,
    ResetPasswordRequest,
    Token,
    UserCreate,
    UserLogin,
    UserOut,
    UserUpdate,
)
from app.services.email.factory import get_email_client
from app.services.seed_demo_data import seed_demo_data

import logging

logger = logging.getLogger("signaltally")

router = APIRouter(prefix="/v1/auth", tags=["auth"])


def _build_tokens(db: Session, user: User) -> Token:
    raw_refresh = generate_refresh_token()
    refresh_row = RefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token(raw_refresh),
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days),
    )
    db.add(refresh_row)

    access_token = create_access_token(subject=str(user.id), token_version=user.token_version)
    return Token(access_token=access_token, refresh_token=raw_refresh)


def _revoke_all_refresh_tokens(db: Session, user_id, reason: str) -> None:
    db.execute(
        update(RefreshToken)
        .where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
        .values(revoked_at=datetime.now(timezone.utc), revoked_reason=reason)
    )


def _delete_user_and_all_data(db: Session, user: User) -> None:
    """Cascading delete shared by real account deletion, demo-account
    sweeping, and demo-account logout - one place, not three copies."""
    client_app_ids = db.scalars(
        select(ClientApp.id).where(ClientApp.owner_user_id == user.id)
    ).all()

    if client_app_ids:
        db.execute(delete(ApiRequestLog).where(ApiRequestLog.client_app_id.in_(client_app_ids)))
        db.execute(
            delete(ObservationAnalysis).where(ObservationAnalysis.client_app_id.in_(client_app_ids))
        )
        db.execute(
            delete(ClientServiceScope).where(ClientServiceScope.client_app_id.in_(client_app_ids))
        )
        db.execute(delete(ApiKey).where(ApiKey.client_app_id.in_(client_app_ids)))
        db.execute(delete(ClientApp).where(ClientApp.id.in_(client_app_ids)))

    db.execute(delete(RefreshToken).where(RefreshToken.user_id == user.id))
    db.delete(user)


def _sweep_stale_demo_accounts(db: Session) -> None:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=settings.demo_account_max_age_hours)
    stale_users = db.scalars(
        select(User).where(User.is_demo == True, User.created_at < cutoff)  # noqa: E712
    ).all()
    for user in stale_users:
        _delete_user_and_all_data(db, user)


@router.post("/signup", response_model=UserOut, status_code=201)
def signup(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise AppError("email_taken", "An account with this email already exists.", 409)
    user = User(email=payload.email, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise AppError("invalid_credentials", "Incorrect email or password.", 401)

    token = _build_tokens(db, user)
    db.commit()
    return token


@router.post("/demo-login", response_model=Token)
def demo_login(db: Session = Depends(get_db)):
    _sweep_stale_demo_accounts(db)

    demo_email = f"demo_{uuid.uuid4().hex[:12]}@behaviorpulse.demo"
    user = User(
        email=demo_email,
        password_hash=hash_password(secrets.token_urlsafe(24)),
        is_demo=True,
    )
    db.add(user)
    db.flush()  # need user.id populated before seeding references it

    seed_demo_data(db, user.id)

    token = _build_tokens(db, user)
    db.commit()
    return token


@router.post("/refresh", response_model=Token)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    token_hash = hash_refresh_token(payload.refresh_token)
    existing = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == token_hash))

    if existing is None:
        raise AppError("invalid_token", "Invalid or expired refresh token.", 401)

    if existing.revoked_at is not None:
        seconds_since_revoked = (datetime.now(timezone.utc) - existing.revoked_at).total_seconds()
        within_grace_period = seconds_since_revoked <= settings.refresh_reuse_grace_seconds

        if within_grace_period and existing.revoked_reason == "rotated":
            user = db.get(User, existing.user_id)
            if user is None:
                raise AppError("invalid_token", "Invalid or expired refresh token.", 401)
            token = _build_tokens(db, user)
            db.commit()
            return token

        user = db.get(User, existing.user_id)
        if user is not None:
            user.token_version += 1
        _revoke_all_refresh_tokens(db, existing.user_id, reason="security_action")
        db.commit()
        raise AppError("invalid_token", "Invalid or expired refresh token.", 401)

    if existing.expires_at < datetime.now(timezone.utc):
        existing.revoked_at = datetime.now(timezone.utc)
        existing.revoked_reason = "expired"
        db.commit()
        raise AppError("invalid_token", "Invalid or expired refresh token.", 401)

    user = db.get(User, existing.user_id)
    if user is None:
        raise AppError("invalid_token", "Invalid or expired refresh token.", 401)

    existing.revoked_at = datetime.now(timezone.utc)
    existing.revoked_reason = "rotated"
    token = _build_tokens(db, user)
    db.commit()
    return token


@router.post("/logout", status_code=204)
def logout(payload: LogoutRequest, db: Session = Depends(get_db)):
    token_hash = hash_refresh_token(payload.refresh_token)
    existing = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == token_hash))

    if existing is None or existing.revoked_at is not None:
        return

    user = db.get(User, existing.user_id)

    if user is not None and user.is_demo:
        # Demo accounts don't linger - logging out fully removes it
        # immediately, rather than waiting for the next sweep.
        _delete_user_and_all_data(db, user)
        db.commit()
        return

    existing.revoked_at = datetime.now(timezone.utc)
    existing.revoked_reason = "logout"
    db.commit()


@router.post("/forgot-password", status_code=204)
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email))

    if user is not None:
        raw_token = generate_refresh_token()
        reset_row = PasswordResetToken(
            user_id=user.id,
            token_hash=hash_refresh_token(raw_token),
            expires_at=datetime.now(timezone.utc)
            + timedelta(minutes=settings.password_reset_token_expire_minutes),
        )
        db.add(reset_row)
        db.commit()

        frontend_url = (settings.frontend_url or "").rstrip("/")
        reset_link = f"{frontend_url}/reset-password?token={raw_token}"

        try:
            get_email_client().send_password_reset_email(user.email, reset_link)
        except Exception as exc:
            logger.warning(
                "Failed to send password reset email to %s: %s. Reset link: %s",
                user.email,
                exc,
                reset_link,
            )

    return None


@router.post("/reset-password", response_model=Token)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    token_hash = hash_refresh_token(payload.token)
    existing = db.scalar(select(PasswordResetToken).where(PasswordResetToken.token_hash == token_hash))

    if existing is None or existing.used_at is not None or existing.expires_at < datetime.now(timezone.utc):
        raise AppError("invalid_token", "This reset link is invalid or has expired.", 400)

    user = db.get(User, existing.user_id)
    if user is None:
        raise AppError("invalid_token", "This reset link is invalid or has expired.", 400)

    user.password_hash = hash_password(payload.new_password)
    user.token_version += 1
    _revoke_all_refresh_tokens(db, user.id, reason="security_action")
    existing.used_at = datetime.now(timezone.utc)

    token = _build_tokens(db, user)
    db.commit()
    return token


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserOut)
def update_me(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    current_user.name = payload.name
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/change-password", response_model=Token)
def change_password(
    payload: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(payload.current_password, current_user.password_hash):
        raise AppError("invalid_credentials", "Current password is incorrect.", 401)

    current_user.password_hash = hash_password(payload.new_password)
    current_user.token_version += 1
    _revoke_all_refresh_tokens(db, current_user.id, reason="security_action")

    token = _build_tokens(db, current_user)
    db.commit()
    return token


@router.post("/change-email", response_model=Token)
def change_email(
    payload: EmailChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(payload.current_password, current_user.password_hash):
        raise AppError("invalid_credentials", "Current password is incorrect.", 401)

    existing = db.scalar(
        select(User).where(User.email == payload.new_email, User.id != current_user.id)
    )
    if existing is not None:
        raise AppError("email_taken", "An account with this email already exists.", 409)

    current_user.email = payload.new_email
    current_user.token_version += 1
    _revoke_all_refresh_tokens(db, current_user.id, reason="security_action")

    token = _build_tokens(db, current_user)
    db.commit()
    return token


@router.delete("/me", status_code=204)
def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _delete_user_and_all_data(db, current_user)
    db.commit()