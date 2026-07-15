import hashlib

from fastapi import Header
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import Depends

from app.core.errors import InvalidApiKeyError, MissingApiKeyError, ServiceNotEnabledError
from app.db.models.api_key import ApiKey
from app.db.models.client_app import ClientApp
from app.db.models.client_service_scope import ClientServiceScope
from app.db.session import get_db


def _hash_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode()).hexdigest()


def require_service_auth(service_key: str):
    def dependency(
        x_client_id: str | None = Header(default=None),
        x_api_key: str | None = Header(default=None),
        db: Session = Depends(get_db),
    ) -> ClientApp:
        if not x_client_id or not x_api_key:
            raise MissingApiKeyError()

        client_app = db.scalar(select(ClientApp).where(ClientApp.client_id == x_client_id))
        if client_app is None:
            raise InvalidApiKeyError()

        key_hash = _hash_key(x_api_key)
        api_key = db.scalar(
            select(ApiKey).where(
                ApiKey.client_app_id == client_app.id,
                ApiKey.key_hash == key_hash,
                ApiKey.is_active == True,  # noqa: E712
            )
        )
        if api_key is None:
            raise InvalidApiKeyError()

        scope = db.scalar(
            select(ClientServiceScope).where(
                ClientServiceScope.client_app_id == client_app.id,
                ClientServiceScope.service_key == service_key,
                ClientServiceScope.enabled == True,  # noqa: E712
            )
        )
        if scope is None:
            raise ServiceNotEnabledError()

        return client_app

    return dependency