from datetime import datetime, timedelta, timezone

import pandas as pd

from app.services.analytics.bucketing import add_local_time_columns, bucket_time_of_day
from app.services.analytics.confidence import compute_average_confidence, compute_confidence_trend
from app.services.analytics.observation_metrics import (
    compute_next_likely_window,
    compute_prediction_confidence,
    compute_top_day_of_week,
    compute_top_sources,
    compute_top_time_window,
    detect_recurring_day_pattern,
)


def observations_to_dataframe(observations: list) -> pd.DataFrame:
    """Flattens the nested request schema (each observation has a nested
    `source` object) into a flat DataFrame the rest of the engine works with.
    """
    rows = [
        {"observed_at": obs.observed_at, "source_id": obs.source.id, "confidence": obs.confidence}
        for obs in observations
    ]
    df = pd.DataFrame(rows)
    df["observed_at"] = pd.to_datetime(df["observed_at"], utc=True)
    return df


def filter_by_date_range(
    df: pd.DataFrame,
    date_from: datetime | None,
    date_to: datetime | None,
    lookback_days: int,
) -> pd.DataFrame:
    """date_from/date_to win if given. Otherwise falls back to the last
    `lookback_days` days from now.
    """
    if date_from is None and date_to is None:
        date_to = datetime.now(timezone.utc)
        date_from = date_to - timedelta(days=lookback_days)
    elif date_from is None:
        date_from = pd.Timestamp.min.tz_localize("UTC")
    elif date_to is None:
        date_to = datetime.now(timezone.utc)

    mask = (df["observed_at"] >= date_from) & (df["observed_at"] <= date_to)
    return df.loc[mask].copy()


def run_observation_analytics(
    observations: list,
    subject_label: str,
    timezone_name: str,
    date_from: datetime | None,
    date_to: datetime | None,
    lookback_days: int,
    time_bucket_hours: int,
) -> dict:
    """The single entry point: raw observations in, fully computed facts
    out. This owns the entire deterministic pipeline end to end - the API
    route only needs to call this one function.
    """
    df = observations_to_dataframe(observations)
    df = filter_by_date_range(df, date_from, date_to, lookback_days)

    if df.empty:
        return {"empty": True, "total_observations": 0}

    df = add_local_time_columns(df, timezone_name)
    df = bucket_time_of_day(df, time_bucket_hours)

    total_observations = len(df)
    average_confidence = compute_average_confidence(df)
    confidence_trend = compute_confidence_trend(df)
    top_sources = compute_top_sources(df)
    top_day = compute_top_day_of_week(df)
    top_time_window = compute_top_time_window(df)

    recurring_pattern = detect_recurring_day_pattern(df, top_day["day"]) if top_day else None
    recurring_hits = recurring_pattern["hits"] if recurring_pattern else 0
    recurring_total = recurring_pattern["total"] if recurring_pattern else 0
    prediction_confidence = compute_prediction_confidence(total_observations, recurring_hits, recurring_total)

    fallback_prediction = compute_next_likely_window(
        top_day["day"] if top_day else None,
        top_time_window["window"] if top_time_window else None,
    )

    pattern_table = [
        {
            "metric": "total_observations",
            "value": str(total_observations),
            "support": f"{total_observations} matching observations in the selected date range",
        }
    ]
    if top_sources:
        pattern_table.append({
            "metric": "most_active_source",
            "value": top_sources[0]["source_id"],
            "support": f"{top_sources[0]['source_id']} recorded {top_sources[0]['count']} of {total_observations} observations",
        })
    if top_time_window:
        pattern_table.append({
            "metric": "most_active_time_window",
            "value": top_time_window["window"],
            "support": f"{top_time_window['count']} of {total_observations} observations occurred in this window",
        })
    if recurring_pattern:
        pattern_table.append({
            "metric": "recurring_day",
            "value": top_day["day"],
            "support": recurring_pattern["support"],
        })

    evidence_packet = {
        "subject_label": subject_label,
        "total_observations": total_observations,
        "average_confidence": average_confidence,
        "confidence_trend": confidence_trend,
        "top_source": top_sources[0]["source_id"] if top_sources else None,
        "top_day": top_day["day"] if top_day else None,
        "top_time_window": top_time_window["window"] if top_time_window else None,
        "recurring_pattern": recurring_pattern["support"] if recurring_pattern else None,
        "prediction_confidence": prediction_confidence,
    }

    return {
        "empty": False,
        "total_observations": total_observations,
        "average_confidence": average_confidence,
        "confidence_trend": confidence_trend,
        "top_sources": top_sources,
        "top_day_of_week": top_day,
        "top_time_window": top_time_window,
        "recurring_pattern": recurring_pattern,
        "prediction_confidence": prediction_confidence,
        "pattern_table": pattern_table,
        "evidence_packet": evidence_packet,
        "fallback_summary": _build_fallback_summary(subject_label, top_day, top_time_window),
        "fallback_prediction": fallback_prediction,
    }


def _build_fallback_summary(subject_label: str, top_day: dict | None, top_time_window: dict | None) -> str:
    if top_day is None or top_time_window is None:
        return f"Not enough data yet to identify a clear pattern for {subject_label}."
    return (
        f"{subject_label} observations are concentrated around {top_time_window['window']}, "
        f"especially on {top_day['day']}."
    )