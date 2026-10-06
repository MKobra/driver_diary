import os
import secrets
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
TRIPS_FILE = PROJECT_ROOT / "data" / "trips.json"
USERS_FILE = PROJECT_ROOT / "data" / "users.json"
STATIC_DIR = PROJECT_ROOT / "app" / "static"
INDEX_FILE = STATIC_DIR / "index.html"
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 50
SESSION_COOKIE = "driver_diary_session"
SESSION_MAX_AGE = 60 * 60 * 24 * 7
SESSION_SECRET = os.getenv("DRIVER_DIARY_SESSION_SECRET") or secrets.token_bytes(32)
