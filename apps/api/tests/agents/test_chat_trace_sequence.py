import pytest

from app.agents.orchestrator import orchestrator
from app.ai.chat import chat_orchestrator
from app.routers.analyses import AnalysisInputs, compute_analysis
from app.schemas.chat import ChatRequest


@pytest.mark.asyncio
async def test_deterministic_request_produces_narrator_then_verifier_trace():
    analysis = compute_analysis(AnalysisInputs(city_id="blr", category_id="cafe", budget_tier="medium", top_n=5))
    request = ChatRequest(
        message="Why is #1 ranked at the top?",
        selected_location_ids=[analysis.locations[0].location_id],
        mode="deterministic",
    )

    response = await chat_orchestrator.handle_chat(analysis, request)
    trace = orchestrator.get_trace(response.trace_id)

    recipients = [m.recipient for m in trace]
    # build_bundle (verifier) happens first, then narrator drafts, then verifier checks
    assert recipients == ["verifier", "narrator", "verifier"]
    assert all(m.sender == "orchestrator" for m in trace)
    assert [m.step for m in trace] == [0, 1, 2]


@pytest.mark.asyncio
async def test_trap_question_produces_no_agent_dispatch_beyond_bundle_build():
    analysis = compute_analysis(AnalysisInputs(city_id="blr", category_id="cafe", budget_tier="medium", top_n=5))
    request = ChatRequest(
        message="What is the exact monthly rent in rupees for #1?",
        selected_location_ids=[analysis.locations[0].location_id],
        mode="auto",
    )

    response = await chat_orchestrator.handle_chat(analysis, request)
    trace = orchestrator.get_trace(response.trace_id)

    # Refusal short-circuits before any narrator/verifier drafting happens
    assert [m.recipient for m in trace] == ["verifier"]
