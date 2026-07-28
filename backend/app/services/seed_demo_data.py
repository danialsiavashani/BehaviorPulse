import secrets
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.db.models.api_key import ApiKey
from app.db.models.client_app import ClientApp
from app.db.models.client_service_scope import ClientServiceScope
from app.db.models.observation_analysis import ObservationAnalysis
from app.db.models.request_log import ApiRequestLog


def _generate_client_id() -> str:
    return f"client_{secrets.token_hex(8)}"


def _generate_raw_key() -> str:
    return f"bp_sk_{secrets.token_hex(24)}"


def _hash_key(raw_key: str) -> str:
    import hashlib

    return hashlib.sha256(raw_key.encode()).hexdigest()


def _generate_analysis_id() -> str:
    return f"ana_{secrets.token_hex(8)}"


# Frozen, real DeepSeek output from an actual /v1/observations/analyze call
# against realistic month-long datasets - not written by hand. Regenerating
# this on every demo visit would mean latency on their first click and a
# small risk of a flaky LLM response; freezing genuine output keeps it
# instant while staying honest about what the LLM actually produced.
_WILDLIFE_ANALYSIS = {
    "subject_type": "animal",
    "subject_label": "hummingbird",
    "total_observations": 28,
    "computed_confidence": 0.97,
    "summary": (
        "Over 28 observations, the most common subject was hummingbirds (57.1%), "
        "followed by cats (28.6%), with blue jays and dogs each at 7.1%. The average "
        "confidence is high (0.9007) and stable. The top source is camera_04, and the "
        "peak activity occurs on Saturdays between 6 AM and 8 AM. A recurring pattern "
        "is noted: observations occurred on 5 of the last 5 Saturdays."
    ),
    "prediction": (
        "Based on the strong recurring pattern and high prediction confidence (0.97), "
        "it is likely that hummingbird activity will continue to be observed on "
        "Saturdays during the early morning window, though occasional variations may "
        "occur."
    ),
    "pattern_table": [
        {"metric": "total_observations", "value": "28", "support": "28 matching observations in the selected date range"},
        {"metric": "most_common_subject", "value": "hummingbird", "support": "hummingbird accounted for 16 of 28 observations"},
        {"metric": "most_active_source", "value": "camera_04", "support": "camera_04 recorded 18 of 28 observations"},
        {"metric": "most_active_time_window", "value": "6 AM - 8 AM", "support": "14 of 28 observations occurred in this window"},
        {"metric": "recurring_day", "value": "Saturday", "support": "Observed 5 of the last 5 Saturdays"},
    ],
    "computed_metrics": {
        "total_observations": 28,
        "average_confidence": 0.9007,
        "top_subjects": [
            {"subject_label": "hummingbird", "count": 16, "percentage": 57.1},
            {"subject_label": "cat", "count": 8, "percentage": 28.6},
            {"subject_label": "blue_jay", "count": 2, "percentage": 7.1},
            {"subject_label": "dog", "count": 2, "percentage": 7.1},
        ],
        "top_sources": [
            {"source_id": "camera_04", "count": 18, "percentage": 64.3},
            {"source_id": "camera_02", "count": 10, "percentage": 35.7},
        ],
        "top_day_of_week": {"day": "Saturday", "count": 16, "percentage": 57.1},
        "top_time_window": {"window": "6 AM - 8 AM", "count": 14, "percentage": 50},
    },
    "recommendations": [
        "Focus monitoring efforts on camera_04 during Saturday mornings (6-8 AM) to capture peak hummingbird activity.",
        "Consider additional observation periods to confirm if the pattern extends to other days or times.",
        "Review cat observations to assess if they occur at different times and may require separate analysis.",
    ],
    "warnings": ["Predictions are pattern estimates based on historical observations, not guarantees."],
}

_TRAFFIC_ANALYSIS = {
    "subject_type": "vehicle",
    "subject_label": "sedan",
    "total_observations": 28,
    "computed_confidence": 0.78,
    "summary": (
        "Over 28 observations, the most common subject is 'sedan' (60.7%), followed by "
        "'pedestrian' (21.4%), 'SUV' (10.7%), and 'truck' (7.1%). The average confidence "
        "is high (0.9014) and stable. The primary source is intersection_a, with the "
        "most activity on Tuesdays between 4 PM and 6 PM. A recurring pattern shows "
        "observations on 4 of the last 5 Tuesdays."
    ),
    "prediction": (
        "Given the recurring pattern and high confidence, it is likely that similar "
        "observations will continue on future Tuesdays during the 4 PM - 6 PM window "
        "at intersection_a, with sedans being the predominant subject. However, this "
        "is not guaranteed and should be monitored."
    ),
    "pattern_table": [
        {"metric": "total_observations", "value": "28", "support": "28 matching observations in the selected date range"},
        {"metric": "most_common_subject", "value": "sedan", "support": "sedan accounted for 17 of 28 observations"},
        {"metric": "most_active_source", "value": "intersection_a", "support": "intersection_a recorded 28 of 28 observations"},
        {"metric": "most_active_time_window", "value": "4 PM - 6 PM", "support": "19 of 28 observations occurred in this window"},
        {"metric": "recurring_day", "value": "Tuesday", "support": "Observed 4 of the last 5 Tuesdays"},
    ],
    "computed_metrics": {
        "total_observations": 28,
        "average_confidence": 0.9014,
        "top_subjects": [
            {"subject_label": "sedan", "count": 17, "percentage": 60.7},
            {"subject_label": "pedestrian", "count": 6, "percentage": 21.4},
            {"subject_label": "suv", "count": 3, "percentage": 10.7},
            {"subject_label": "truck", "count": 2, "percentage": 7.1},
        ],
        "top_sources": [{"source_id": "intersection_a", "count": 28, "percentage": 100}],
        "top_day_of_week": {"day": "Tuesday", "count": 12, "percentage": 42.9},
        "top_time_window": {"window": "4 PM - 6 PM", "count": 19, "percentage": 67.9},
    },
    "recommendations": [
        "Focus monitoring on intersection_a during Tuesday 4-6 PM to gather more data on the recurring pattern.",
        "Consider pedestrian safety measures given the significant proportion of pedestrian observations.",
    ],
    "warnings": ["Predictions are pattern estimates based on historical observations, not guarantees."],
}


def _seed_app(db: Session, user_id: uuid.UUID, name: str, analysis_data: dict) -> None:
    app = ClientApp(
        owner_user_id=user_id,
        name=name,
        environment="production",
        client_id=_generate_client_id(),
    )
    db.add(app)
    db.flush()  # so app.id is populated for the foreign keys below

    db.add(ClientServiceScope(client_app_id=app.id, service_key="observations.analyze", enabled=True))

    raw_key = _generate_raw_key()
    db.add(
        ApiKey(
            client_app_id=app.id,
            key_prefix=raw_key[:12],
            key_hash=_hash_key(raw_key),
            name="Demo Key",
        )
    )

    db.add(
        ObservationAnalysis(
            client_app_id=app.id,
            analysis_id=_generate_analysis_id(),
            subject_type=analysis_data["subject_type"],
            subject_label=analysis_data["subject_label"],
            total_observations=analysis_data["total_observations"],
            computed_confidence=analysis_data["computed_confidence"],
            summary=analysis_data["summary"],
            prediction=analysis_data["prediction"],
            pattern_table_json=analysis_data["pattern_table"],
            computed_metrics_json=analysis_data["computed_metrics"],
            recommendations_json=analysis_data["recommendations"],
            warnings_json=analysis_data["warnings"],
        )
    )

    now = datetime.now(timezone.utc)
    for days_ago in (1, 3, 6, 10, 14, 20):
        db.add(
            ApiRequestLog(
                client_app_id=app.id,
                service_key="observations.analyze",
                endpoint="/v1/observations/analyze",
                method="POST",
                status_code=200,
                success=True,
                error_code=None,
                latency_ms=850 + (days_ago * 13) % 400,
                request_id=uuid.uuid4().hex,
                created_at=now - timedelta(days=days_ago, hours=days_ago % 5),
            )
        )


def seed_demo_data(db: Session, user_id: uuid.UUID) -> None:
    """Seeds a fresh demo account with two realistic apps, each with an
    enabled scope, an API key, one real (frozen) LLM-generated analysis,
    and a handful of request-log rows for Usage/Logs to show real data.

    Does not commit - the caller controls the transaction boundary."""
    _seed_app(db, user_id, "Wildlife Detection", _WILDLIFE_ANALYSIS)
    _seed_app(db, user_id, "Traffic Cam Pilot", _TRAFFIC_ANALYSIS)