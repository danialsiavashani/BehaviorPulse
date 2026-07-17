import secrets

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps_service_auth import require_service_auth
from app.core.errors import PayloadTooLargeError
from app.db.models.client_app import ClientApp
from app.db.models.observation_analysis import ObservationAnalysis
from app.db.session import get_db
from app.schemas.observation import (
    ComputedMetrics,
    ObservationAnalyzeRequest,
    ObservationAnalyzeResponse,
    PatternTableRow,
    TopDayOfWeek,
    TopSource,
    TopSubject,
    TopTimeWindow,
)
from app.services.analytics.engine import run_observation_analytics
from app.services.llm.factory import get_llm_client
from app.services.llm.fallback_client import FallbackClient

router = APIRouter(prefix="/v1/observations", tags=["observations"])

MAX_OBSERVATIONS = 5000


def _generate_analysis_id() -> str:
    return f"ana_{secrets.token_hex(8)}"


@router.post("/analyze", response_model=ObservationAnalyzeResponse)
def analyze_observations(
    payload: ObservationAnalyzeRequest,
    db: Session = Depends(get_db),
    current_client: ClientApp = Depends(require_service_auth("observations.analyze")),
):
    if len(payload.observations) > MAX_OBSERVATIONS:
        raise PayloadTooLargeError(
            f"This request contains too many observations for synchronous "
            f"analysis (max {MAX_OBSERVATIONS}). Please reduce the date range "
            f"or use async analysis in a future version."
        )

    result = run_observation_analytics(
        observations=payload.observations,
        timezone_name=payload.options.timezone,
        date_from=payload.options.date_from,
        date_to=payload.options.date_to,
        lookback_days=payload.options.lookback_days,
        time_bucket_hours=payload.options.time_bucket_hours,
    )

    analysis_id = _generate_analysis_id()
    warnings = ["Predictions are pattern estimates based on historical observations, not guarantees."]

    if result["empty"]:
        computed_metrics = ComputedMetrics(
            total_observations=0, average_confidence=0.0, top_subjects=[], top_sources=[]
        )
        summary = "No observations found in the selected date range."
        prediction = "Not enough data to make a prediction."
        recommendations = ["Widen the date range or provide more observation data."]
        computed_confidence = 0.0
        pattern_table = [
            PatternTableRow(
                metric="total_observations",
                value="0",
                support="No matching observations in the selected date range",
            )
        ]
        subject_type = "unknown"
        subject_label = "none"
    else:
        llm_client = get_llm_client()
        if isinstance(llm_client, FallbackClient):
            warnings.append("No LLM provider configured - using a deterministic fallback summary.")

        llm_result = llm_client.summarize_observation_analysis(result["evidence_packet"])

        summary = llm_result["summary"]
        prediction = llm_result["prediction"]
        recommendations = llm_result["recommendations"]
        computed_confidence = result["prediction_confidence"]

        computed_metrics = ComputedMetrics(
            total_observations=result["total_observations"],
            average_confidence=result["average_confidence"],
            top_subjects=[TopSubject(**s) for s in result["top_subjects"]],
            top_sources=[TopSource(**s) for s in result["top_sources"]],
            top_day_of_week=TopDayOfWeek(**result["top_day_of_week"]) if result["top_day_of_week"] else None,
            top_time_window=TopTimeWindow(**result["top_time_window"]) if result["top_time_window"] else None,
        )
        pattern_table = [PatternTableRow(**row) for row in result["pattern_table"]]

        # Representative label for the DB record - the top subject in this
        # batch. Full per-subject breakdown lives in computed_metrics_json.
        top_subject_label = result["top_subjects"][0]["subject_label"] if result["top_subjects"] else "unknown"
        matching_obs = next(
            (o for o in payload.observations if o.subject.label == top_subject_label), None
        )
        subject_type = matching_obs.subject.type if matching_obs else "unknown"
        subject_label = top_subject_label

    analysis_record = ObservationAnalysis(
        client_app_id=current_client.id,
        analysis_id=analysis_id,
        subject_type=subject_type,
        subject_label=subject_label,
        total_observations=computed_metrics.total_observations,
        computed_confidence=computed_confidence,
        summary=summary,
        prediction=prediction,
        pattern_table_json=[row.model_dump() for row in pattern_table],
        computed_metrics_json=computed_metrics.model_dump(),
        recommendations_json=recommendations,
        warnings_json=warnings,
    )
    db.add(analysis_record)
    db.commit()

    return ObservationAnalyzeResponse(
        analysis_id=analysis_id,
        status="completed",
        summary=summary,
        prediction=prediction,
        computed_confidence=computed_confidence,
        pattern_table=pattern_table,
        computed_metrics=computed_metrics,
        recommendations=recommendations,
        warnings=warnings,
    )