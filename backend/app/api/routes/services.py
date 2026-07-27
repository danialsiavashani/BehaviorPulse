from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.errors import AppError
from app.db.models.client_app import ClientApp
from app.db.models.client_service_scope import ClientServiceScope
from app.db.models.service import Service
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.client_app import ClientAppOut
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


@router.get("/{service_key}", response_model=ServiceOut)
def get_service(
    service_key: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = db.scalar(select(Service).where(Service.service_key == service_key))
    if service is None:
        raise AppError("not_found", "Service not found.", 404)

    return service


@router.get("/{service_key}/apps", response_model=list[ClientAppOut])
def list_apps_with_service_enabled(
    service_key: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = db.scalar(select(Service).where(Service.service_key == service_key))
    if service is None:
        raise AppError("not_found", "Service not found.", 404)

    apps = db.scalars(
        select(ClientApp)
        .join(ClientServiceScope, ClientServiceScope.client_app_id == ClientApp.id)
        .where(
            ClientApp.owner_user_id == current_user.id,
            ClientServiceScope.service_key == service_key,
            ClientServiceScope.enabled == True,  # noqa: E712
        )
        .order_by(ClientApp.name)
    ).all()

    return apps