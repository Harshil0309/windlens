import pandas as pd
import pytest

from app.analysis.metrics import calculate_metrics


def test_calculate_metrics():
    actual = pd.Series([100.0, 200.0, 300.0])
    forecast = pd.Series([110.0, 180.0, 330.0])

    result = calculate_metrics(actual, forecast)

    assert result["sample_count"] == 3
    assert result["mae_mw"] == pytest.approx(20.0)
    assert result["rmse_mw"] == pytest.approx(21.60, abs=0.01)
    assert result["bias_mw"] == pytest.approx(6.67, abs=0.01)


def test_calculate_metrics_rejects_empty_data():
    with pytest.raises(ValueError):
        calculate_metrics(pd.Series(dtype=float), pd.Series(dtype=float))
