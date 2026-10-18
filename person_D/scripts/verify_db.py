"""
verify_db.py — Verifies PostGIS extension, table counts, and spatial integrity.
"""

import asyncio
import sys
from pathlib import Path

person_d_dir = Path(__file__).resolve().parents[1]
repo_root = person_d_dir.parent
for p in [str(person_d_dir), str(repo_root)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from sqlalchemy import func, select, text

from person_D.db.connection import check_db_health, get_async_session
from person_D.db.models import POI, City, H3Cell


async def verify():
    print("[person_D] 1. Checking PostGIS database health...")
    health = await check_db_health()
    print(f"Health status: {health}")
    if not health.get("connected"):
        print("ERROR: Could not connect to database.")
        sys.exit(1)

    async with get_async_session() as session:
        # Check PostGIS version
        v_res = await session.execute(text("SELECT PostGIS_Full_Version();"))
        print(f"PostGIS Full Version: {v_res.scalar_one()}")

        # Check table counts
        city_count = (await session.execute(select(func.count(City.id)))).scalar_one()
        cell_count = (await session.execute(select(func.count(H3Cell.h3_index)))).scalar_one()
        poi_count = (await session.execute(select(func.count(POI.id)))).scalar_one()

        print(f"Counts: Cities = {city_count}, H3 Cells = {cell_count}, POIs = {poi_count}")

        # Check spatial geometry validity
        invalid_centroids = (await session.execute(
            text("SELECT count(*) FROM h3_cells WHERE NOT ST_IsValid(centroid);")
        )).scalar_one()
        invalid_boundaries = (await session.execute(
            text("SELECT count(*) FROM h3_cells WHERE NOT ST_IsValid(boundary);")
        )).scalar_one()

        print(f"Spatial validity: Invalid centroids = {invalid_centroids}, Invalid boundaries = {invalid_boundaries}")

        assert invalid_centroids == 0, "Found invalid centroid geometries!"
        assert invalid_boundaries == 0, "Found invalid boundary geometries!"

        print("[person_D] All PostGIS verification checks passed successfully!")


if __name__ == "__main__":
    asyncio.run(verify())
