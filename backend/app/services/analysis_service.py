from datetime import date, datetime, time, timedelta, timezone

import pandas as pd

from app.analysis.alignment import build_comparison
from app.analysis.forecast_selection import select_forecast_vintage
from app.analysis.metrics import calculate_metrics
from app.services.elexon_client import ElexonClient


class AnalysisService:
    """Coordinates Elexon data retrieval and forecast analysis."""

    def __init__(self, client: ElexonClient | None = None):
        self.client = client or ElexonClient()

    async def analyze_delivery_day(
        self,
        delivery_date: date,
        decision_time: datetime,
    ) -> dict:
        if decision_time.tzinfo is None:
            raise ValueError("decision_time must include a timezone.")

        cutoff = decision_time.astimezone(timezone.utc)

        delivery_start = datetime.combine(
            delivery_date, time.min, tzinfo=timezone.utc
        )
        delivery_end = delivery_start + timedelta(days=1)

        if cutoff >= delivery_end:
            # A decision cutoff after delivery has ended would permit
            # forecasts published after the delivery period began.
            # Keep this check conservative and require a pre-delivery cutoff.
            raise ValueError("decision_time must be before the delivery day ends.")

        # Retrieve a history window broad enough to capture forecasts
        # published before the delivery date. This is a pilot assumption;
        # we will verify the archive coverage and cutoff convention.
        publish_from = delivery_start - timedelta(days=3)

        actual_records = await self.client.get_actual_wind(
            delivery_date,
            delivery_date,
        )

        forecast_records = await self.client.get_forecasts(
            publish_from,
            cutoff,
        )

        selected = select_forecast_vintage(
            forecast_records=forecast_records,
            decision_time=cutoff.isoformat(),
            delivery_start=delivery_start.isoformat(),
            delivery_end=delivery_end.isoformat(),
        )

        actuals = [
            record
            for record in actual_records
            if delivery_start.isoformat().replace("+00:00", "Z")
            <= record["startTime"]
            < delivery_end.isoformat().replace("+00:00", "Z")
        ]

        selected_records = [
            {
                "startTime": row["start_time"].isoformat(),
                "generation": row["forecast_mw"],
                "publishTime": row["publish_time"].isoformat(),
            }
            for _, row in selected.iterrows()
        ]

        comparison = build_comparison(actuals, selected_records)

        if comparison.empty:
            metrics = {
                "sample_count": 0,
                "mae_mw": None,
                "rmse_mw": None,
                "bias_mw": None,
                "wape_percent": None,
            }
        else:
            metrics = calculate_metrics(
                comparison["actual_mw"],
                comparison["forecast_mw"],
            )

        comparison_records = comparison.copy()
        if not comparison_records.empty:
            comparison_records["start_time"] = (
                comparison_records["start_time"].dt.strftime(
                    "%Y-%m-%dT%H:%M:%SZ"
                )
            )

        # Return selected forecasts separately, including intervals
        # without matching actuals, so missing comparisons remain visible.
        forecast_output = [
            {
                "start_time": row["start_time"].isoformat(),
                "publish_time": row["publish_time"].isoformat(),
                "forecast_mw": float(row["forecast_mw"]),
            }
            for _, row in selected.iterrows()
        ]

        actual_output = [
            {
                "start_time": record["startTime"],
                "actual_mw": record["generation"],
            }
            for record in actuals
        ]

        return {
            "delivery_date": delivery_date.isoformat(),
            "decision_time": cutoff.isoformat(),
            "forecast_interval_count": len(forecast_output),
            "actual_interval_count": len(actual_output),
            "comparison_interval_count": len(comparison_records),
            "metrics": metrics,
            "forecasts": forecast_output,
            "actuals": actual_output,
            "comparison": comparison_records.to_dict(orient="records"),
        }

    
    async def analyze_january(self) -> dict:
        start_date = date(2026, 1, 1)
        end_date = date(2026, 2, 1)
        last_date = date(2026, 1, 31)

        # Fetch actual generation once for the entire month.
        actual_records = await self.client.get_actual_wind(
            start_date, last_date
        )

        # Fetch forecast publications once, up to the latest
        # day-ahead decision cutoff needed for January.
        publish_from = datetime.combine(
            start_date, time.min, tzinfo=timezone.utc
        ) - timedelta(days=3)

        latest_cutoff = datetime.combine(
            last_date - timedelta(days=1),
            time(11, 0),
            tzinfo=timezone.utc,
        )

        forecast_records = await self.client.get_forecasts(
            publish_from, latest_cutoff
        )

        daily_results = []
        all_comparisons = []

        for offset in range(31):
            delivery_date = start_date + timedelta(days=offset)

            delivery_start = datetime.combine(
                delivery_date, time.min, tzinfo=timezone.utc
            )
            delivery_end = delivery_start + timedelta(days=1)

            # Provisional day-ahead decision cutoff.
            decision_time = datetime.combine(
                delivery_date - timedelta(days=1),
                time(11, 0),
                tzinfo=timezone.utc,
            )

            selected = select_forecast_vintage(
                forecast_records=forecast_records,
                decision_time=decision_time.isoformat(),
                delivery_start=delivery_start.isoformat(),
                delivery_end=delivery_end.isoformat(),
            )

            start_text = delivery_start.isoformat().replace(
                "+00:00", "Z"
            )
            end_text = delivery_end.isoformat().replace(
                "+00:00", "Z"
            )

            actual_day = [
                record
                for record in actual_records
                if start_text <= record["startTime"] < end_text
            ]

            selected_records = [
                {
                    "startTime": row["start_time"].isoformat(),
                    "generation": row["forecast_mw"],
                    "publishTime": row["publish_time"].isoformat(),
                }
                for _, row in selected.iterrows()
            ]

            comparison = build_comparison(
                actual_day, selected_records
            )

            if not comparison.empty:
                all_comparisons.append(comparison)
                day_metrics = calculate_metrics(
                    comparison["actual_mw"],
                    comparison["forecast_mw"],
                )
            else:
                day_metrics = {
                    "sample_count": 0,
                    "mae_mw": None,
                    "rmse_mw": None,
                    "bias_mw": None,
                    "wape_percent": None,
                }

            daily_results.append(
                {
                    "delivery_date": delivery_date.isoformat(),
                    "sample_count": day_metrics["sample_count"],
                    "mae_mw": day_metrics["mae_mw"],
                    "bias_mw": day_metrics["bias_mw"],
                    "wape_percent": day_metrics["wape_percent"],
                }
            )

        if all_comparisons:
            monthly_comparison = pd.concat(
                all_comparisons, ignore_index=True
            )
            monthly_metrics = calculate_metrics(
                monthly_comparison["actual_mw"],
                monthly_comparison["forecast_mw"],
            )
        else:
            monthly_metrics = {
                "sample_count": 0,
                "mae_mw": None,
                "rmse_mw": None,
                "bias_mw": None,
                "wape_percent": None,
            }

        return {
            "month": "2026-01",
            "decision_cutoff_rule": (
                "11:00 UTC on the day before delivery; "
                "provisional assumption"
            ),
            "metrics": monthly_metrics,
            "days_with_comparisons": sum(
                day["sample_count"] > 0 for day in daily_results
            ),
            "daily_results": daily_results,
        }
