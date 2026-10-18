import pytest

from app.agents.verifier_agent import verifier_agent
from app.ai.evidence import build_evidence_bundle
from app.ai.verifier import verifier
from app.routers.analyses import AnalysisInputs, compute_analysis
from app.schemas.chat import LLMBlock, LLMClaim, LLMOutput
from app.schemas.enums import ClaimPolarity, ClaimType


@pytest.fixture
def analysis():
    return compute_analysis(AnalysisInputs(city_id="blr", category_id="cafe", budget_tier="medium", top_n=5))


def test_build_bundle_matches_direct_call(analysis):
    selected = [analysis.locations[0].location_id]
    via_agent = verifier_agent.build_bundle(analysis, selected)
    direct = build_evidence_bundle(analysis, selected)

    assert via_agent.analysis_id == direct.analysis_id
    assert via_agent.selected_locations[0].location_id == direct.selected_locations[0].location_id
    assert set(via_agent.evidence_lookup.keys()) == set(direct.evidence_lookup.keys())


def test_check_matches_direct_verify(analysis):
    bundle = verifier_agent.build_bundle(analysis, [analysis.locations[0].location_id])
    loc = bundle.selected_locations[0]
    ev_id = next(iter(bundle.evidence_lookup.keys()))

    draft = LLMOutput(blocks=[LLMBlock(
        text=f"{loc.display_name} ranks #{loc.rank} overall.",
        claims=[LLMClaim(
            type=ClaimType.SCORE,
            location_ids=[loc.location_id],
            polarity=ClaimPolarity.STRENGTH,
            evidence_ids=[ev_id],
            numbers=[float(loc.rank)],
        )],
    )])

    via_agent = verifier_agent.check(draft, bundle)
    direct = verifier.verify(draft, bundle)

    assert via_agent[2] == direct[2]
    assert len(via_agent[0]) == len(direct[0])
