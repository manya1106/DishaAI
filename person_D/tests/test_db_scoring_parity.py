"""
test_db_scoring_parity.py — Proves that ScoringEngine running over
PostGIS-backed data yields bit-for-bit identical rankings to the JSON snapshot (Gate D.9).
"""

import sys
from pathlib import Path

import pytest

person_d_dir = Path(__file__).resolve().parents[1]
repo_root = person_d_dir.parent
for p in [str(person_d_dir), str(repo_root), str(repo_root / "apps/api")]:
    if p not in sys.path:
        sys.path.insert(0, p)

from app.data.loader import loader as snapshot_loader
from app.scoring.engine import scoring_engine

from person_D.loader import db_loader


@pytest.mark.asyncio
async def test_scoring_parity_between_db_and_snapshot():
    # 1. Load cells from JSON snapshot
    snapshot_data = snapshot_loader.get_snapshot("blr")
    snapshot_cells = snapshot_data.get("cells", {})

    # 2. Load cells from PostGIS Database
    db_data = await db_loader.load_from_db("blr")
    db_cells = db_data.get("cells", {})

    assert len(db_cells) == len(snapshot_cells), f"Cell counts differ: DB has {len(db_cells)}, snapshot has {len(snapshot_cells)}"

    # 3. Score Cafe / Medium
    locs_snapshot, weights_snap = scoring_engine.score_cells(snapshot_cells, "cafe", "medium", top_n=10)
    locs_db, weights_db = scoring_engine.score_cells(db_cells, "cafe", "medium", top_n=10)

    assert len(locs_snapshot) == 10
    assert len(locs_db) == 10
    assert weights_snap == weights_db

    # 4. Assert bit-for-bit match on ranks, location IDs, scores, and confidence
    for snap_loc, db_loc in zip(locs_snapshot, locs_db):
        assert snap_loc.rank == db_loc.rank, f"Rank mismatch: {snap_loc.rank} != {db_loc.rank}"
        assert snap_loc.location_id == db_loc.location_id, f"Location ID mismatch: {snap_loc.location_id} != {db_loc.location_id}"
        assert snap_loc.overall_score == db_loc.overall_score, f"Score mismatch: {snap_loc.overall_score} != {db_loc.overall_score}"
        assert snap_loc.confidence == db_loc.confidence, f"Confidence mismatch: {snap_loc.confidence} != {db_loc.confidence}"
        
        # Check individual signals
        assert len(snap_loc.signals) == len(db_loc.signals)
        for s_snap, s_db in zip(snap_loc.signals, db_loc.signals):
            assert s_snap.signal_id == s_db.signal_id
            assert s_snap.score == s_db.score
            assert s_snap.status == s_db.status
