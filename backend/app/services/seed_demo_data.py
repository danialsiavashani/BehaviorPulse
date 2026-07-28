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


# Frozen, real DeepSeek output from actual runs of the real analytics
# engine + LLM client against realistic month-long datasets - not written
# by hand. Each app's list represents a genuine narrative: the same
# consumer re-running analysis periodically as more real data came in,
# so prediction confidence climbs across the list rather than being
# static. Each entry here becomes exactly one ObservationAnalysis row
# and one matching ApiRequestLog row - no log without a real analysis
# behind it.

_WILDLIFE_ANALYSES = [
    {
        "days_ago": 21,
        "subject_type": "animal",
        "subject_label": "hummingbird",
        "total_observations": 3,
        "computed_confidence": 0.13,
        "summary": "From 3 sightings, hummingbirds were most common (67%) over blue jays (33%), with high average confidence (0.88). Activity peaked Saturday 6-8 AM on camera_04, but the pattern is weak: only 1 of the last 5 Saturdays had a sighting.",
        "prediction": "Given the low frequency (1 of 5 Saturdays) and very low prediction confidence (0.13), a similar sighting next Saturday is unlikely based on available data.",
        "pattern_table": [
            {"metric": "total_observations", "value": "3", "support": "3 matching observations in the selected date range"},
            {"metric": "most_common_subject", "value": "hummingbird", "support": "hummingbird accounted for 2 of 3 observations"},
            {"metric": "most_active_source", "value": "camera_04", "support": "camera_04 recorded 3 of 3 observations"},
            {"metric": "most_active_time_window", "value": "6 AM - 8 AM", "support": "3 of 3 observations occurred in this window"},
            {"metric": "recurring_day", "value": "Saturday", "support": "Observed 1 of the last 5 Saturdays"},
        ],
        "computed_metrics": {
            "total_observations": 3,
            "average_confidence": 0.88,
            "top_subjects": [
                {"subject_label": "hummingbird", "count": 2, "percentage": 66.7},
                {"subject_label": "blue_jay", "count": 1, "percentage": 33.3},
            ],
            "top_sources": [{"source_id": "camera_04", "count": 3, "percentage": 100.0}],
            "top_day_of_week": {"day": "Saturday", "count": 3, "percentage": 100.0},
            "top_time_window": {"window": "6 AM - 8 AM", "count": 3, "percentage": 100.0},
        },
        "recommendations": [
            "Continue monitoring camera_04 during Saturday morning windows to gather more data.",
            "Consider increasing sampling or adjusting camera placement if higher detection rates are desired.",
        ],
    },
    {
        "days_ago": 15,
        "subject_type": "animal",
        "subject_label": "hummingbird",
        "total_observations": 9,
        "computed_confidence": 0.29,
        "summary": "Out of 9 total observations, hummingbirds were the most frequent subject (6 observations, 66.7%), followed by cats (2) and blue jays (1). Average confidence in detections was high (0.89). Most observations came from camera_04, on Saturdays between 6-8 AM. A recurring pattern shows hummingbirds observed on 2 of the last 5 Saturdays.",
        "prediction": "Based on the low prediction confidence (0.29), it is uncertain whether the pattern will continue. However, if it does, the most likely next observation would be a hummingbird on a Saturday morning.",
        "pattern_table": [
            {"metric": "total_observations", "value": "9", "support": "9 matching observations in the selected date range"},
            {"metric": "most_common_subject", "value": "hummingbird", "support": "hummingbird accounted for 6 of 9 observations"},
            {"metric": "most_active_source", "value": "camera_04", "support": "camera_04 recorded 7 of 9 observations"},
            {"metric": "most_active_time_window", "value": "6 AM - 8 AM", "support": "6 of 9 observations occurred in this window"},
            {"metric": "recurring_day", "value": "Saturday", "support": "Observed 2 of the last 5 Saturdays"},
        ],
        "computed_metrics": {
            "total_observations": 9,
            "average_confidence": 0.8922,
            "top_subjects": [
                {"subject_label": "hummingbird", "count": 6, "percentage": 66.7},
                {"subject_label": "cat", "count": 2, "percentage": 22.2},
                {"subject_label": "blue_jay", "count": 1, "percentage": 11.1},
            ],
            "top_sources": [
                {"source_id": "camera_04", "count": 7, "percentage": 77.8},
                {"source_id": "camera_02", "count": 2, "percentage": 22.2},
            ],
            "top_day_of_week": {"day": "Saturday", "count": 6, "percentage": 66.7},
            "top_time_window": {"window": "6 AM - 8 AM", "count": 6, "percentage": 66.7},
        },
        "recommendations": [
            "Increase monitoring on Saturday mornings to gather more data.",
            "Consider calibrating camera_04 to improve detection confidence if needed.",
            "Explore whether environmental factors (e.g., feeders) attract hummingbirds at that time.",
        ],
    },
    {
        "days_ago": 10,
        "subject_type": "animal",
        "subject_label": "hummingbird",
        "total_observations": 15,
        "computed_confidence": 0.48,
        "summary": "Out of 15 observations across 3 subjects, hummingbird was the most frequent (60%), followed by cat (26.7%) and blue jay (13.3%). Average confidence is high (0.89) and stable. Most activity came from camera_04 on Saturdays between 6-8 AM, with a recurring pattern observed on 3 of the last 5 Saturdays.",
        "prediction": "Based on the recurring Saturday pattern, similar activity is likely to occur on upcoming Saturdays during the early morning window at camera_04, but the moderate prediction confidence (0.48) indicates this is not certain.",
        "pattern_table": [
            {"metric": "total_observations", "value": "15", "support": "15 matching observations in the selected date range"},
            {"metric": "most_common_subject", "value": "hummingbird", "support": "hummingbird accounted for 9 of 15 observations"},
            {"metric": "most_active_source", "value": "camera_04", "support": "camera_04 recorded 11 of 15 observations"},
            {"metric": "most_active_time_window", "value": "6 AM - 8 AM", "support": "9 of 15 observations occurred in this window"},
            {"metric": "recurring_day", "value": "Saturday", "support": "Observed 3 of the last 5 Saturdays"},
        ],
        "computed_metrics": {
            "total_observations": 15,
            "average_confidence": 0.8913,
            "top_subjects": [
                {"subject_label": "hummingbird", "count": 9, "percentage": 60.0},
                {"subject_label": "cat", "count": 4, "percentage": 26.7},
                {"subject_label": "blue_jay", "count": 2, "percentage": 13.3},
            ],
            "top_sources": [
                {"source_id": "camera_04", "count": 11, "percentage": 73.3},
                {"source_id": "camera_02", "count": 4, "percentage": 26.7},
            ],
            "top_day_of_week": {"day": "Saturday", "count": 9, "percentage": 60.0},
            "top_time_window": {"window": "6 AM - 8 AM", "count": 9, "percentage": 60.0},
        },
        "recommendations": [
            "Continue monitoring camera_04 during Saturday mornings to confirm the pattern.",
            "Consider increasing observation coverage on other days to see if the pattern is unique to Saturdays.",
            "Use the high and stable confidence to inform automated alerts for hummingbird detections.",
        ],
    },
    {
        "days_ago": 5,
        "subject_type": "animal",
        "subject_label": "hummingbird",
        "total_observations": 21,
        "computed_confidence": 0.7,
        "summary": "Based on 21 observations across 4 subjects, hummingbirds are the most frequent (57.1%), followed by cats (28.6%). Observations are concentrated on Saturdays from 6-8 AM via camera_04. Average confidence is high (0.90) and stable, with a recurring pattern of sightings on 4 of the last 5 Saturdays.",
        "prediction": "Given the recurring pattern and a prediction confidence of 0.7, it is likely that similar activity will continue, with hummingbirds and cats being the most probable subjects during early Saturday mornings.",
        "pattern_table": [
            {"metric": "total_observations", "value": "21", "support": "21 matching observations in the selected date range"},
            {"metric": "most_common_subject", "value": "hummingbird", "support": "hummingbird accounted for 12 of 21 observations"},
            {"metric": "most_active_source", "value": "camera_04", "support": "camera_04 recorded 14 of 21 observations"},
            {"metric": "most_active_time_window", "value": "6 AM - 8 AM", "support": "11 of 21 observations occurred in this window"},
            {"metric": "recurring_day", "value": "Saturday", "support": "Observed 4 of the last 5 Saturdays"},
        ],
        "computed_metrics": {
            "total_observations": 21,
            "average_confidence": 0.8957,
            "top_subjects": [
                {"subject_label": "hummingbird", "count": 12, "percentage": 57.1},
                {"subject_label": "cat", "count": 6, "percentage": 28.6},
                {"subject_label": "blue_jay", "count": 2, "percentage": 9.5},
                {"subject_label": "dog", "count": 1, "percentage": 4.8},
            ],
            "top_sources": [
                {"source_id": "camera_04", "count": 14, "percentage": 66.7},
                {"source_id": "camera_02", "count": 7, "percentage": 33.3},
            ],
            "top_day_of_week": {"day": "Saturday", "count": 12, "percentage": 57.1},
            "top_time_window": {"window": "6 AM - 8 AM", "count": 11, "percentage": 52.4},
        },
        "recommendations": [
            "Focus camera_04 on Saturdays between 6-8 AM to maximize capture of high-frequency subjects.",
            "Monitor hummingbird and cat activity for potential behavioral trends or changes.",
            "Consider expanding observation to other times or subjects to increase diversity of data.",
        ],
    },
    {
        "days_ago": 1,
        "subject_type": "animal",
        "subject_label": "hummingbird",
        "total_observations": 28,
        "computed_confidence": 0.97,
        "summary": "Over 28 observations, the most common subject was hummingbirds (57.1%), followed by cats (28.6%), with blue jays and dogs each at 7.1%. The average confidence is high (0.9007) and stable. The top source is camera_04, and the peak activity occurs on Saturdays between 6 AM and 8 AM. A recurring pattern is noted: observations occurred on 5 of the last 5 Saturdays.",
        "prediction": "Based on the strong recurring pattern and high prediction confidence (0.97), it is likely that hummingbird activity will continue to be observed on Saturdays during the early morning window, though occasional variations may occur.",
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
    },
]

_TRAFFIC_ANALYSES = [
    {
        "days_ago": 18,
        "subject_type": "vehicle",
        "subject_label": "sedan",
        "total_observations": 9,
        "computed_confidence": 0.14,
        "summary": "Based on 9 observations across 4 subjects, sedans are the most common subject (55.6%), followed by pedestrians (22.2%), SUVs (11.1%), and trucks (11.1%). The average confidence level is high (0.8989). Most observations originate from intersection_a on Wednesdays between 4 PM and 6 PM, but the recurring pattern is weak (observed only 1 out of the last 5 Wednesdays).",
        "prediction": "Given the low prediction confidence (0.14) and the weak recurring pattern, future occurrences are uncertain and unlikely to follow a strong weekly trend.",
        "pattern_table": [
            {"metric": "total_observations", "value": "9", "support": "9 matching observations in the selected date range"},
            {"metric": "most_common_subject", "value": "sedan", "support": "sedan accounted for 5 of 9 observations"},
            {"metric": "most_active_source", "value": "intersection_a", "support": "intersection_a recorded 9 of 9 observations"},
            {"metric": "most_active_time_window", "value": "4 PM - 6 PM", "support": "6 of 9 observations occurred in this window"},
            {"metric": "recurring_day", "value": "Wednesday", "support": "Observed 1 of the last 5 Wednesdays"},
        ],
        "computed_metrics": {
            "total_observations": 9,
            "average_confidence": 0.8989,
            "top_subjects": [
                {"subject_label": "sedan", "count": 5, "percentage": 55.6},
                {"subject_label": "pedestrian", "count": 2, "percentage": 22.2},
                {"subject_label": "suv", "count": 1, "percentage": 11.1},
                {"subject_label": "truck", "count": 1, "percentage": 11.1},
            ],
            "top_sources": [{"source_id": "intersection_a", "count": 9, "percentage": 100.0}],
            "top_day_of_week": {"day": "Wednesday", "count": 4, "percentage": 44.4},
            "top_time_window": {"window": "4 PM - 6 PM", "count": 6, "percentage": 66.7},
        },
        "recommendations": [
            "Increase monitoring on Wednesdays to gather more data on the pattern.",
            "Consider observing other time windows and days to identify additional patterns.",
            "Verify subject classification accuracy to maintain high confidence.",
        ],
    },
    {
        "days_ago": 12,
        "subject_type": "vehicle",
        "subject_label": "sedan",
        "total_observations": 16,
        "computed_confidence": 0.33,
        "summary": "Over 16 observations, sedans are the most frequent subject (56.2%), followed by pedestrians (25%), SUVs (12.5%), and trucks (6.2%). Average confidence is high (0.91) and stable. Most activity occurs at intersection_a on Wednesdays between 4-6 PM. A recurring pattern is observed on 2 of the last 5 Wednesdays.",
        "prediction": "There is a low confidence (0.33) suggestion that similar activity may recur on a future Wednesday, but the pattern is not strongly established yet.",
        "pattern_table": [
            {"metric": "total_observations", "value": "16", "support": "16 matching observations in the selected date range"},
            {"metric": "most_common_subject", "value": "sedan", "support": "sedan accounted for 9 of 16 observations"},
            {"metric": "most_active_source", "value": "intersection_a", "support": "intersection_a recorded 16 of 16 observations"},
            {"metric": "most_active_time_window", "value": "4 PM - 6 PM", "support": "11 of 16 observations occurred in this window"},
            {"metric": "recurring_day", "value": "Wednesday", "support": "Observed 2 of the last 5 Wednesdays"},
        ],
        "computed_metrics": {
            "total_observations": 16,
            "average_confidence": 0.9094,
            "top_subjects": [
                {"subject_label": "sedan", "count": 9, "percentage": 56.2},
                {"subject_label": "pedestrian", "count": 4, "percentage": 25.0},
                {"subject_label": "suv", "count": 2, "percentage": 12.5},
                {"subject_label": "truck", "count": 1, "percentage": 6.2},
            ],
            "top_sources": [{"source_id": "intersection_a", "count": 16, "percentage": 100.0}],
            "top_day_of_week": {"day": "Wednesday", "count": 7, "percentage": 43.8},
            "top_time_window": {"window": "4 PM - 6 PM", "count": 11, "percentage": 68.8},
        },
        "recommendations": [
            "Continue monitoring Wednesdays during the 4-6 PM window at intersection_a to gather more data.",
            "Investigate if the recurring pattern strengthens to better anticipate future occurrences.",
            "Consider whether the high proportion of sedans warrants tailored analysis or response.",
        ],
    },
    {
        "days_ago": 6,
        "subject_type": "vehicle",
        "subject_label": "sedan",
        "total_observations": 22,
        "computed_confidence": 0.54,
        "summary": "Out of 22 observations across 4 subject types, sedans dominated (59.1%), followed by pedestrians (22.7%), with SUVs and trucks each at 9.1%. Average confidence is high (0.90) and stable. Most observations came from intersection_a, primarily on Tuesdays between 4-6 PM, a pattern seen on 3 of the last 5 Tuesdays.",
        "prediction": "The pattern suggests similar activity is likely to recur on future Tuesdays during that window, but the low prediction confidence (0.54) indicates substantial uncertainty.",
        "pattern_table": [
            {"metric": "total_observations", "value": "22", "support": "22 matching observations in the selected date range"},
            {"metric": "most_common_subject", "value": "sedan", "support": "sedan accounted for 13 of 22 observations"},
            {"metric": "most_active_source", "value": "intersection_a", "support": "intersection_a recorded 22 of 22 observations"},
            {"metric": "most_active_time_window", "value": "4 PM - 6 PM", "support": "15 of 22 observations occurred in this window"},
            {"metric": "recurring_day", "value": "Tuesday", "support": "Observed 3 of the last 5 Tuesdays"},
        ],
        "computed_metrics": {
            "total_observations": 22,
            "average_confidence": 0.9027,
            "top_subjects": [
                {"subject_label": "sedan", "count": 13, "percentage": 59.1},
                {"subject_label": "pedestrian", "count": 5, "percentage": 22.7},
                {"subject_label": "suv", "count": 2, "percentage": 9.1},
                {"subject_label": "truck", "count": 2, "percentage": 9.1},
            ],
            "top_sources": [{"source_id": "intersection_a", "count": 22, "percentage": 100.0}],
            "top_day_of_week": {"day": "Tuesday", "count": 9, "percentage": 40.9},
            "top_time_window": {"window": "4 PM - 6 PM", "count": 15, "percentage": 68.2},
        },
        "recommendations": [
            "Increase monitoring at intersection_a during Tuesday 4-6 PM to gather more data and improve confidence.",
            "Consider enhancing pedestrian safety measures given the 22.7% pedestrian share.",
            "Investigate why sedans dominate and whether that influences traffic flow or safety.",
        ],
    },
    {
        "days_ago": 1,
        "subject_type": "vehicle",
        "subject_label": "sedan",
        "total_observations": 28,
        "computed_confidence": 0.78,
        "summary": "Over 28 observations, the most common subject is 'sedan' (60.7%), followed by 'pedestrian' (21.4%), 'SUV' (10.7%), and 'truck' (7.1%). The average confidence is high (0.9014) and stable. The primary source is intersection_a, with the most activity on Tuesdays between 4 PM and 6 PM. A recurring pattern shows observations on 4 of the last 5 Tuesdays.",
        "prediction": "Given the recurring pattern and high confidence, it is likely that similar observations will continue on future Tuesdays during the 4 PM - 6 PM window at intersection_a, with sedans being the predominant subject. However, this is not guaranteed and should be monitored.",
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
    },
]


def _seed_app(db: Session, user_id: uuid.UUID, name: str, analyses: list[dict]) -> None:
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

    now = datetime.now(timezone.utc)
    for entry in analyses:
        created_at = now - timedelta(days=entry["days_ago"], hours=entry["days_ago"] % 5)

        db.add(
            ObservationAnalysis(
                client_app_id=app.id,
                analysis_id=_generate_analysis_id(),
                subject_type=entry["subject_type"],
                subject_label=entry["subject_label"],
                total_observations=entry["total_observations"],
                computed_confidence=entry["computed_confidence"],
                summary=entry["summary"],
                prediction=entry["prediction"],
                pattern_table_json=entry["pattern_table"],
                computed_metrics_json=entry["computed_metrics"],
                recommendations_json=entry["recommendations"],
                warnings_json=["Predictions are pattern estimates based on historical observations, not guarantees."],
                created_at=created_at,
            )
        )

        db.add(
            ApiRequestLog(
                client_app_id=app.id,
                service_key="observations.analyze",
                endpoint="/v1/observations/analyze",
                method="POST",
                status_code=200,
                success=True,
                error_code=None,
                latency_ms=850 + (entry["days_ago"] * 13) % 400,
                request_id=uuid.uuid4().hex,
                created_at=created_at,
            )
        )


def seed_demo_data(db: Session, user_id: uuid.UUID) -> None:
    """Seeds a fresh demo account with two realistic apps, each with an
    enabled scope, an API key, and a real history of genuine (frozen)
    LLM-generated analyses - one ApiRequestLog row per ObservationAnalysis
    row, always, matching how the real endpoint actually behaves.

    Does not commit - the caller controls the transaction boundary."""
    _seed_app(db, user_id, "Wildlife Detection", _WILDLIFE_ANALYSES)
    _seed_app(db, user_id, "Traffic Cam Pilot", _TRAFFIC_ANALYSES)