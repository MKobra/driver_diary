from datetime import date

from fastapi import FastAPI, Query, Response

from app.config import TRIPS_FILE
from app.models import Trip
from app.storage import TripStorage


app = FastAPI(title="Driver Diary")
storage = TripStorage(TRIPS_FILE)


@app.get("/api/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/trips", response_model=list[Trip])
async def get_trips(selected_date: date = Query(alias="date")) -> list[Trip]:
    trips = await storage.list_trips()
    return [trip for trip in trips if trip.start.date() == selected_date]


@app.post("/api/trips", response_model=Trip)
async def create_trip(trip: Trip, response: Response) -> Trip:
    stored_trip, created = await storage.add_trip(trip)
    response.status_code = 201 if created else 200
    return stored_trip
