from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.models.service import Service
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.pagination import PaginatedResponse, PaginationParams
from app.schemas.service import ServiceOut

router = APIRouter(prefix="/v1/services", tags=["services"])


@router.get("", response_model=PaginatedResponse[ServiceOut])
def list_services(
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    base_query = select(Service)

    total = db.scalar(select(func.count()).select_from(base_query.subquery()))

    services = db.scalars(
        base_query.order_by(Service.name).offset(pagination.offset).limit(pagination.page_size)
    ).all()

    return PaginatedResponse(
        items=services,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    )