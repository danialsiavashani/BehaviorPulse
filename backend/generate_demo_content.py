"""
One-off script - NOT part of the deployed app, don't commit this into
app/. Run once from backend/ (with .venv active) to generate real,
distinct LLM-written analyses for the demo seed data, sliced across a
few progressively larger date windows so each one is genuinely different
(more data, stronger pattern, higher confidence) rather than repeats.

Usage (from backend/):
    python generate_demo_content.py
"""
import json
from datetime import datetime

from app.schemas.observation import ObservationIn, SourceIn, SubjectIn
from app.services.analytics.engine import run_observation_analytics
from app.services.llm.factory import get_llm_client


def obs(observed_at, subject_type, subject_label, source_type, source_id, confidence, metadata=None):
    return ObservationIn(
        observed_at=datetime.fromisoformat(observed_at.replace("Z", "+00:00")),
        subject=SubjectIn(type=subject_type, label=subject_label),
        source=SourceIn(type=source_type, id=source_id),
        confidence=confidence,
        metadata=metadata or {},
    )


WILDLIFE_OBSERVATIONS = [
    obs("2026-06-06T13:15:00Z", "animal", "hummingbird", "camera", "camera_04", 0.91, {"location": "feeder"}),
    obs("2026-06-06T13:42:00Z", "animal", "hummingbird", "camera", "camera_04", 0.88, {"location": "feeder"}),
    obs("2026-06-06T14:05:00Z", "animal", "blue_jay", "camera", "camera_04", 0.85, {"location": "feeder"}),
    obs("2026-06-09T01:10:00Z", "animal", "cat", "camera", "camera_02", 0.95, {"location": "north_fence"}),
    obs("2026-06-11T01:25:00Z", "animal", "cat", "camera", "camera_02", 0.93, {"location": "north_fence"}),
    obs("2026-06-13T13:05:00Z", "animal", "hummingbird", "camera", "camera_04", 0.89, {"location": "feeder"}),
    obs("2026-06-13T13:30:00Z", "animal", "hummingbird", "camera", "camera_04", 0.93, {"location": "feeder"}),
    obs("2026-06-13T14:20:00Z", "animal", "hummingbird", "camera", "camera_04", 0.87, {"location": "feeder"}),
    obs("2026-06-16T01:15:00Z", "animal", "cat", "camera", "camera_02", 0.94, {"location": "north_fence"}),
    obs("2026-06-18T01:20:00Z", "animal", "cat", "camera", "camera_02", 0.92, {"location": "north_fence"}),
    obs("2026-06-20T13:10:00Z", "animal", "hummingbird", "camera", "camera_04", 0.88, {"location": "feeder"}),
    obs("2026-06-20T13:50:00Z", "animal", "hummingbird", "camera", "camera_04", 0.90, {"location": "feeder"}),
    obs("2026-06-20T14:00:00Z", "animal", "blue_jay", "camera", "camera_04", 0.86, {"location": "feeder"}),
    obs("2026-06-23T01:05:00Z", "animal", "cat", "camera", "camera_02", 0.96, {"location": "north_fence"}),
    obs("2026-06-25T01:30:00Z", "animal", "cat", "camera", "camera_02", 0.91, {"location": "north_fence"}),
    obs("2026-06-27T13:20:00Z", "animal", "hummingbird", "camera", "camera_04", 0.90, {"location": "feeder"}),
    obs("2026-06-27T13:45:00Z", "animal", "hummingbird", "camera", "camera_04", 0.87, {"location": "feeder"}),
    obs("2026-06-27T15:30:00Z", "animal", "dog", "camera", "camera_02", 0.97, {"location": "north_fence"}),
    obs("2026-06-30T01:10:00Z", "animal", "cat", "camera", "camera_02", 0.93, {"location": "north_fence"}),
    obs("2026-07-02T01:15:00Z", "animal", "cat", "camera", "camera_02", 0.95, {"location": "north_fence"}),
    obs("2026-07-04T13:12:00Z", "animal", "hummingbird", "camera", "camera_04", 0.92, {"location": "feeder"}),
    obs("2026-07-04T13:35:00Z", "animal", "hummingbird", "camera", "camera_04", 0.89, {"location": "feeder"}),
    obs("2026-07-04T14:10:00Z", "animal", "hummingbird", "camera", "camera_04", 0.91, {"location": "feeder"}),
    obs("2026-07-04T15:30:00Z", "animal", "dog", "camera", "camera_02", 0.96, {"location": "north_fence"}),
    obs("2026-06-10T18:45:00Z", "animal", "hummingbird", "camera", "camera_04", 0.82, {"location": "feeder"}),
    obs("2026-06-17T19:05:00Z", "animal", "hummingbird", "camera", "camera_04", 0.84, {"location": "feeder"}),
    obs("2026-06-24T18:50:00Z", "animal", "hummingbird", "camera", "camera_04", 0.83, {"location": "feeder"}),
    obs("2026-07-01T19:00:00Z", "animal", "hummingbird", "camera", "camera_04", 0.85, {"location": "feeder"}),
]

TRAFFIC_OBSERVATIONS = [
    obs("2026-07-01T00:15:00Z", "vehicle", "sedan", "camera", "intersection_a", 0.94, {"lane": "southbound"}),
    obs("2026-07-01T00:35:00Z", "vehicle", "sedan", "camera", "intersection_a", 0.91, {"lane": "southbound"}),
    obs("2026-07-01T00:50:00Z", "vehicle", "suv", "camera", "intersection_a", 0.87, {"lane": "southbound"}),
    obs("2026-07-01T19:10:00Z", "pedestrian", "pedestrian", "camera", "intersection_a", 0.96, {"crosswalk": "main_st"}),
    obs("2026-07-02T00:20:00Z", "vehicle", "sedan", "camera", "intersection_a", 0.93, {"lane": "southbound"}),
    obs("2026-07-02T00:40:00Z", "vehicle", "sedan", "camera", "intersection_a", 0.90, {"lane": "southbound"}),
    obs("2026-07-02T00:55:00Z", "vehicle", "truck", "camera", "intersection_a", 0.85, {"lane": "southbound"}),
    obs("2026-07-02T19:05:00Z", "pedestrian", "pedestrian", "camera", "intersection_a", 0.95, {"crosswalk": "main_st"}),
    obs("2026-07-08T00:10:00Z", "vehicle", "sedan", "camera", "intersection_a", 0.92, {"lane": "southbound"}),
    obs("2026-07-08T00:30:00Z", "vehicle", "sedan", "camera", "intersection_a", 0.95, {"lane": "southbound"}),
    obs("2026-07-08T00:45:00Z", "vehicle", "sedan", "camera", "intersection_a", 0.89, {"lane": "southbound"}),
    obs("2026-07-08T19:15:00Z", "pedestrian", "pedestrian", "camera", "intersection_a", 0.97, {"crosswalk": "main_st"}),
    obs("2026-07-09T00:25:00Z", "vehicle", "sedan", "camera", "intersection_a", 0.91, {"lane": "southbound"}),
    obs("2026-07-09T00:50:00Z", "vehicle", "suv", "camera", "intersection_a", 0.88, {"lane": "southbound"}),
    obs("2026-07-09T19:00:00Z", "pedestrian", "pedestrian", "camera", "intersection_a", 0.94, {"crosswalk": "main_st"}),
    obs("2026-07-15T00:15:00Z", "vehicle", "sedan", "camera", "intersection_a", 0.93, {"lane": "southbound"}),
    obs("2026-07-15T00:35:00Z", "vehicle", "sedan", "camera", "intersection_a", 0.90, {"lane": "southbound"}),
    obs("2026-07-15T00:50:00Z", "vehicle", "truck", "camera", "intersection_a", 0.84, {"lane": "southbound"}),
    obs("2026-07-16T00:20:00Z", "vehicle", "sedan", "camera", "intersection_a", 0.92, {"lane": "southbound"}),
    obs("2026-07-16T19:10:00Z", "pedestrian", "pedestrian", "camera", "intersection_a", 0.96, {"crosswalk": "main_st"}),
    obs("2026-07-22T00:10:00Z", "vehicle", "sedan", "camera", "intersection_a", 0.94, {"lane": "southbound"}),
    obs("2026-07-22T00:30:00Z", "vehicle", "sedan", "camera", "intersection_a", 0.91, {"lane": "southbound"}),
    obs("2026-07-22T00:45:00Z", "vehicle", "suv", "camera", "intersection_a", 0.86, {"lane": "southbound"}),
    obs("2026-07-23T00:15:00Z", "vehicle", "sedan", "camera", "intersection_a", 0.93, {"lane": "southbound"}),
    obs("2026-07-23T19:05:00Z", "pedestrian", "pedestrian", "camera", "intersection_a", 0.95, {"crosswalk": "main_st"}),
    obs("2026-07-04T16:20:00Z", "vehicle", "sedan", "camera", "intersection_a", 0.78, {"lane": "southbound"}),
    obs("2026-07-11T16:35:00Z", "vehicle", "sedan", "camera", "intersection_a", 0.76, {"lane": "southbound"}),
    obs("2026-07-18T16:15:00Z", "vehicle", "sedan", "camera", "intersection_a", 0.79, {"lane": "southbound"}),
]

# date_from is fixed per dataset; only date_to grows each window - a
# realistic "re-ran analysis weekly as more data came in" narrative.
# Window 5/full for each dataset is skipped here since we already have
# that real output frozen from earlier.
WILDLIFE_WINDOWS = ["2026-06-08", "2026-06-15", "2026-06-22", "2026-06-29"]
TRAFFIC_WINDOWS = ["2026-07-05", "2026-07-10", "2026-07-17", "2026-07-24"]


def generate(observations, date_from_str, windows, timezone_name):
    llm_client = get_llm_client()
    for date_to_str in windows:
        date_from = datetime.fromisoformat(date_from_str + "T00:00:00+00:00")
        date_to = datetime.fromisoformat(date_to_str + "T23:59:59+00:00")

        result = run_observation_analytics(
            observations=observations,
            timezone_name=timezone_name,
            date_from=date_from,
            date_to=date_to,
            lookback_days=30,
            time_bucket_hours=2,
        )

        if result["empty"] or result["total_observations"] < 3:
            print(f"\n=== window ending {date_to_str}: too little data, skipping ===")
            continue

        llm_result = llm_client.summarize_observation_analysis(result["evidence_packet"])

        top_subject_label = result["top_subjects"][0]["subject_label"] if result["top_subjects"] else "unknown"
        matching = next((o for o in observations if o.subject.label == top_subject_label), None)
        subject_type = matching.subject.type if matching else "unknown"

        output = {
            "window_ending": date_to_str,
            "subject_type": subject_type,
            "subject_label": top_subject_label,
            "total_observations": result["total_observations"],
            "computed_confidence": result["prediction_confidence"],
            "summary": llm_result["summary"],
            "prediction": llm_result["prediction"],
            "pattern_table": result["pattern_table"],
            "computed_metrics": {
                "total_observations": result["total_observations"],
                "average_confidence": result["average_confidence"],
                "top_subjects": result["top_subjects"],
                "top_sources": result["top_sources"],
                "top_day_of_week": result["top_day_of_week"],
                "top_time_window": result["top_time_window"],
            },
            "recommendations": llm_result["recommendations"],
            "warnings": ["Predictions are pattern estimates based on historical observations, not guarantees."],
        }
        print(f"\n=== window ending {date_to_str} ===")
        print(json.dumps(output, indent=2, default=str))


if __name__ == "__main__":
    print("########## WILDLIFE ##########")
    generate(WILDLIFE_OBSERVATIONS, "2026-06-01", WILDLIFE_WINDOWS, "America/Los_Angeles")

    print("\n\n########## TRAFFIC ##########")
    generate(TRAFFIC_OBSERVATIONS, "2026-07-01", TRAFFIC_WINDOWS, "America/Los_Angeles")