import sys
from pathlib import Path

person_d_dir = Path(__file__).resolve().parents[1]
repo_root = person_d_dir.parent
for p in [str(person_d_dir), str(repo_root)]:
    if p not in sys.path:
        sys.path.insert(0, p)

import pytest
from sqlalchemy import func, select

from person_D.db.connection import get_async_session
from person_D.db.models import POI, City, H3Cell
from person_D.scripts.load_snapshot_to_db import load_snapshot


@pytest.mark.asyncio
async def test_loader_idempotency():
    # Run 1: Load snapshot
    counts_run1 = await load_snapshot("blr")
    assert counts_run1["cities"] >= 1
    assert counts_run1["h3_cells"] == 417
    assert counts_run1["pois"] == 2592

    # Run 2: Re-run snapshot loader
    counts_run2 = await load_snapshot("blr")

    # Assert exact equality
    assert counts_run2["cities"] == counts_run1["cities"], "City count changed on second load!"
    assert counts_run2["h3_cells"] == counts_run1["h3_cells"], "H3 cell count changed on second load!"
    assert counts_run2["pois"] == counts_run1["pois"], "POI count changed on second load!"

    # Double check directly in database
    async with get_async_session() as session:
        city_count = (await session.execute(select(func.count(City.id)))).scalar_one()
        cell_count = (await session.execute(select(func.count(H3Cell.h3_index)))).scalar_one()
        poi_count = (await session.execute(select(func.count(POI.id)))).scalar_one()

        assert city_count == 1
        assert cell_count == 417
        assert poi_count == 2592
