import asyncio
import json
import os
import tempfile
from pathlib import Path

from app.models import Trip


class TripOverlapError(Exception):
    def __init__(self, conflicting_trip: Trip) -> None:
        super().__init__(
            f"Поездка пересекается с существующей поездкой {conflicting_trip.id}: "
            f"{conflicting_trip.start:%H:%M}–{conflicting_trip.end:%H:%M}"
        )


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
                if stored_trip.owner_id != trip.owner_id:
                    continue
                if stored_trip.id == trip.id:
                    return stored_trip, False
                if trip.start < stored_trip.end and trip.end > stored_trip.start:
                    raise TripOverlapError(stored_trip)

            trips.append(trip)
            await asyncio.to_thread(self._write_file, trips)
            return trip, True

    async def assign_legacy_trips(self, owner_id: str) -> None:
        async with self._lock:
            trips = await self.list_trips()
            legacy_trips = [trip.model_copy(update={"owner_id": owner_id}) for trip in trips if not trip.owner_id]
            if not legacy_trips:
                return
            updated_trips = [
                trip.model_copy(update={"owner_id": owner_id}) if not trip.owner_id else trip
                for trip in trips
            ]
            await asyncio.to_thread(self._write_file, updated_trips)

    async def seed_templates(self, templates_path: Path, owner_id: str) -> None:
        async with self._lock:
            trips = await self.list_trips()
            templates = await asyncio.to_thread(self._read_file_from_path, templates_path)
            template_trips = [Trip.model_validate(item) for item in templates]
            existing_ids = {trip.id for trip in trips if trip.owner_id == owner_id}
            seeded_trips = [
                template.model_copy(update={"owner_id": owner_id})
                for template in template_trips
                if template.id not in existing_ids
            ]
            if not seeded_trips:
                return
            await asyncio.to_thread(self._write_file, trips + seeded_trips)

    def _read_file(self) -> list[dict[str, object]]:
        return self._read_file_from_path(self._file_path)

    @staticmethod
    def _read_file_from_path(file_path: Path) -> list[dict[str, object]]:
        with file_path.open(encoding="utf-8") as file:
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
