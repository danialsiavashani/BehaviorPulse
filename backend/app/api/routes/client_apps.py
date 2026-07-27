import secrets
import uuid

from app.core.errors import AppError

from fastapi import APIRouter, Depends
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.models.client_app import ClientApp
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.client_app import ClientAppCreate, ClientAppOut
from app.schemas.pagination import PaginatedResponse, PaginationParams
from app.db.models.client_service_scope import ClientServiceScope
from app.schemas.client_service_scope import ScopeCreate, ScopeOut
from fastapi import APIRouter, Depends, Response
from app.db.models.api_key import ApiKey
from app.db.models.observation_analysis import ObservationAnalysis
from app.db.models.request_log import ApiRequestLog

router = APIRouter(prefix="/v1/apps", tags=["client_apps"])


def _generate_client_id() -> str:
    return f"client_{secrets.token_hex(8)}"


@router.post("", response_model=ClientAppOut, status_code=201)
def create_client_app(
    payload: ClientAppCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    client_app = ClientApp(
        owner_user_id=current_user.id,
        name=payload.name,
        environment=payload.environment,
        client_id=_generate_client_id(),
    )
    db.add(client_app)
    db.commit()
    db.refresh(client_app)
    return client_app


@router.get("", response_model=PaginatedResponse[ClientAppOut])
def list_client_apps(
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    base_query = select(ClientApp).where(ClientApp.owner_user_id == current_user.id)

    total = db.scalar(select(func.count()).select_from(base_query.subquery()))

    apps = db.scalars(
        base_query.order_by(ClientApp.created_at.desc())
        .offset(pagination.offset)
        .limit(pagination.page_size)
    ).all()

    return PaginatedResponse(
        items=apps,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    )

@router.get("/{client_app_id}/scopes", response_model=list[ScopeOut])
def list_scopes(
    client_app_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    client_app = db.get(ClientApp, client_app_id)
    if client_app is None or client_app.owner_user_id != current_user.id:
        raise AppError("not_found", "Client app not found.", 404)

    scopes = db.scalars(
        select(ClientServiceScope).where(ClientServiceScope.client_app_id == client_app_id)
    ).all()
    return scopes


@router.post("/{client_app_id}/scopes", response_model=ScopeOut, status_code=201)
def set_scope(
    client_app_id: uuid.UUID,
    payload: ScopeCreate,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    client_app = db.get(ClientApp, client_app_id)
    if client_app is None or client_app.owner_user_id != current_user.id:
        raise AppError("not_found", "Client app not found.", 404)

    existing = db.scalar(
        select(ClientServiceScope).where(
            ClientServiceScope.client_app_id == client_app_id,
            ClientServiceScope.service_key == payload.service_key,
        )
    )
    if existing:
        existing.enabled = payload.enabled
        db.commit()
        db.refresh(existing)
        response.status_code = 200
        return existing

    scope = ClientServiceScope(
        client_app_id=client_app_id,
        service_key=payload.service_key,
        enabled=payload.enabled,
    )
    db.add(scope)
    db.commit()
    db.refresh(scope)
    return scope

@router.delete("/{client_app_id}", status_code=204)
def delete_client_app(
    client_app_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    client_app = db.get(ClientApp, client_app_id)
    if client_app is None or client_app.owner_user_id != current_user.id:
        raise AppError("not_found", "Client app not found.", 404)

    db.execute(delete(ApiRequestLog).where(ApiRequestLog.client_app_id == client_app_id))
    db.execute(delete(ObservationAnalysis).where(ObservationAnalysis.client_app_id == client_app_id))
    db.execute(delete(ClientServiceScope).where(ClientServiceScope.client_app_id == client_app_id))
    db.execute(delete(ApiKey).where(ApiKey.client_app_id == client_app_id))

    db.delete(client_app)
    db.commit()