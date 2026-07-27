import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel


class ObservationAnalysisListItem(BaseModel):
    id: uuid.UUID
    analysis_id: str
    client_app_id: uuid.UUID
    app_name: str
    subject_type: str
    subject_label: str
    total_observations: int
    computed_confidence: float
    summary: str
    created_at: datetime


class ObservationAnalysisDetail(BaseModel):
    id: uuid.UUID
    analysis_id: str
    client_app_id: uuid.UUID
    app_name: str
    subject_type: str
    subject_label: str
    total_observations: int
    computed_confidence: float
    summary: str
    prediction: str
    pattern_table: list[dict[str, Any]]
    computed_metrics: dict[str, Any]
    recommendations: list[str]
    warnings: list[str]
    created_at: datetime