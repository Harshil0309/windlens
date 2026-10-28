from app.analysis.alignment import build_comparison


def test_alignment_aggregates_half_hourly_actuals():
    actual = [
        {"startTime": "2026-01-01T00:00:00Z", "generation": 100},
        {"startTime": "2026-01-01T00:30:00Z", "generation": 110},
        {"startTime": "2026-01-01T01:00:00Z", "generation": 120},
        {"startTime": "2026-01-01T01:30:00Z", "generation": 140},
    ]

    forecast = [
        {"startTime": "2026-01-01T00:00:00Z", "generation": 120},
        {"startTime": "2026-01-01T01:00:00Z", "generation": 130},
    ]

    result = build_comparison(actual, forecast)

    assert len(result) == 2

    # First hourly actual = (100 + 110) / 2 = 105 MW.
    assert result.iloc[0]["actual_mw"] == 105
    assert result.iloc[0]["forecast_mw"] == 120
    assert result.iloc[0]["error_mw"] == 15

    # Second hourly actual = (120 + 140) / 2 = 130 MW.
    assert result.iloc[1]["actual_mw"] == 130
    assert result.iloc[1]["forecast_mw"] == 130
    assert result.iloc[1]["error_mw"] == 0


def test_alignment_excludes_incomplete_hours():
    actual = [
        {"startTime": "2026-01-01T00:00:00Z", "generation": 100},
    ]

    forecast = [
        {"startTime": "2026-01-01T00:00:00Z", "generation": 120},
    ]

    result = build_comparison(actual, forecast)

    assert result.empty
