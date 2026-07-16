from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SubjectIn(BaseModel):
    type: str
    label: str


class SourceIn(BaseModel):
    type: str
    id: str


class ObservationIn(BaseModel):
    observed_at: datetime
    source: SourceIn
    confidence: float = Field(ge=0.0, le=1.0)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AnalysisOptions(BaseModel):
    timezone: str = "UTC"
    date_from: datetime | None = None
    date_to: datetime | None = None
    lookback_days: int = 30
    prediction_window_days: int = 7
    time_bucket_hours: int = 2


class ObservationAnalyzeRequest(BaseModel):
    analysis_type: str = "activity_patterns"
    subject: SubjectIn
    observations: list[ObservationIn] = Field(min_length=1)
    options: AnalysisOptions = Field(default_factory=AnalysisOptions)


class PatternTableRow(BaseModel):
    metric: str
    value: str
    support: str


class TopSource(BaseModel):
    source_id: str
    count: int
    percentage: float


class TopDayOfWeek(BaseModel):
    day: str
    count: int
    percentage: float


class TopTimeWindow(BaseModel):
    window: str
    count: int
    percentage: float


class ComputedMetrics(BaseModel):
    total_observations: int
    average_confidence: float
    top_sources: list[TopSource]
    top_day_of_week: TopDayOfWeek | None = None
    top_time_window: TopTimeWindow | None = None


class ObservationAnalyzeResponse(BaseModel):
    analysis_id: str
    status: str
    summary: str
    prediction: str
    computed_confidence: float
    pattern_table: list[PatternTableRow]
    computed_metrics: ComputedMetrics
    recommendations: list[str]
    warnings: list[str]