from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models.request_log import ApiRequestLog


def write_request_log(
    db: Session,
    *,
    client_app_id: UUID | None,
    service_key: str,
    endpoint: str,
    method: str,
    status_code: int,
    success: bool,
    error_code: str | None,
    latency_ms: int,
    request_id: str,
) -> None:
    db.add(
        ApiRequestLog(
            client_app_id=client_app_id,
            service_key=service_key,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            success=success,
            error_code=error_code,
            latency_ms=latency_ms,
            request_id=request_id,
        )
    )
    db.commit()