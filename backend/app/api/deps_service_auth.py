import hashlib
import time

from fastapi import Header, Request
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import Depends

from app.core.errors import InvalidApiKeyError, MissingApiKeyError, ServiceNotEnabledError
from app.core.request_logging import write_request_log
from app.db.models.api_key import ApiKey
from app.db.models.client_app import ClientApp
from app.db.models.client_service_scope import ClientServiceScope
from app.db.session import get_db


def _hash_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode()).hexdigest()


def require_service_auth(service_key: str):
    def dependency(
        request: Request,
        x_client_id: str | None = Header(default=None),
        x_api_key: str | None = Header(default=None),
        db: Session = Depends(get_db),
    ) -> ClientApp:
        start = time.monotonic()
        request_id = getattr(request.state, "request_id", "unknown")

        def log_failure(status_code: int, error_code: str, client_app_id=None) -> None:
            write_request_log(
                db,
                client_app_id=client_app_id,
                service_key=service_key,
                endpoint=request.url.path,
                method=request.method,
                status_code=status_code,
                success=False,
                error_code=error_code,
                latency_ms=int((time.monotonic() - start) * 1000),
                request_id=request_id,
            )

        if not x_client_id or not x_api_key:
            log_failure(401, "missing_api_key")
            raise MissingApiKeyError()

        client_app = db.scalar(select(ClientApp).where(ClientApp.client_id == x_client_id))
        if client_app is None:
            log_failure(401, "invalid_api_key")
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
            log_failure(401, "invalid_api_key", client_app_id=client_app.id)
            raise InvalidApiKeyError()

        scope = db.scalar(
            select(ClientServiceScope).where(
                ClientServiceScope.client_app_id == client_app.id,
                ClientServiceScope.service_key == service_key,
                ClientServiceScope.enabled == True,  # noqa: E712
            )
        )
        if scope is None:
            log_failure(403, "service_not_enabled", client_app_id=client_app.id)
            raise ServiceNotEnabledError()

        # Auth passed - stash for observations.py to log the final outcome
        # (success or payload_too_large) once the real work is done.
        request.state.log_start_time = start
        request.state.service_key = service_key

        return client_app

    return dependency