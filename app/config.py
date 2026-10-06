from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
TRIPS_FILE = PROJECT_ROOT / "data" / "trips.json"
STATIC_DIR = PROJECT_ROOT / "app" / "static"
INDEX_FILE = STATIC_DIR / "index.html"
