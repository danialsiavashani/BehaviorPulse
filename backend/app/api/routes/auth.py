from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import select, update
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
from app.db.models.refresh_token import RefreshToken
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.auth import (
    EmailChange,
    LogoutRequest,
    PasswordChange,
    RefreshRequest,
    Token,
    UserCreate,
    UserLogin,
    UserOut,
    UserUpdate,
)

router = APIRouter(prefix="/v1/auth", tags=["auth"])


def _build_tokens(db: Session, user: User) -> Token:
    """Adds a new refresh token row (uncommitted) and returns a fresh
    access/refresh pair. Caller is responsible for db.commit()."""
    raw_refresh = generate_refresh_token()
    refresh_row = RefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token(raw_refresh),
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days),
    )
    db.add(refresh_row)

    access_token = create_access_token(subject=str(user.id), token_version=user.token_version)
    return Token(access_token=access_token, refresh_token=raw_refresh)


def _revoke_all_refresh_tokens(db: Session, user_id) -> None:
    db.execute(
        update(RefreshToken)
        .where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
        .values(revoked_at=datetime.now(timezone.utc))
    )


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


@router.post("/refresh", response_model=Token)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    token_hash = hash_refresh_token(payload.refresh_token)
    existing = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == token_hash))

    if existing is None:
        raise AppError("invalid_token", "Invalid or expired refresh token.", 401)

    if existing.revoked_at is not None:
        # This token was already rotated away once. Being presented again
        # means it was likely stolen before the legitimate rotation - treat
        # it as a compromise signal and kill every session for this user.
        user = db.get(User, existing.user_id)
        if user is not None:
            user.token_version += 1
        _revoke_all_refresh_tokens(db, existing.user_id)
        db.commit()
        raise AppError("invalid_token", "Invalid or expired refresh token.", 401)

    if existing.expires_at < datetime.now(timezone.utc):
        existing.revoked_at = datetime.now(timezone.utc)
        db.commit()
        raise AppError("invalid_token", "Invalid or expired refresh token.", 401)

    user = db.get(User, existing.user_id)
    if user is None:
        raise AppError("invalid_token", "Invalid or expired refresh token.", 401)

    existing.revoked_at = datetime.now(timezone.utc)
    token = _build_tokens(db, user)
    db.commit()
    return token


@router.post("/logout", status_code=204)
def logout(payload: LogoutRequest, db: Session = Depends(get_db)):
    token_hash = hash_refresh_token(payload.refresh_token)
    existing = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
    if existing is not None and existing.revoked_at is None:
        existing.revoked_at = datetime.now(timezone.utc)
        db.commit()


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
    _revoke_all_refresh_tokens(db, current_user.id)

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
    _revoke_all_refresh_tokens(db, current_user.id)

    token = _build_tokens(db, current_user)
    db.commit()
    return token