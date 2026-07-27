import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.models.client_app import ClientApp
from app.db.models.request_log import ApiRequestLog
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.pagination import PaginatedResponse, PaginationParams
from app.schemas.request_log import ApiRequestLogOut

router = APIRouter(prefix="/v1/logs", tags=["logs"])


@router.get("", response_model=PaginatedResponse[ApiRequestLogOut])
def list_logs(
    client_app_id: uuid.UUID | None = Query(default=None),
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    base_query = (
        select(ApiRequestLog)
        .join(ClientApp, ApiRequestLog.client_app_id == ClientApp.id)
        .where(ClientApp.owner_user_id == current_user.id)
    )

    if client_app_id is not None:
        base_query = base_query.where(ApiRequestLog.client_app_id == client_app_id)

    total = db.scalar(select(func.count()).select_from(base_query.subquery()))

    logs = db.scalars(
        base_query.order_by(ApiRequestLog.created_at.desc())
        .offset(pagination.offset)
        .limit(pagination.page_size)
    ).all()

    return PaginatedResponse(
        items=logs,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    )