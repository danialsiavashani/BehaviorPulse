import secrets
import uuid

from app.core.errors import AppError

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.models.client_app import ClientApp
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.client_app import ClientAppCreate, ClientAppOut
from app.db.models.client_service_scope import ClientServiceScope
from app.schemas.client_service_scope import ScopeCreate, ScopeOut

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


@router.get("", response_model=list[ClientAppOut])
def list_client_apps(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    apps = db.scalars(select(ClientApp).where(ClientApp.owner_user_id == current_user.id)).all()
    return apps


@router.post("/{client_app_id}/scopes", response_model=ScopeOut, status_code=201)
def grant_scope(
    client_app_id: uuid.UUID,
    payload: ScopeCreate,
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
        existing.enabled = True
        db.commit()
        db.refresh(existing)
        return existing

    scope = ClientServiceScope(client_app_id=client_app_id, service_key=payload.service_key)
    db.add(scope)
    db.commit()
    db.refresh(scope)
    return scope