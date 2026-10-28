import numpy as np
import pandas as pd


def calculate_metrics(
    actual: pd.Series,
    forecast: pd.Series,
) -> dict:
    """Calculate accuracy metrics for aligned actual and forecast values."""

    paired = pd.concat(
        [
            actual.rename("actual"),
            forecast.rename("forecast"),
        ],
        axis=1,
    ).dropna()

    if paired.empty:
        raise ValueError("No valid actual/forecast pairs are available.")

    errors = paired["forecast"] - paired["actual"]

    mae = float(np.mean(np.abs(errors)))
    rmse = float(np.sqrt(np.mean(np.square(errors))))
    bias = float(np.mean(errors))

    actual_total = float(paired["actual"].abs().sum())
    wape = (
        float(np.abs(errors).sum() / actual_total * 100)
        if actual_total > 0
        else None
    )

    return {
        "sample_count": int(len(paired)),
        "mae_mw": round(mae, 2),
        "rmse_mw": round(rmse, 2),
        "bias_mw": round(bias, 2),
        "wape_percent": round(wape, 2) if wape is not None else None,
    }
