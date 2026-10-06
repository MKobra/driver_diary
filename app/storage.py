import asyncio
import json
import os
import tempfile
from pathlib import Path

from app.models import Trip


class TripStorage:
    def __init__(self, file_path: Path) -> None:
        self._file_path = file_path
        self._lock = asyncio.Lock()

    async def list_trips(self) -> list[Trip]:
        payload = await asyncio.to_thread(self._read_file)
        return [Trip.model_validate(item) for item in payload]

    async def add_trip(self, trip: Trip) -> tuple[Trip, bool]:
        async with self._lock:
            trips = await self.list_trips()
            for stored_trip in trips:
                if stored_trip.id == trip.id:
                    return stored_trip, False

            trips.append(trip)
            await asyncio.to_thread(self._write_file, trips)
            return trip, True

    def _read_file(self) -> list[dict[str, object]]:
        with self._file_path.open(encoding="utf-8") as file:
            payload = json.load(file)
        if not isinstance(payload, list):
            raise ValueError("Файл поездок должен содержать JSON-массив")
        return payload

    def _write_file(self, trips: list[Trip]) -> None:
        self._file_path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=self._file_path.parent,
            prefix=f"{self._file_path.name}.",
            delete=False,
        ) as temporary_file:
            json.dump(
                [trip.model_dump(mode="json") for trip in trips],
                temporary_file,
                ensure_ascii=False,
                indent=2,
            )
            temporary_path = Path(temporary_file.name)
        os.replace(temporary_path, self._file_path)
