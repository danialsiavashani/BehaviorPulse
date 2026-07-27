import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: uuid.UUID
    email: EmailStr
    name: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"