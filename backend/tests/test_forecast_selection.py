import pytest

from app.analysis.forecast_selection import select_forecast_vintage


def test_selects_latest_forecast_available_at_cutoff():
    forecasts = [
        {
            "startTime": "2026-01-15T14:00:00Z",
            "publishTime": "2026-01-14T08:00:00Z",
            "generation": 18000,
        },
        {
            "startTime": "2026-01-15T14:00:00Z",
            "publishTime": "2026-01-14T11:30:00Z",
            "generation": 17500,
        },
        {
            "startTime": "2026-01-15T14:00:00Z",
            "publishTime": "2026-01-14T14:00:00Z",
            "generation": 16800,
        },
    ]

    result = select_forecast_vintage(
        forecasts,
        decision_time="2026-01-14T12:00:00Z",
        delivery_start="2026-01-15T00:00:00Z",
        delivery_end="2026-01-16T00:00:00Z",
    )

    assert len(result) == 1
    assert result.iloc[0]["forecast_mw"] == 17500
    assert result.iloc[0]["publish_time"].isoformat() == (
        "2026-01-14T11:30:00+00:00"
    )


def test_returns_empty_when_no_forecast_was_available():
    forecasts = [
        {
            "startTime": "2026-01-15T14:00:00Z",
            "publishTime": "2026-01-14T14:00:00Z",
            "generation": 16800,
        }
    ]

    result = select_forecast_vintage(
        forecasts,
        decision_time="2026-01-14T12:00:00Z",
        delivery_start="2026-01-15T00:00:00Z",
        delivery_end="2026-01-16T00:00:00Z",
    )

    assert result.empty


def test_rejects_timezone_naive_timestamps():
    with pytest.raises(ValueError):
        select_forecast_vintage(
            [],
            decision_time="2026-01-14T12:00:00",
            delivery_start="2026-01-15T00:00:00Z",
            delivery_end="2026-01-16T00:00:00Z",
        )
