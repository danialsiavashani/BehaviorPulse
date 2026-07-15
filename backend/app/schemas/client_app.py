import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ClientAppCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    environment: str = Field(default="production", max_length=50)


class ClientAppOut(BaseModel):
    id: uuid.UUID
    name: str
    environment: str
    client_id: str
    created_at: datetime

    class Config:
        from_attributes = True