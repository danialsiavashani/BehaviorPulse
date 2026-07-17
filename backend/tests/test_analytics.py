from datetime import datetime, timezone

from app.schemas.observation import ObservationIn, SourceIn, SubjectIn
from app.services.analytics.engine import run_observation_analytics


def _build_test_observations() -> list[ObservationIn]:
    wednesday_noon_utc = [
        "2026-06-24T19:00:00Z",
        "2026-07-01T19:05:00Z",
        "2026-07-08T18:55:00Z",
        "2026-07-15T19:10:00Z",
    ]
    observations = [
        ObservationIn(
            observed_at=ts,
            subject=SubjectIn(type="animal", label="hummingbird"),
            source=SourceIn(type="camera", id="camera_04"),
            confidence=0.85,
        )
        for ts in wednesday_noon_utc
    ]

    noise = [
        ("2026-06-20T08:00:00Z", "camera_09", 0.6, "squirrel"),
        ("2026-06-22T22:00:00Z", "camera_09", 0.55, "squirrel"),
        ("2026-06-28T06:00:00Z", "camera_09", 0.7, "blue_jay"),
        ("2026-07-05T23:00:00Z", "camera_04", 0.65, "hummingbird"),
        ("2026-07-10T02:00:00Z", "camera_09", 0.5, "squirrel"),
    ]
    for ts, cam, conf, label in noise:
        observations.append(ObservationIn(
            observed_at=ts,
            subject=SubjectIn(type="animal", label=label),
            source=SourceIn(type="camera", id=cam),
            confidence=conf,
        ))
    return observations


def _run_test_analysis():
    return run_observation_analytics(
        observations=_build_test_observations(),
        timezone_name="America/Los_Angeles",
        date_from=datetime(2026, 6, 1, tzinfo=timezone.utc),
        date_to=datetime(2026, 7, 15, 23, 59, 59, tzinfo=timezone.utc),
        lookback_days=30,
        time_bucket_hours=2,
    )


def test_total_observation_count():
    result = _run_test_analysis()
    assert result["total_observations"] == 9


def test_top_subject_is_hummingbird():
    result = _run_test_analysis()
    assert result["top_subjects"][0]["subject_label"] == "hummingbird"
    assert result["top_subjects"][0]["count"] == 5


def test_multiple_subjects_all_captured():
    result = _run_test_analysis()
    labels = {s["subject_label"] for s in result["top_subjects"]}
    assert labels == {"hummingbird", "squirrel", "blue_jay"}


def test_top_source_is_camera_04():
    result = _run_test_analysis()
    assert result["top_sources"][0]["source_id"] == "camera_04"
    assert result["top_sources"][0]["count"] == 5


def test_top_day_is_wednesday():
    result = _run_test_analysis()
    assert result["top_day_of_week"]["day"] == "Wednesday"


def test_timezone_conversion_buckets_noon_correctly():
    result = _run_test_analysis()
    assert result["top_time_window"]["window"] == "12 PM - 2 PM"


def test_recurring_wednesday_pattern_detected():
    result = _run_test_analysis()
    pattern = result["recurring_pattern"]
    assert pattern["hits"] == 4
    assert pattern["total"] == 5
    assert pattern["support"] == "Observed 4 of the last 5 Wednesdays"


def test_empty_observations_after_date_filter():
    result = run_observation_analytics(
        observations=_build_test_observations(),
        timezone_name="America/Los_Angeles",
        date_from=datetime(2020, 1, 1, tzinfo=timezone.utc),
        date_to=datetime(2020, 1, 31, tzinfo=timezone.utc),
        lookback_days=30,
        time_bucket_hours=2,
    )
    assert result["empty"] is True
    assert result["total_observations"] == 0