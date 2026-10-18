from app.agents.scoring_agent import scoring_agent
from app.data.loader import loader
from app.scoring.engine import scoring_engine


def test_score_matches_direct_engine_call():
    via_agent, weights_agent = scoring_agent.score("blr", "cafe", "medium", top_n=5)

    snapshot = loader.get_snapshot("blr")
    direct, weights_direct = scoring_engine.score_cells(snapshot["cells"], "cafe", "medium", top_n=5)

    assert weights_agent == weights_direct
    assert len(via_agent) == len(direct)
    for a, b in zip(via_agent, direct):
        assert a.location_id == b.location_id
        assert a.overall_score == b.overall_score
        assert a.rank == b.rank
