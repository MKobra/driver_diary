from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient


def test_repeated_trip_id_returns_existing_trip_without_duplicate(client: TestClient) -> None:
    client.post(
        "/api/auth/register",
        json={
            "phone": "79001234567",
            "password": "strong-pass-1",
            "password_confirm": "strong-pass-1",
        },
    )
    payload = {
        "id": "trip-1",
        "start": "2026-10-01T08:00:00+05:00",
        "end": "2026-10-01T08:30:00+05:00",
        "amount": 1000,
        "payment": "cash",
        "commission": 100,
    }

    first = client.post("/api/trips", json=payload)
    duplicate = client.post("/api/trips", json=payload)
    page = client.get("/api/trips?date=2026-10-01&page=1&page_size=10")

    assert first.status_code == 201
    assert first.json()["created"] is True
    assert duplicate.status_code == 200
    assert duplicate.json()["created"] is False
    assert page.json()["total"] == 1


def test_overlapping_trip_returns_conflict(client: TestClient) -> None:
    client.post(
        "/api/auth/register",
        json={
            "phone": "79001234567",
            "password": "strong-pass-1",
            "password_confirm": "strong-pass-1",
        },
    )
    first = {
        "id": "trip-1",
        "start": "2026-10-01T08:00:00+05:00",
        "end": "2026-10-01T08:30:00+05:00",
        "amount": 1000,
        "payment": "cash",
        "commission": 100,
    }
    overlapping = {**first, "id": "trip-2", "start": "2026-10-01T08:20:00+05:00"}

    assert client.post("/api/trips", json=first).status_code == 201
    response = client.post("/api/trips", json=overlapping)

    assert response.status_code == 409
    assert "trip-1" in response.json()["detail"]


def test_invalid_trip_data_returns_unprocessable_entity(client: TestClient) -> None:
    client.post(
        "/api/auth/register",
        json={
            "phone": "79001234567",
            "password": "strong-pass-1",
            "password_confirm": "strong-pass-1",
        },
    )
    response = client.post(
        "/api/trips",
        json={
            "id": "invalid",
            "start": "2026-10-01T09:00:00+05:00",
            "end": "2026-10-01T08:00:00+05:00",
            "amount": 0,
            "payment": "online",
            "commission": 100,
        },
    )

    assert response.status_code == 422
    assert len(response.json()["detail"]) >= 2


def test_trip_list_returns_paginated_items(client: TestClient) -> None:
    client.post(
        "/api/auth/register",
        json={
            "phone": "79001234567",
            "password": "strong-pass-1",
            "password_confirm": "strong-pass-1",
        },
    )
    start = datetime(2026, 10, 1, 8, tzinfo=timezone(timedelta(hours=5)))
    for index in range(11):
        trip_start = start + timedelta(minutes=index * 30)
        trip_end = trip_start + timedelta(minutes=30)
        response = client.post(
            "/api/trips",
            json={
                "id": f"trip-{index}",
                "start": trip_start.isoformat(),
                "end": trip_end.isoformat(),
                "amount": 1000,
                "payment": "cash",
                "commission": 100,
            },
        )
        assert response.status_code == 201

    first_page = client.get("/api/trips?date=2026-10-01&page=1&page_size=10")
    second_page = client.get("/api/trips?date=2026-10-01&page=2&page_size=10")

    assert first_page.json()["total"] == 11
    assert first_page.json()["total_pages"] == 2
    assert len(first_page.json()["items"]) == 10
    assert len(second_page.json()["items"]) == 1


def test_each_driver_sees_only_own_trips(client: TestClient) -> None:
    first_driver = client.post(
        "/api/auth/register",
        json={
            "phone": "79001234567",
            "password": "strong-pass-1",
            "password_confirm": "strong-pass-1",
        },
    )
    first_trip = client.post(
        "/api/trips",
        json={
            "id": "private-trip",
            "start": "2026-10-01T08:00:00+05:00",
            "end": "2026-10-01T08:30:00+05:00",
            "amount": 1000,
            "payment": "cash",
            "commission": 100,
        },
    )
    second_client = TestClient(client.app)
    second_driver = second_client.post(
        "/api/auth/register",
        json={
            "phone": "79001234568",
            "password": "strong-pass-2",
            "password_confirm": "strong-pass-2",
        },
    )
    second_trips = second_client.get("/api/trips?date=2026-10-01&page=1&page_size=10")
    first_trips = client.get("/api/trips?date=2026-10-01&page=1&page_size=10")

    assert first_driver.status_code == 201
    assert first_trip.status_code == 201
    assert second_driver.status_code == 201
    assert second_trips.json()["total"] == 0
    assert first_trips.json()["total"] == 1
