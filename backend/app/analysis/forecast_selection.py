import pandas as pd


def select_forecast_vintage(
    forecast_records: list[dict],
    decision_time: str,
    delivery_start: str,
    delivery_end: str,
) -> pd.DataFrame:
    """
    Select the latest forecast published by decision_time for each
    delivery timestamp in [delivery_start, delivery_end).

    All timestamps are normalized to UTC.
    """

    columns = ["start_time", "publish_time", "forecast_mw"]

    # Validate timestamps before returning for empty forecast data.
    cutoff = pd.Timestamp(decision_time)
    start = pd.Timestamp(delivery_start)
    end = pd.Timestamp(delivery_end)

    if cutoff.tzinfo is None or start.tzinfo is None or end.tzinfo is None:
        raise ValueError("All timestamps must include a timezone.")

    cutoff = cutoff.tz_convert("UTC")
    start = start.tz_convert("UTC")
    end = end.tz_convert("UTC")

    if end <= start:
        raise ValueError("delivery_end must be after delivery_start.")

    if not forecast_records:
        return pd.DataFrame(columns=columns)

    forecasts = pd.DataFrame(forecast_records)

    required = {"startTime", "publishTime", "generation"}
    if not required.issubset(forecasts.columns):
        raise ValueError("Forecast records are missing required fields.")

    forecasts = forecasts.rename(
        columns={
            "startTime": "start_time",
            "publishTime": "publish_time",
            "generation": "forecast_mw",
        }
    )

    forecasts["start_time"] = pd.to_datetime(
        forecasts["start_time"], utc=True, errors="coerce"
    )
    forecasts["publish_time"] = pd.to_datetime(
        forecasts["publish_time"], utc=True, errors="coerce"
    )
    forecasts["forecast_mw"] = pd.to_numeric(
        forecasts["forecast_mw"], errors="coerce"
    )

    forecasts = forecasts.dropna(
        subset=["start_time", "publish_time", "forecast_mw"]
    )

    # Keep only the delivery window and forecasts available at the cutoff.
    forecasts = forecasts[
        (forecasts["start_time"] >= start)
        & (forecasts["start_time"] < end)
        & (forecasts["publish_time"] <= cutoff)
    ]

    # The latest eligible publication wins for each delivery interval.
    forecasts = forecasts.sort_values(
        ["start_time", "publish_time"]
    )

    selected = forecasts.drop_duplicates(
        subset=["start_time"],
        keep="last",
    )

    return selected[columns].sort_values(
        "start_time"
    ).reset_index(drop=True)
