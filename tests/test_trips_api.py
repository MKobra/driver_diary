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
