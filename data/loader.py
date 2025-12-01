# data/loader.py

import json
from pathlib import Path

DATA_DIR = Path("data")
CACHE_DIR = DATA_DIR / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def load_json(filename: str):
    """Load JSON file from data/."""
    file_path = DATA_DIR / filename
    if not file_path.exists():
        return None
    with open(file_path, "r") as f:
        return json.load(f)

def save_json(filename: str, data):
    """Save JSON file to data/."""
    file_path = DATA_DIR / filename
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)