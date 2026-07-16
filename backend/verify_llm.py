import json

from app.services.analytics.engine import run_observation_analytics
from app.schemas.observation import ObservationIn, SourceIn
from app.services.llm.factory import get_llm_client
from datetime import datetime, timezone

# Reuse the same hummingbird dataset from the analytics engine test.
wednesday_noon_utc = [
    "2026-06-24T19:00:00Z",
    "2026-07-01T19:05:00Z",
    "2026-07-08T18:55:00Z",
    "2026-07-15T19:10:00Z",
]
observations = [
    ObservationIn(
        observed_at=ts,
        source=SourceIn(type="camera", id="camera_04"),
        confidence=0.85,
    )
    for ts in wednesday_noon_utc
]

result = run_observation_analytics(
    observations=observations,
    subject_label="hummingbird",
    timezone_name="America/Los_Angeles",
    date_from=datetime(2026, 6, 1, tzinfo=timezone.utc),
    date_to=datetime(2026, 7, 15, 23, 59, 59, tzinfo=timezone.utc),
    lookback_days=30,
    time_bucket_hours=2,
)

print("Evidence packet sent to the LLM:")
print(json.dumps(result["evidence_packet"], indent=2))
print()

llm_client = get_llm_client()
print(f"Using: {type(llm_client).__name__}")
print()

llm_result = llm_client.summarize_observation_analysis(result["evidence_packet"])
print("LLM response:")
print(json.dumps(llm_result, indent=2))