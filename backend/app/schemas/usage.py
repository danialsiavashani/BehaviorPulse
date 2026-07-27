import uuid

from pydantic import BaseModel


class UsageByService(BaseModel):
    service_key: str
    count: int


class UsageByApp(BaseModel):
    client_app_id: uuid.UUID
    app_name: str
    count: int


class UsageByDay(BaseModel):
    date: str
    count: int


class UsageOut(BaseModel):
    total_requests: int
    success_count: int
    error_count: int
    success_rate: float
    by_service: list[UsageByService]
    by_app: list[UsageByApp]
    requests_over_time: list[UsageByDay]