"""Postgres-backed data loader (Phase D).

Reconstructs the exact dict shape SnapshotLoader.get_snapshot() returns
from the JSON snapshot, so scoring/engine.py and everything downstream
of it work completely unchanged regardless of which loader is active.
Selected by DATA_MODE=postgres (apps/api/app/config.py); the JSON
snapshot loader remains the default/offline fallback.
"""

import asyncio
import concurrent.futures
from typing import Any

from geoalchemy2.shape import to_shape
from sqlalchemy import select

from ..db.base import SessionLocal
from ..db.models import City, H3Cell
from ..logging import logger


def _run_sync(coro):
    """Run an async coroutine from sync code, safe even when called from
    inside an already-running event loop (e.g. a FastAPI async route
    calling this synchronously). asyncio.run() alone would raise
    RuntimeError in that case; running it in a fresh thread avoids that.
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, coro).result()


class PostgresLoader:
    def __init__(self):
        self._cache: dict[str, dict[str, Any]] = {}

    def get_snapshot(self, city_id: str = "blr") -> dict[str, Any]:
        if city_id in self._cache:
            return self._cache[city_id]

        if SessionLocal is None:
            raise RuntimeError("DATABASE_URL is not configured; cannot use the Postgres loader")

        snapshot = _run_sync(self._fetch(city_id))
        self._cache[city_id] = snapshot
        return snapshot

    async def _fetch(self, city_id: str) -> dict[str, Any]:
        async with SessionLocal() as session:
            city_result = await session.execute(select(City).where(City.slug == city_id))
            city = city_result.scalar_one_or_none()
            if city is None:
                raise FileNotFoundError(f"City '{city_id}' not found in Postgres; run scripts/ingest_osm_bengaluru.py")

            cells_result = await session.execute(select(H3Cell).where(H3Cell.city_id == city.id))
            db_cells = cells_result.scalars().all()

            cells: dict[str, Any] = {}
            eligible_count = 0
            for c in db_cells:
                point = to_shape(c.centroid)
                if not c.ineligible:
                    eligible_count += 1
                cells[c.h3_index] = {
                    "cell_id": c.h3_index,
                    "centroid": {"lat": point.y, "lng": point.x},
                    "polygon": c.boundary,
                    "display_name": c.display_name,
                    "rent_tier": c.rent_tier,
                    "ineligible": c.ineligible,
                    "neighbourhood_pois": c.neighbourhood_pois,
                    "features": c.features,
                    "pois": [],
                }

            logger.info(f"Loaded {len(cells)} H3 cells from Postgres for city '{city_id}' ({eligible_count} eligible)")

            return {
                "dataset_id": f"{city_id}-osm-postgres",
                "city_id": city_id,
                "as_of": "2026-09",
                "attribution": "© OpenStreetMap contributors (ODbL)",
                "is_synthetic": False,
                "h3_resolution": city.h3_resolution,
                "cell_count": len(cells),
                "eligible_cell_count": eligible_count,
                "cells": cells,
            }


postgres_loader = PostgresLoader()
