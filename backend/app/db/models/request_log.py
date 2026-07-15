import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ApiRequestLog(Base):
    __tablename__ = "api_request_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_app_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("client_apps.id"), nullable=True)
    service_key: Mapped[str | None] = mapped_column(String(100), nullable=True)
    endpoint: Mapped[str] = mapped_column(String(255), nullable=False)
    method: Mapped[str] = mapped_column(String(10), nullable=False)
    status_code: Mapped[int] = mapped_column(Integer, nullable=False)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    error_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    request_id: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())