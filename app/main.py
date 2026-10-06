from datetime import date

from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.auth import create_session, hash_password, read_session, verify_password
from app.config import (
    DEFAULT_PAGE_SIZE,
    INDEX_FILE,
    MAX_PAGE_SIZE,
    SESSION_COOKIE,
    SESSION_MAX_AGE,
    SESSION_SECRET,
    STATIC_DIR,
    TRIPS_FILE,
    USERS_FILE,
)
from app.models import (
    AuthResponse,
    DaySummary,
    LoginRequest,
    RegisterRequest,
    Trip,
    TripPage,
    TripResponse,
    UserPublic,
)
from app.storage import TripOverlapError, TripStorage
from app.summary import calculate_summary
from app.user_storage import UserStorage


app = FastAPI(title="Driver Diary")
storage = TripStorage(TRIPS_FILE)
users = UserStorage(USERS_FILE)


@app.get("/api/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/auth/register", response_model=AuthResponse, status_code=201)
async def register(payload: RegisterRequest, response: Response) -> AuthResponse:
    user = await users.create(payload.phone, hash_password(payload.password))
    if user is None:
        raise HTTPException(status_code=409, detail="Пользователь с таким телефоном уже существует")
    _set_session_cookie(response, user.id)
    return AuthResponse(message="Регистрация выполнена", user=UserPublic(id=user.id, phone=user.phone))


@app.post("/api/auth/login", response_model=AuthResponse)
async def login(payload: LoginRequest, response: Response) -> AuthResponse:
    user = await users.get_by_phone(payload.phone)
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Неверный телефон или пароль")
    _set_session_cookie(response, user.id)
    return AuthResponse(message="Вход выполнен", user=UserPublic(id=user.id, phone=user.phone))


@app.post("/api/auth/logout")
async def logout(response: Response) -> dict[str, str]:
    response.delete_cookie(SESSION_COOKIE, path="/")
    return {"message": "Выход выполнен"}


@app.get("/api/auth/me", response_model=UserPublic)
async def current_user(request: Request) -> UserPublic:
    user_id = read_session(request.cookies.get(SESSION_COOKIE), SESSION_SECRET, SESSION_MAX_AGE)
    user = await users.get_by_id(user_id) if user_id else None
    if user is None:
        raise HTTPException(status_code=401, detail="Требуется вход в аккаунт")
    return UserPublic(id=user.id, phone=user.phone)


def _set_session_cookie(response: Response, user_id: str) -> None:
    response.set_cookie(
        SESSION_COOKIE,
        create_session(user_id, SESSION_SECRET),
        max_age=SESSION_MAX_AGE,
        httponly=True,
        samesite="lax",
        path="/",
    )


@app.get("/api/trips", response_model=TripPage)
async def get_trips(
    selected_date: date = Query(alias="date"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
) -> TripPage:
    trips = await storage.list_trips()
    daily_trips = sorted(
        (trip for trip in trips if trip.start.date() == selected_date),
        key=lambda trip: trip.start,
    )
    total = len(daily_trips)
    total_pages = max(1, (total + page_size - 1) // page_size)
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    return TripPage(
        items=daily_trips[start_index:end_index],
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
    )


@app.get("/api/summary", response_model=DaySummary)
async def get_summary(selected_date: date = Query(alias="date")) -> DaySummary:
    trips = await storage.list_trips()
    return calculate_summary(trips, selected_date)


@app.post("/api/trips", response_model=TripResponse)
async def create_trip(trip: Trip, response: Response) -> TripResponse:
    try:
        stored_trip, created = await storage.add_trip(trip)
    except TripOverlapError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    response.status_code = 201 if created else 200
    message = "Поездка добавлена" if created else f"Поездка с id={trip.id} уже существует"
    return TripResponse(message=message, trip=stored_trip, created=created)


@app.get("/", include_in_schema=False)
async def index() -> FileResponse:
    return FileResponse(INDEX_FILE)


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
