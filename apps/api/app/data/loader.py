import json
from pathlib import Path
from typing import Any

from ..config import settings
from ..logging import logger

DATA_DIR = Path(__file__).resolve().parent / "snapshots"


class SnapshotLoader:
    def __init__(self):
        self._snapshots: dict[str, dict[str, Any]] = {}

    def get_snapshot(self, city_id: str = "blr") -> dict[str, Any]:
        mode = settings.DATA_MODE
        cache_key = f"{city_id}_{mode}"

        if cache_key in self._snapshots:
            return self._snapshots[cache_key]

        filename = f"{city_id}.json"
        if mode == "synthetic":
            filename = f"{city_id}_synthetic.json"

        file_path = DATA_DIR / filename
        if not file_path.exists():
            # Fallback to standard snapshot if synthetic doesn't exist or vice-versa
            file_path = DATA_DIR / f"{city_id}.json"

        if not file_path.exists():
            raise FileNotFoundError(f"Snapshot data file for {city_id} not found at {file_path}")

        logger.info(f"Loading geospatial snapshot from: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self._snapshots[cache_key] = data
        return data


loader = SnapshotLoader()
