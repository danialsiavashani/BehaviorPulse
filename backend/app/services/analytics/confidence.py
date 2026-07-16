import pandas as pd


def compute_average_confidence(df: pd.DataFrame) -> float:
    return round(float(df["confidence"].mean()), 4)


def compute_confidence_trend(df: pd.DataFrame, min_observations: int = 10) -> str | None:
    """Compares average confidence in the first half of the date range vs
    the second half. Returns "increasing", "decreasing", "stable", or None
    if there isn't enough data to say anything meaningful.
    """
    if len(df) < min_observations:
        return None

    sorted_df = df.sort_values("observed_at")
    midpoint = len(sorted_df) // 2
    first_half_avg = sorted_df.iloc[:midpoint]["confidence"].mean()
    second_half_avg = sorted_df.iloc[midpoint:]["confidence"].mean()

    difference = second_half_avg - first_half_avg
    if abs(difference) < 0.03:
        return "stable"
    return "increasing" if difference > 0 else "decreasing"