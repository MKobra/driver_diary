import asyncio
import json
from pathlib import Path

from app.models import Trip
from app.storage import TripStorage


def test_add_trip_with_same_id_does_not_create_duplicate(tmp_path: Path) -> None:
    storage_file = tmp_path / "trips.json"
    storage_file.write_text("[]", encoding="utf-8")
    storage = TripStorage(storage_file)
    trip = Trip(
        owner_id="driver-1",
        id="same-id",
        start="2026-10-01T08:00:00+05:00",
        end="2026-10-01T08:30:00+05:00",
        amount=1000,
        payment="cash",
        commission=100,
    )

    async def add_twice() -> tuple[tuple[Trip, bool], tuple[Trip, bool]]:
        first = await storage.add_trip(trip)
        second = await storage.add_trip(trip)
        return first, second

    first, second = asyncio.run(add_twice())
    stored_data = json.loads(storage_file.read_text(encoding="utf-8"))

    assert first[1] is True
    assert second[1] is False
    assert second[0].id == trip.id
    assert len(stored_data) == 1
