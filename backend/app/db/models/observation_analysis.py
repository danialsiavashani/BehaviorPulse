import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ObservationAnalysis(Base):
    __tablename__ = "observation_analyses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_app_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("client_apps.id"), nullable=False)
    analysis_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    subject_type: Mapped[str] = mapped_column(String(100), nullable=False)
    subject_label: Mapped[str] = mapped_column(String(255), nullable=False)
    total_observations: Mapped[int] = mapped_column(Integer, nullable=False)
    computed_confidence: Mapped[float] = mapped_column(Float, nullable=False)
    summary: Mapped[str] = mapped_column(String(2000), nullable=False)
    prediction: Mapped[str] = mapped_column(String(2000), nullable=False)
    pattern_table_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    computed_metrics_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    recommendations_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    warnings_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())