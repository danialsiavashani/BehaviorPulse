import uuid
from datetime import datetime

from pydantic import BaseModel


class ApiRequestLogOut(BaseModel):
    id: uuid.UUID
    client_app_id: uuid.UUID | None
    service_key: str | None
    endpoint: str
    method: str
    status_code: int
    success: bool
    error_code: str | None
    latency_ms: int
    request_id: str
    created_at: datetime

    class Config:
        from_attributes = True