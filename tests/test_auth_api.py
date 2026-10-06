from fastapi.testclient import TestClient


def test_register_normalizes_phone_and_creates_session(client: TestClient) -> None:
    response = client.post(
        "/api/auth/register",
        json={
            "phone": "+7 (900) 123-45-67",
            "password": "strong-pass-1",
            "password_confirm": "strong-pass-1",
        },
    )

    assert response.status_code == 201
    assert response.json()["user"]["phone"] == "79001234567"
    assert client.get("/api/auth/me").status_code == 200
