import uuid
from datetime import datetime

from pydantic import BaseModel


class ServiceOut(BaseModel):
    id: uuid.UUID
    service_key: str
    name: str
    description: str
    status: str
    endpoint: str
    created_at: datetime

    class Config:
        from_attributes = True