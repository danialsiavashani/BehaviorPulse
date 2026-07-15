import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ApiKeyCreate(BaseModel):
    client_app_id: uuid.UUID
    name: str = Field(min_length=1, max_length=255)


class ApiKeyCreated(BaseModel):
    id: uuid.UUID
    name: str
    key_prefix: str
    raw_key: str
    created_at: datetime


class ApiKeyOut(BaseModel):
    id: uuid.UUID
    name: str
    key_prefix: str
    is_active: bool
    created_at: datetime
    revoked_at: datetime | None
    last_used_at: datetime | None

    class Config:
        from_attributes = True