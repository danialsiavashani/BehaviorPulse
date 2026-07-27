from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.models.client_app import ClientApp
from app.db.models.request_log import ApiRequestLog
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.usage import UsageByApp, UsageByDay, UsageByService, UsageOut

router = APIRouter(prefix="/v1/usage", tags=["usage"])

USAGE_WINDOW_DAYS = 14


@router.get("", response_model=UsageOut)
def get_usage(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    base_query = (
        select(ApiRequestLog)
        .join(ClientApp, ApiRequestLog.client_app_id == ClientApp.id)
        .where(ClientApp.owner_user_id == current_user.id)
    )

    total_requests = db.scalar(select(func.count()).select_from(base_query.subquery()))
    success_count = db.scalar(
        select(func.count()).select_from(
            base_query.where(ApiRequestLog.success == True).subquery()  # noqa: E712
        )
    )
    error_count = total_requests - success_count
    success_rate = round((success_count / total_requests) * 100, 1) if total_requests else 0.0

    by_service_rows = db.execute(
        select(ApiRequestLog.service_key, func.count().label("count"))
        .join(ClientApp, ApiRequestLog.client_app_id == ClientApp.id)
        .where(ClientApp.owner_user_id == current_user.id)
        .group_by(ApiRequestLog.service_key)
        .order_by(func.count().desc())
    ).all()
    by_service = [
        UsageByService(service_key=row.service_key or "unknown", count=row.count)
        for row in by_service_rows
    ]

    by_app_rows = db.execute(
        select(ClientApp.id, ClientApp.name, func.count().label("count"))
        .select_from(ApiRequestLog)
        .join(ClientApp, ApiRequestLog.client_app_id == ClientApp.id)
        .where(ClientApp.owner_user_id == current_user.id)
        .group_by(ClientApp.id, ClientApp.name)
        .order_by(func.count().desc())
    ).all()
    by_app = [
        UsageByApp(client_app_id=row.id, app_name=row.name, count=row.count)
        for row in by_app_rows
    ]

    window_start = datetime.now(timezone.utc) - timedelta(days=USAGE_WINDOW_DAYS - 1)
    daily_rows = db.execute(
        select(func.date(ApiRequestLog.created_at).label("day"), func.count().label("count"))
        .join(ClientApp, ApiRequestLog.client_app_id == ClientApp.id)
        .where(
            ClientApp.owner_user_id == current_user.id,
            ApiRequestLog.created_at >= window_start,
        )
        .group_by(func.date(ApiRequestLog.created_at))
    ).all()
    counts_by_day = {row.day.isoformat(): row.count for row in daily_rows}

    requests_over_time = []
    for i in range(USAGE_WINDOW_DAYS):
        day = (window_start + timedelta(days=i)).date().isoformat()
        requests_over_time.append(UsageByDay(date=day, count=counts_by_day.get(day, 0)))

    return UsageOut(
        total_requests=total_requests,
        success_count=success_count,
        error_count=error_count,
        success_rate=success_rate,
        by_service=by_service,
        by_app=by_app,
        requests_over_time=requests_over_time,
    )