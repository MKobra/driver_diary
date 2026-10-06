import asyncio
from pathlib import Path

import pytest

from app.models import Trip
from app.storage import TripOverlapError, TripStorage


def test_overlapping_trips_are_rejected_but_adjacent_trips_are_allowed(tmp_path: Path) -> None:
    storage_file = tmp_path / "trips.json"
    storage_file.write_text("[]", encoding="utf-8")
    storage = TripStorage(storage_file)
    first_trip = Trip(
        owner_id="driver-1",
        id="first",
        start="2026-10-01T13:00:00+05:00",
        end="2026-10-01T13:30:00+05:00",
        amount=1000,
        payment="cash",
        commission=100,
    )
    overlapping_trip = Trip.model_validate(
        {**first_trip.model_dump(), "id": "overlap", "start": "2026-10-01T13:20:00+05:00"}
    )
    adjacent_trip = Trip.model_validate(
        {
            **first_trip.model_dump(),
            "id": "adjacent",
            "start": "2026-10-01T13:30:00+05:00",
            "end": "2026-10-01T14:00:00+05:00",
        }
    )

    async def add_trips() -> tuple[Trip, Trip]:
        created, _ = await storage.add_trip(first_trip)
        with pytest.raises(TripOverlapError):
            await storage.add_trip(overlapping_trip)
        adjacent, _ = await storage.add_trip(adjacent_trip)
        return created, adjacent

    created, adjacent = asyncio.run(add_trips())

    assert created.id == "first"
    assert adjacent.id == "adjacent"
