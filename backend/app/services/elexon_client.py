from datetime import date, datetime, timezone

import httpx

BASE_URL = "https://data.elexon.co.uk/bmrs/api/v1/datasets"


class ElexonClient:
    """Client for retrieving wind generation data from Elexon BMRS."""

    def __init__(self, timeout: float = 60.0):
        self.timeout = timeout

    async def get_actual_wind(
        self,
        start_date: date,
        end_date: date,
    ) -> list[dict]:
        """Fetch actual wind generation for an inclusive date range."""
        params = {
            "settlementDateFrom": start_date.isoformat(),
            "settlementDateTo": end_date.isoformat(),
            "fuelType": "WIND",
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{BASE_URL}/FUELHH/stream",
                params=params,
            )
            response.raise_for_status()
            return response.json()

    async def get_forecasts(
        self,
        publish_from: datetime,
        publish_to: datetime,
    ) -> list[dict]:
        """Fetch forecasts published within a specified time range."""
        if publish_from.tzinfo is None or publish_to.tzinfo is None:
            raise ValueError("Publication timestamps must include a timezone.")

        params = {
            "publishDateTimeFrom": publish_from.astimezone(
                timezone.utc
            ).isoformat().replace("+00:00", "Z"),
            "publishDateTimeTo": publish_to.astimezone(
                timezone.utc
            ).isoformat().replace("+00:00", "Z"),
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{BASE_URL}/WINDFOR/stream",
                params=params,
            )
            response.raise_for_status()
            return response.json()
