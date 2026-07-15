from datetime import datetime

from pydantic import BaseModel


class ScopeCreate(BaseModel):
    service_key: str


class ScopeOut(BaseModel):
    service_key: str
    enabled: bool
    created_at: datetime

    class Config:
        from_attributes = True