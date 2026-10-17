from app.data.loader import loader
from app.scoring.engine import scoring_engine


def test_golden_ranking_reproducibility():
    """Verify that scoring identical inputs over the snapshot yields identical outputs."""
    snapshot = loader.get_snapshot("blr")
    cells = snapshot.get("cells", {})

    run_1_locs, _ = scoring_engine.score_cells(cells, "cafe", "medium", top_n=10)
    run_2_locs, _ = scoring_engine.score_cells(cells, "cafe", "medium", top_n=10)

    assert len(run_1_locs) == 10
    assert len(run_2_locs) == 10

    # Ensure exact match on ranking order, scores, and location IDs
    for loc1, loc2 in zip(run_1_locs, run_2_locs):
        assert loc1.rank == loc2.rank
        assert loc1.location_id == loc2.location_id
        assert loc1.overall_score == loc2.overall_score
        assert loc1.confidence == loc2.confidence
