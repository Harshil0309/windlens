from datetime import date, datetime, time, timedelta, timezone

from fastapi import APIRouter, HTTPException, Query

from app.services.analysis_service import AnalysisService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["Wind analysis"])
analysis_service = AnalysisService()


@router.get("/dates")
def get_available_dates():
    start = date(2026, 1, 1)
    return {
        "dates": [
            (start + timedelta(days=offset)).isoformat()
            for offset in range(31)
        ]
    }


@router.get("/forecast")
async def get_forecast(
    delivery_date: date = Query(
        default=date(2026, 1, 1),
        description="Delivery date in January 2026",
    ),
    decision_time: datetime | None = Query(
        default=None,
        description="Timezone-aware forecast decision cutoff",
    ),
):
    if not date(2026, 1, 1) <= delivery_date <= date(2026, 1, 31):
        raise HTTPException(
            status_code=400,
            detail="delivery_date must be within January 2026",
        )

    # Temporary pilot default: 11:00 UTC on the preceding day.
    # This is configurable and must not be presented as a verified
    # market rule until we confirm the applicable convention.
    if decision_time is None:
        previous_day = delivery_date - timedelta(days=1)
        decision_time = datetime.combine(
            previous_day,
            time(11, 0),
            tzinfo=timezone.utc,
        )

    if decision_time.tzinfo is None:
        raise HTTPException(
            status_code=400,
            detail="decision_time must include a timezone, e.g. Z or +00:00",
        )

    try:
        return await analysis_service.analyze_delivery_day(
            delivery_date=delivery_date,
            decision_time=decision_time,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Wind analysis failed for %s", delivery_date)
        raise HTTPException(
            status_code=502,
            detail=f"Wind analysis failed: {exc}",
        ) from exc


@router.get("/accuracy")
async def get_accuracy(
    delivery_date: date = Query(default=date(2026, 1, 1)),
    decision_time: datetime | None = Query(default=None),
):
    result = await get_forecast(
        delivery_date=delivery_date,
        decision_time=decision_time,
    )
    return {
        "delivery_date": result["delivery_date"],
        "decision_time": result["decision_time"],
        "metrics": result["metrics"],
        "forecast_interval_count": result["forecast_interval_count"],
        "actual_interval_count": result["actual_interval_count"],
        "comparison_interval_count": result["comparison_interval_count"],
    }


@router.get("/monthly-analysis")
async def get_monthly_analysis():
    try:
        return await analysis_service.analyze_january()
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Monthly wind analysis failed: {exc}",
        ) from exc
