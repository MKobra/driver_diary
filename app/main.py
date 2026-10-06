from datetime import date

from fastapi import FastAPI, Query, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import INDEX_FILE, STATIC_DIR, TRIPS_FILE
from app.models import DaySummary, Trip, TripResponse
from app.storage import TripStorage
from app.summary import calculate_summary


app = FastAPI(title="Driver Diary")
storage = TripStorage(TRIPS_FILE)


@app.get("/api/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/trips", response_model=list[Trip])
async def get_trips(selected_date: date = Query(alias="date")) -> list[Trip]:
    trips = await storage.list_trips()
    return [trip for trip in trips if trip.start.date() == selected_date]


@app.get("/api/summary", response_model=DaySummary)
async def get_summary(selected_date: date = Query(alias="date")) -> DaySummary:
    trips = await storage.list_trips()
    return calculate_summary(trips, selected_date)


@app.post("/api/trips", response_model=TripResponse)
async def create_trip(trip: Trip, response: Response) -> TripResponse:
    stored_trip, created = await storage.add_trip(trip)
    response.status_code = 201 if created else 200
    message = "Поездка добавлена" if created else f"Поездка с id={trip.id} уже существует"
    return TripResponse(message=message, trip=stored_trip)


@app.get("/", include_in_schema=False)
async def index() -> FileResponse:
    return FileResponse(INDEX_FILE)


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
