import hashlib
import secrets
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.errors import AppError
from app.db.models.api_key import ApiKey
from app.db.models.client_app import ClientApp
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.api_key import ApiKeyCreate, ApiKeyCreated, ApiKeyOut

router = APIRouter(prefix="/v1/api-keys", tags=["api_keys"])


def _generate_raw_key() -> str:
    return f"bp_sk_{secrets.token_hex(24)}"


def _hash_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode()).hexdigest()


def _get_owned_client_app(db: Session, client_app_id: uuid.UUID, user_id: uuid.UUID) -> ClientApp:
    client_app = db.get(ClientApp, client_app_id)
    if client_app is None or client_app.owner_user_id != user_id:
        raise AppError("not_found", "Client app not found.", 404)
    return client_app


@router.post("", response_model=ApiKeyCreated, status_code=201)
def create_api_key(
    payload: ApiKeyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_owned_client_app(db, payload.client_app_id, current_user.id)

    raw_key = _generate_raw_key()
    key_prefix = raw_key[:12]

    api_key = ApiKey(
        client_app_id=payload.client_app_id,
        key_prefix=key_prefix,
        key_hash=_hash_key(raw_key),
        name=payload.name,
    )
    db.add(api_key)
    db.commit()
    db.refresh(api_key)

    return ApiKeyCreated(
        id=api_key.id,
        name=api_key.name,
        key_prefix=api_key.key_prefix,
        raw_key=raw_key,
        created_at=api_key.created_at,
    )


@router.get("", response_model=list[ApiKeyOut])
def list_api_keys(
    client_app_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_owned_client_app(db, client_app_id, current_user.id)
    keys = db.scalars(select(ApiKey).where(ApiKey.client_app_id == client_app_id)).all()
    return keys


@router.post("/{api_key_id}/revoke", response_model=ApiKeyOut)
def revoke_api_key(
    api_key_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    api_key = db.get(ApiKey, api_key_id)
    if api_key is None:
        raise AppError("not_found", "API key not found.", 404)

    _get_owned_client_app(db, api_key.client_app_id, current_user.id)

    api_key.is_active = False
    api_key.revoked_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(api_key)
    return api_key