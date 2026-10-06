import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import app.main as main
from app.storage import TripStorage
from app.user_storage import UserStorage


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    trips_file = tmp_path / "trips.json"
    trips_file.write_text(json.dumps([]), encoding="utf-8")
    monkeypatch.setattr(main, "storage", TripStorage(trips_file))
    monkeypatch.setattr(main, "users", UserStorage(tmp_path / "users.json"))
    return TestClient(main.app)
