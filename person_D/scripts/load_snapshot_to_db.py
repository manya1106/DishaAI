"""
load_snapshot_to_db.py — Migrates JSON snapshot data into PostgreSQL + PostGIS.
Idempotent: running multiple times preserves exact row counts.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add person_D and repo root to sys.path
person_d_dir = Path(__file__).resolve().parents[1]
repo_root = person_d_dir.parent
for p in [str(person_d_dir), str(repo_root)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from sqlalchemy import delete, func, select

from person_D.db.connection import get_async_session
from person_D.db.models import POI, City, H3Cell


async def load_snapshot(city_slug: str = "blr", snapshot_path: Path | None = None) -> dict[str, int]:
    if snapshot_path is None:
        snapshot_path = repo_root / "apps/api/app/data/snapshots" / f"{city_slug}.json"

    if not snapshot_path.exists():
        raise FileNotFoundError(f"Snapshot not found at {snapshot_path}")

    print(f"[person_D] Reading snapshot from: {snapshot_path}")
    with open(snapshot_path, "r", encoding="utf-8") as f:  # noqa: ASYNC230
        data = json.load(f)

    city_id_slug = data.get("city_id", city_slug)
    cells_data = data.get("cells", {})
    print(f"[person_D] Found city '{city_id_slug}' with {len(cells_data)} H3 cells.")

    async with get_async_session() as session:
        # 1. Upsert City
        city_stmt = select(City).where(City.slug == city_id_slug)
        result = await session.execute(city_stmt)
        city = result.scalar_one_or_none()

        if city is None:
            city = City(
                slug=city_id_slug,
                name="Bengaluru" if city_id_slug == "blr" else city_id_slug.capitalize(),
            )
            session.add(city)
            await session.flush()
            print(f"[person_D] Created City record with id: {city.id}")
        else:
            print(f"[person_D] City record already exists with id: {city.id}")

        city_db_id = city.id

        # 2. Upsert H3 Cells
        print(f"[person_D] Loading {len(cells_data)} H3 cells...")
        loaded_cells = 0
        total_pois_loaded = 0

        for cell_id, cell_info in cells_data.items():
            centroid = cell_info.get("centroid", {})
            lat = centroid.get("lat", 0.0)
            lng = centroid.get("lng", 0.0)

            # Construct centroid point SQL
            centroid_geom = func.ST_SetSRID(func.ST_MakePoint(lng, lat), 4326)

            # Construct boundary polygon
            raw_poly = cell_info.get("polygon", [])
            if raw_poly:
                # Ensure closed ring
                ring = list(raw_poly)
                if ring[0] != ring[-1]:
                    ring.append(ring[0])
                geojson_poly = json.dumps({"type": "Polygon", "coordinates": [ring]})
                boundary_geom = func.ST_SetSRID(func.ST_GeomFromGeoJSON(geojson_poly), 4326)
            else:
                boundary_geom = centroid_geom

            # Check if cell exists
            existing_cell = await session.get(H3Cell, cell_id)
            if existing_cell is None:
                new_cell = H3Cell(
                    h3_index=cell_id,
                    city_id=city_db_id,
                    centroid=centroid_geom,
                    boundary=boundary_geom,
                    locality_name=cell_info.get("display_name"),
                    rent_tier=cell_info.get("rent_tier"),
                    ineligible=cell_info.get("ineligible", False),
                    features=cell_info.get("features", {}),
                )
                session.add(new_cell)
            else:
                existing_cell.locality_name = cell_info.get("display_name")
                existing_cell.rent_tier = cell_info.get("rent_tier")
                existing_cell.ineligible = cell_info.get("ineligible", False)
                existing_cell.features = cell_info.get("features", {})
                existing_cell.centroid = centroid_geom
                existing_cell.boundary = boundary_geom

            loaded_cells += 1

        await session.flush()
        print(f"[person_D] Successfully upserted {loaded_cells} H3 cells.")

        # 3. Load POIs idempotently
        # Delete existing snapshot POIs for these cells to maintain exact idempotency
        h3_indices = list(cells_data.keys())
        await session.execute(delete(POI).where(POI.h3_index.in_(h3_indices)))

        poi_objects = []
        for cell_id, cell_info in cells_data.items():
            for p in cell_info.get("pois", []):
                p_lat = p.get("lat")
                p_lng = p.get("lng")
                p_geom = None
                if p_lat is not None and p_lng is not None:
                    p_geom = func.ST_SetSRID(func.ST_MakePoint(p_lng, p_lat), 4326)

                poi_objects.append(
                    POI(
                        h3_index=cell_id,
                        category=p.get("group", "general"),
                        name=p.get("name"),
                        lat=p_lat,
                        lng=p_lng,
                        geom=p_geom,
                        tags={"source": "snapshot"},
                    )
                )

        if poi_objects:
            session.add_all(poi_objects)
            await session.flush()
            total_pois_loaded = len(poi_objects)
            print(f"[person_D] Successfully inserted {total_pois_loaded} POIs.")

        # Verify counts
        cell_count_res = await session.execute(select(func.count(H3Cell.h3_index)))
        poi_count_res = await session.execute(select(func.count(POI.id)))
        city_count_res = await session.execute(select(func.count(City.id)))

        counts = {
            "cities": city_count_res.scalar_one(),
            "h3_cells": cell_count_res.scalar_one(),
            "pois": poi_count_res.scalar_one(),
        }
        print(f"[person_D] Current DB Totals -> Cities: {counts['cities']}, Cells: {counts['h3_cells']}, POIs: {counts['pois']}")
        return counts


if __name__ == "__main__":
    asyncio.run(load_snapshot())
