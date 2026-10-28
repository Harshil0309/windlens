import pandas as pd


COMPARISON_COLUMNS = [
    "start_time",
    "actual_mw",
    "forecast_mw",
    "error_mw",
]


def build_comparison(
    actual_records: list[dict],
    forecast_records: list[dict],
) -> pd.DataFrame:
    """
    Compare hourly forecasts against hourly average actual generation.

    Each hourly actual requires both half-hourly observations.
    Forecast timestamps represent the start of the delivery hour.
    """

    if not actual_records or not forecast_records:
        return pd.DataFrame(columns=COMPARISON_COLUMNS)

    actual = pd.DataFrame(actual_records)
    forecast = pd.DataFrame(forecast_records)

    actual = actual[["startTime", "generation"]].rename(
        columns={
            "startTime": "start_time",
            "generation": "actual_mw",
        }
    )

    forecast = forecast[["startTime", "generation"]].rename(
        columns={
            "startTime": "start_time",
            "generation": "forecast_mw",
        }
    )

    for frame, value_column in [
        (actual, "actual_mw"),
        (forecast, "forecast_mw"),
    ]:
        frame["start_time"] = pd.to_datetime(
            frame["start_time"], utc=True, errors="coerce"
        )
        frame[value_column] = pd.to_numeric(
            frame[value_column], errors="coerce"
        )
        frame.dropna(
            subset=["start_time", value_column],
            inplace=True,
        )

    actual = actual.drop_duplicates("start_time", keep="last")
    forecast = forecast.drop_duplicates("start_time", keep="last")

    # Aggregate half-hourly actuals into hourly average generation.
    actual["hour"] = actual["start_time"].dt.floor("h")

    hourly_actual = (
        actual.groupby("hour")
        .agg(
            actual_mw=("actual_mw", "mean"),
            observation_count=("actual_mw", "count"),
        )
        .reset_index()
        .rename(columns={"hour": "start_time"})
    )

    # Exclude incomplete hours rather than comparing partial averages.
    hourly_actual = hourly_actual[
        hourly_actual["observation_count"] == 2
    ].drop(columns=["observation_count"])

    comparison = hourly_actual.merge(
        forecast,
        on="start_time",
        how="inner",
        validate="one_to_one",
    )

    comparison["error_mw"] = (
        comparison["forecast_mw"] - comparison["actual_mw"]
    )

    return (
        comparison[COMPARISON_COLUMNS]
        .sort_values("start_time")
        .reset_index(drop=True)
    )
