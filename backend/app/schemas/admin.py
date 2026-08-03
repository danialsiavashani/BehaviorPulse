import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class AdminMeOut(BaseModel):
    id: uuid.UUID
    email: str
    name: str | None
    role: str

    class Config:
        from_attributes = True


class AdminUserOut(BaseModel):
    id: uuid.UUID
    email: str
    name: str | None
    role: str
    is_active: bool
    is_demo: bool
    created_at: datetime
    app_count: int
    request_count: int
    # Derived from the most recent RefreshToken.created_at for this user,
    # not a dedicated "last login" column - rotation issues a new refresh
    # token on every /refresh call too, so this reads as "last time this
    # user's session was active," which is what actually exists to query.
    last_active_at: datetime | None


class AdminUserUpdate(BaseModel):
    role: str | None = Field(default=None, pattern="^(user|admin)$")
    is_active: bool | None = None


class AdminSignupsByDay(BaseModel):
    date: str
    count: int


class AdminRecentSignup(BaseModel):
    id: uuid.UUID
    email: str
    created_at: datetime
    is_demo: bool

    class Config:
        from_attributes = True


class AdminStatsOut(BaseModel):
    total_users: int
    demo_users: int
    real_users: int
    active_users: int
    disabled_users: int
    total_requests: int
    signups_over_time: list[AdminSignupsByDay]
    recent_signups: list[AdminRecentSignup]