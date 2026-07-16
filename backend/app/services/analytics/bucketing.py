import pandas as pd


def add_local_time_columns(df: pd.DataFrame, timezone: str) -> pd.DataFrame:
    """Convert UTC observed_at timestamps into the caller's local timezone,
    then derive day_of_week and hour from that local time. Pattern
    detection should reason in local time, not UTC - "noon" should mean
    noon where the camera actually is, not noon UTC.
    """
    df = df.copy()
    local_time = df["observed_at"].dt.tz_convert(timezone)
    df["local_time"] = local_time
    df["day_of_week"] = local_time.dt.day_name()
    df["hour"] = local_time.dt.hour
    return df


def bucket_time_of_day(df: pd.DataFrame, bucket_hours: int) -> pd.DataFrame:
    """Assign each observation to a time-of-day bucket. With
    bucket_hours=2: 12 AM-2 AM, 2 AM-4 AM, ... 10 PM-12 AM.
    """
    df = df.copy()
    bucket_index = (df["hour"] // bucket_hours).astype(int)
    df["time_bucket"] = bucket_index.apply(lambda i: _format_bucket_label(i, bucket_hours))
    return df


def _format_bucket_label(bucket_index: int, bucket_hours: int) -> str:
    start_hour = bucket_index * bucket_hours
    end_hour = (start_hour + bucket_hours) % 24
    return f"{_format_hour(start_hour)} - {_format_hour(end_hour)}"


def _format_hour(hour: int) -> str:
    period = "AM" if hour < 12 else "PM"
    display_hour = hour % 12
    if display_hour == 0:
        display_hour = 12
    return f"{display_hour} {period}"