import pandas as pd


def compute_top_sources(df: pd.DataFrame, limit: int = 5) -> list[dict]:
    total = len(df)
    counts = df["source_id"].value_counts().head(limit)
    return [
        {
            "source_id": source_id,
            "count": int(count),
            "percentage": round(count / total * 100, 1),
        }
        for source_id, count in counts.items()
    ]

def compute_top_subjects(df: pd.DataFrame, limit: int = 10) -> list[dict]:
    total = len(df)
    counts = df["subject_label"].value_counts().head(limit)
    return [
        {
            "subject_label": subject_label,
            "count": int(count),
            "percentage": round(count / total * 100, 1),
        }
        for subject_label, count in counts.items()
    ]

def compute_day_of_week_distribution(df: pd.DataFrame) -> dict[str, int]:
    return df["day_of_week"].value_counts().to_dict()


def compute_top_day_of_week(df: pd.DataFrame) -> dict | None:
    if df.empty:
        return None
    total = len(df)
    counts = df["day_of_week"].value_counts()
    top_day = counts.index[0]
    top_count = int(counts.iloc[0])
    return {
        "day": top_day,
        "count": top_count,
        "percentage": round(top_count / total * 100, 1),
    }


def compute_time_bucket_distribution(df: pd.DataFrame) -> dict[str, int]:
    return df["time_bucket"].value_counts().to_dict()


def compute_top_time_window(df: pd.DataFrame) -> dict | None:
    if df.empty:
        return None
    total = len(df)
    counts = df["time_bucket"].value_counts()
    top_window = counts.index[0]
    top_count = int(counts.iloc[0])
    return {
        "window": top_window,
        "count": top_count,
        "percentage": round(top_count / total * 100, 1),
    }


def detect_recurring_day_pattern(df: pd.DataFrame, day_name: str, window: int = 5) -> dict | None:
    """Checks how many of the last `window` occurrences of day_name (e.g.
    the last 5 Wednesdays, spaced exactly 7 days apart, ending at the most
    recent observation date) actually had at least one observation.
    Returns None if there's no data to anchor the check against.
    """
    if df.empty:
        return None

    max_date = df["local_time"].dt.date.max()
    day_abbrev = day_name[:3].upper()
    candidate_dates = pd.date_range(end=max_date, periods=window, freq=f"W-{day_abbrev}")

    observed_dates = set(df[df["day_of_week"] == day_name]["local_time"].dt.date)
    hits = sum(1 for d in candidate_dates if d.date() in observed_dates)
    total = len(candidate_dates)

    return {
        "hits": hits,
        "total": total,
        "support": f"Observed {hits} of the last {total} {day_name}s",
    }


def compute_next_likely_window(top_day: str | None, top_time_window: str | None) -> str:
    if top_day is None or top_time_window is None:
        return "Not enough data yet to predict a likely next observation window."
    return f"The next likely observation window is {top_day} around {top_time_window}."


def compute_prediction_confidence(
    total_observations: int,
    recurring_hits: int,
    recurring_total: int,
) -> float:
    """A simple, transparent (not ML-based) confidence score: how strong
    the recurring pattern is, scaled down a bit if the sample size is thin.
    Deliberately simple - this is a computed fact the LLM will describe,
    not something the LLM should be trusted to estimate itself.
    """
    if recurring_total == 0:
        return 0.0

    pattern_strength = recurring_hits / recurring_total
    sample_size_factor = min(total_observations / 30, 1.0)
    confidence = pattern_strength * (0.6 + 0.4 * sample_size_factor)
    confidence = min(confidence, 0.99)  # never claim absolute certainty
    return round(confidence, 2)