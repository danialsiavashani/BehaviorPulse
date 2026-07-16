from datetime import datetime, timezone

from app.schemas.observation import ObservationIn, SourceIn
from app.services.analytics.engine import run_observation_analytics


def _build_test_observations() -> list[ObservationIn]:
    # Last 5 Wednesdays ending 2026-07-15: Jun 17, 24, Jul 1, 8, 15.
    # Sightings at noon Pacific (=19:00 UTC in PDT) on 4 of the 5 - skip
    # Jun 17 to simulate a realistic "4 of last 5" pattern.
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

    noise = [
        ("2026-06-20T08:00:00Z", "camera_09", 0.6),
        ("2026-06-22T22:00:00Z", "camera_09", 0.55),
        ("2026-06-28T06:00:00Z", "camera_09", 0.7),
        ("2026-07-05T23:00:00Z", "camera_04", 0.65),
        ("2026-07-10T02:00:00Z", "camera_09", 0.5),
    ]
    for ts, cam, conf in noise:
        observations.append(ObservationIn(
            observed_at=ts,
            source=SourceIn(type="camera", id=cam),
            confidence=conf,
        ))
    return observations


def _run_test_analysis():
    return run_observation_analytics(
        observations=_build_test_observations(),
        subject_label="hummingbird",
        timezone_name="America/Los_Angeles",
        date_from=datetime(2026, 6, 1, tzinfo=timezone.utc),
        date_to=datetime(2026, 7, 15, 23, 59, 59, tzinfo=timezone.utc),
        lookback_days=30,
        time_bucket_hours=2,
    )


def test_total_observation_count():
    result = _run_test_analysis()
    assert result["total_observations"] == 9


def test_top_source_is_camera_04():
    result = _run_test_analysis()
    assert result["top_sources"][0]["source_id"] == "camera_04"
    assert result["top_sources"][0]["count"] == 5


def test_top_day_is_wednesday():
    result = _run_test_analysis()
    assert result["top_day_of_week"]["day"] == "Wednesday"


def test_timezone_conversion_buckets_noon_correctly():
    # 19:00 UTC in summer (PDT, UTC-7) is noon Pacific - this proves the
    # engine converts timezone before bucketing, not after.
    result = _run_test_analysis()
    assert result["top_time_window"]["window"] == "12 PM - 2 PM"


def test_recurring_wednesday_pattern_detected():
    result = _run_test_analysis()
    pattern = result["recurring_pattern"]
    assert pattern["hits"] == 4
    assert pattern["total"] == 5
    assert pattern["support"] == "Observed 4 of the last 5 Wednesdays"


def test_empty_observations_after_date_filter():
    observations = _build_test_observations()
    result = run_observation_analytics(
        observations=observations,
        subject_label="hummingbird",
        timezone_name="America/Los_Angeles",
        date_from=datetime(2020, 1, 1, tzinfo=timezone.utc),
        date_to=datetime(2020, 1, 31, tzinfo=timezone.utc),
        lookback_days=30,
        time_bucket_hours=2,
    )
    assert result["empty"] is True
    assert result["total_observations"] == 0