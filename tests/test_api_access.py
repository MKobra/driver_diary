from fastapi.testclient import TestClient


def test_trip_endpoints_require_authentication(client: TestClient) -> None:
    trips = client.get("/api/trips?date=2026-10-01")
    summary = client.get("/api/summary?date=2026-10-01")

    assert trips.status_code == 401
    assert summary.status_code == 401
