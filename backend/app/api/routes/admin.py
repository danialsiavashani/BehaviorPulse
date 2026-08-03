import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin_user
from app.core.errors import AppError
from app.db.models.admin_action_log import AdminActionLog
from app.db.models.client_app import ClientApp
from app.db.models.refresh_token import RefreshToken
from app.db.models.request_log import ApiRequestLog
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.admin import (
    AdminMeOut,
    AdminSignupsByDay,
    AdminStatsOut,
    AdminUserOut,
    AdminUserUpdate,
)
from app.schemas.pagination import PaginatedResponse, PaginationParams
from app.services.token_revocation import revoke_all_refresh_tokens

router = APIRouter(prefix="/v1/admin", tags=["admin"])

STATS_SIGNUP_WINDOW_DAYS = 30
RECENT_SIGNUPS_LIMIT = 5


def _serialize_admin_user(db: Session, user: User) -> AdminUserOut:
    """Single-user version of the aggregate lookup used by get/patch. Not
    used by list_users - that one batches all three aggregates in a single
    joined query instead of running this per row across a page."""
    app_count = db.scalar(
        select(func.count()).select_from(ClientApp).where(ClientApp.owner_user_id == user.id)
    )
    request_count = db.scalar(
        select(func.count())
        .select_from(ApiRequestLog)
        .join(ClientApp, ApiRequestLog.client_app_id == ClientApp.id)
        .where(ClientApp.owner_user_id == user.id)
    )
    last_active_at = db.scalar(
        select(func.max(RefreshToken.created_at)).where(RefreshToken.user_id == user.id)
    )
    return AdminUserOut(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role,
        is_active=user.is_active,
        is_demo=user.is_demo,
        created_at=user.created_at,
        app_count=app_count or 0,
        request_count=request_count or 0,
        last_active_at=last_active_at,
    )


def _count_other_active_admins(db: Session, excluding_user_id: uuid.UUID) -> int:
    return db.scalar(
        select(func.count()).select_from(
            select(User.id)
            .where(User.role == "admin", User.is_active == True, User.id != excluding_user_id)  # noqa: E712
            .subquery()
        )
    )


@router.get("/me", response_model=AdminMeOut)
def read_admin_me(current_admin: User = Depends(get_current_admin_user)):
    return current_admin


@router.get("/stats", response_model=AdminStatsOut)
def get_stats(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user),
):
    total_users = db.scalar(select(func.count()).select_from(User))
    demo_users = db.scalar(select(func.count()).select_from(User).where(User.is_demo == True))  # noqa: E712
    active_users = db.scalar(select(func.count()).select_from(User).where(User.is_active == True))  # noqa: E712
    total_requests = db.scalar(select(func.count()).select_from(ApiRequestLog))

    window_start = datetime.now(timezone.utc) - timedelta(days=STATS_SIGNUP_WINDOW_DAYS - 1)
    daily_rows = db.execute(
        select(func.date(User.created_at).label("day"), func.count().label("count"))
        .where(User.created_at >= window_start)
        .group_by(func.date(User.created_at))
    ).all()
    counts_by_day = {row.day.isoformat(): row.count for row in daily_rows}

    signups_over_time = []
    for i in range(STATS_SIGNUP_WINDOW_DAYS):
        day = (window_start + timedelta(days=i)).date().isoformat()
        signups_over_time.append(AdminSignupsByDay(date=day, count=counts_by_day.get(day, 0)))

    recent_signups = db.scalars(
        select(User).order_by(User.created_at.desc()).limit(RECENT_SIGNUPS_LIMIT)
    ).all()

    return AdminStatsOut(
        total_users=total_users,
        demo_users=demo_users,
        real_users=total_users - demo_users,
        active_users=active_users,
        disabled_users=total_users - active_users,
        total_requests=total_requests,
        signups_over_time=signups_over_time,
        recent_signups=recent_signups,
    )


@router.get("/users", response_model=PaginatedResponse[AdminUserOut])
def list_users(
    search: str | None = Query(default=None, description="Filters by email, case-insensitive substring match"),
    is_active: bool | None = Query(default=None),
    is_demo: bool | None = Query(default=None),
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user),
):
    filters = []
    if search:
        filters.append(User.email.ilike(f"%{search}%"))
    if is_active is not None:
        filters.append(User.is_active == is_active)
    if is_demo is not None:
        filters.append(User.is_demo == is_demo)

    total = db.scalar(select(func.count()).select_from(select(User.id).where(*filters).subquery()))

    app_counts = (
        select(ClientApp.owner_user_id.label("user_id"), func.count().label("app_count"))
        .group_by(ClientApp.owner_user_id)
        .subquery()
    )
    request_counts = (
        select(ClientApp.owner_user_id.label("user_id"), func.count(ApiRequestLog.id).label("request_count"))
        .select_from(ApiRequestLog)
        .join(ClientApp, ApiRequestLog.client_app_id == ClientApp.id)
        .group_by(ClientApp.owner_user_id)
        .subquery()
    )
    last_active = (
        select(RefreshToken.user_id.label("user_id"), func.max(RefreshToken.created_at).label("last_active_at"))
        .group_by(RefreshToken.user_id)
        .subquery()
    )

    rows = db.execute(
        select(
            User,
            func.coalesce(app_counts.c.app_count, 0).label("app_count"),
            func.coalesce(request_counts.c.request_count, 0).label("request_count"),
            last_active.c.last_active_at,
        )
        .outerjoin(app_counts, app_counts.c.user_id == User.id)
        .outerjoin(request_counts, request_counts.c.user_id == User.id)
        .outerjoin(last_active, last_active.c.user_id == User.id)
        .where(*filters)
        .order_by(User.created_at.desc())
        .offset(pagination.offset)
        .limit(pagination.page_size)
    ).all()

    items = [
        AdminUserOut(
            id=row.User.id,
            email=row.User.email,
            name=row.User.name,
            role=row.User.role,
            is_active=row.User.is_active,
            is_demo=row.User.is_demo,
            created_at=row.User.created_at,
            app_count=row.app_count,
            request_count=row.request_count,
            last_active_at=row.last_active_at,
        )
        for row in rows
    ]

    return PaginatedResponse(items=items, total=total, page=pagination.page, page_size=pagination.page_size)


@router.get("/users/{user_id}", response_model=AdminUserOut)
def get_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user),
):
    user = db.get(User, user_id)
    if user is None:
        raise AppError("not_found", "User not found.", 404)

    return _serialize_admin_user(db, user)


@router.patch("/users/{user_id}", response_model=AdminUserOut)
def update_user(
    user_id: uuid.UUID,
    payload: AdminUserUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user),
):
    if user_id == current_admin.id:
        raise AppError(
            "cannot_modify_self",
            "You can't change your own role or status from the admin panel - use your account settings instead.",
            403,
        )

    target = db.get(User, user_id)
    if target is None:
        raise AppError("not_found", "User not found.", 404)

    is_currently_live_admin = target.role == "admin" and target.is_active
    would_demote = payload.role is not None and payload.role != "admin"
    would_disable = payload.is_active is False

    if is_currently_live_admin and (would_demote or would_disable):
        if _count_other_active_admins(db, excluding_user_id=target.id) == 0:
            raise AppError(
                "last_admin",
                "Can't remove the last active admin. Promote someone else first.",
                409,
            )

    if payload.role is not None and payload.role != target.role:
        db.add(AdminActionLog(
            admin_id=current_admin.id,
            target_user_id=target.id,
            action="change_role",
            previous_value=target.role,
            new_value=payload.role,
        ))
        target.role = payload.role

    if payload.is_active is not None and payload.is_active != target.is_active:
        db.add(AdminActionLog(
            admin_id=current_admin.id,
            target_user_id=target.id,
            action="enable_user" if payload.is_active else "disable_user",
            previous_value=str(target.is_active),
            new_value=str(payload.is_active),
        ))
        target.is_active = payload.is_active
        if not payload.is_active:
            # Same instant-kill path as change-password/change-email -
            # disabling shouldn't wait for the access token to expire.
            revoke_all_refresh_tokens(db, target.id, reason="security_action")

    db.commit()
    db.refresh(target)

    return _serialize_admin_user(db, target)