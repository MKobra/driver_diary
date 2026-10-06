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


def test_register_rejects_mismatched_passwords_and_duplicate_phone(client: TestClient) -> None:
    mismatched = client.post(
        "/api/auth/register",
        json={
            "phone": "79001234567",
            "password": "strong-pass-1",
            "password_confirm": "different-pass",
        },
    )
    first = client.post(
        "/api/auth/register",
        json={
            "phone": "79001234567",
            "password": "strong-pass-1",
            "password_confirm": "strong-pass-1",
        },
    )
    duplicate = client.post(
        "/api/auth/register",
        json={
            "phone": "+7 (900) 123-45-67",
            "password": "strong-pass-2",
            "password_confirm": "strong-pass-2",
        },
    )

    assert mismatched.status_code == 422
    assert first.status_code == 201
    assert duplicate.status_code == 409


def test_login_rejects_wrong_password_and_logout_expires_session(client: TestClient) -> None:
    client.post(
        "/api/auth/register",
        json={
            "phone": "79001234567",
            "password": "strong-pass-1",
            "password_confirm": "strong-pass-1",
        },
    )

    wrong_password = client.post(
        "/api/auth/login",
        json={"phone": "79001234567", "password": "wrong-pass"},
    )
    logged_in = client.post(
        "/api/auth/login",
        json={"phone": "79001234567", "password": "strong-pass-1"},
    )
    logged_out = client.post("/api/auth/logout")

    assert wrong_password.status_code == 401
    assert logged_in.status_code == 200
    assert logged_out.status_code == 200
    assert client.get("/api/auth/me").status_code == 401
