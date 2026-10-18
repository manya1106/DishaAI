"""
loader.py — Database-backed geospatial loader for Disha AI (person_D).
Reads city, cells, POIs, and signals from PostgreSQL + PostGIS,
with automatic fallback to JSON snapshot if DB is unavailable.
"""

import json
import logging
from pathlib import Path
from typing import Any

from sqlalchemy import func, select

logger = logging.getLogger("disha.person_D.loader")

# Path setup
person_d_dir = Path(__file__).resolve().parent
repo_root = person_d_dir.parent


class DatabaseLoader:
    def __init__(self):
        self._cache: dict[str, dict[str, Any]] = {}

    def get_snapshot(self, city_id: str = "blr") -> dict[str, Any]:
        """
        Synchronous wrapper around DB loader or cache, with snapshot fallback.
        """
        if city_id in self._cache:
            return self._cache[city_id]

        try:
            import asyncio
            data = asyncio.run(self.load_from_db(city_id))
            if data and data.get("cells"):
                self._cache[city_id] = data
                return data
        except Exception as exc:  # noqa: BLE001
            logger.warning(f"[person_D] Could not load from DB ({exc}), falling back to JSON snapshot.")

        return self._load_fallback_json(city_id)

    async def load_from_db(self, city_id: str = "blr") -> dict[str, Any]:
        from person_D.db.connection import get_async_session
        from person_D.db.models import POI, City, H3Cell

        async with get_async_session() as session:
            # Query city
            city_stmt = select(City).where(City.slug == city_id)
            res = await session.execute(city_stmt)
            city = res.scalar_one_or_none()
            if not city:
                raise ValueError(f"City '{city_id}' not found in database.")

            # Query all cells for this city with GeoJSON representations of centroid and boundary
            cells_stmt = select(
                H3Cell.h3_index,
                H3Cell.locality_name,
                H3Cell.rent_tier,
                H3Cell.ineligible,
                H3Cell.features,
                func.ST_AsGeoJSON(H3Cell.centroid).label("centroid_geojson"),
                func.ST_AsGeoJSON(H3Cell.boundary).label("boundary_geojson"),
            ).where(H3Cell.city_id == city.id)

            cell_rows = (await session.execute(cells_stmt)).all()
            if not cell_rows:
                raise ValueError(f"No cells found for city '{city_id}'.")

            # Query all POIs
            pois_stmt = select(
                POI.h3_index,
                POI.category,
                POI.name,
                POI.lat,
                POI.lng,
            ).where(POI.h3_index.in_([r.h3_index for r in cell_rows]))

            poi_rows = (await session.execute(pois_stmt)).all()
            pois_by_cell: dict[str, list[dict[str, Any]]] = {}
            for p in poi_rows:
                pois_by_cell.setdefault(p.h3_index, []).append({
                    "name": p.name,
                    "group": p.category,
                    "lat": p.lat,
                    "lng": p.lng,
                })

            # Assemble cells dict
            cells_dict: dict[str, Any] = {}
            for row in cell_rows:
                c_geom = json.loads(row.centroid_geojson) if row.centroid_geojson else {"coordinates": [0, 0]}
                b_geom = json.loads(row.boundary_geojson) if row.boundary_geojson else {"coordinates": [[]]}
                
                coords = b_geom.get("coordinates", [[]])
                polygon = coords[0] if coords else []

                cells_dict[row.h3_index] = {
                    "cell_id": row.h3_index,
                    "display_name": row.locality_name,
                    "rent_tier": row.rent_tier,
                    "ineligible": row.ineligible,
                    "features": row.features or {},
                    "centroid": {
                        "lng": c_geom["coordinates"][0],
                        "lat": c_geom["coordinates"][1],
                    },
                    "polygon": polygon,
                    "pois": pois_by_cell.get(row.h3_index, []),
                }

            assembled = {
                "dataset_id": f"{city_id}_db",
                "city_id": city_id,
                "city_name": city.name,
                "cell_count": len(cells_dict),
                "eligible_cell_count": sum(1 for c in cells_dict.values() if not c["ineligible"]),
                "cells": cells_dict,
                "attribution": "OpenStreetMap contributors (PostGIS DB)",
                "data_mode": "database",
            }
            self._cache[city_id] = assembled
            return assembled

    def _load_fallback_json(self, city_id: str) -> dict[str, Any]:
        snapshot_file = repo_root / "apps/api/app/data/snapshots" / f"{city_id}.json"
        if not snapshot_file.exists():
            raise FileNotFoundError(f"Neither DB nor fallback JSON found for {city_id}")
        with open(snapshot_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self._cache[city_id] = data
        return data


db_loader = DatabaseLoader()
