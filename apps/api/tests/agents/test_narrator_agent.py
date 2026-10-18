import pytest

from app.agents.narrator_agent import narrator_agent
from app.agents.verifier_agent import verifier_agent
from app.ai.fallback import deterministic_narrator
from app.routers.analyses import AnalysisInputs, compute_analysis


@pytest.fixture
def bundle():
    analysis = compute_analysis(AnalysisInputs(city_id="blr", category_id="cafe", budget_tier="medium", top_n=5))
    return verifier_agent.build_bundle(analysis, [analysis.locations[0].location_id])


def test_draft_deterministic_matches_direct_call(bundle):
    via_agent = narrator_agent.draft_deterministic("Why is #1 ranked at the top?", bundle)
    direct = deterministic_narrator.narrate("Why is #1 ranked at the top?", bundle)

    assert len(via_agent.blocks) == len(direct.blocks)
    assert via_agent.blocks[0].text == direct.blocks[0].text


@pytest.mark.asyncio
async def test_draft_llm_returns_none_when_disabled(bundle):
    # settings.LLM_ENABLED defaults to False in this environment (no API key configured)
    result = await narrator_agent.draft_llm("system prompt", "user prompt")
    assert result is None
