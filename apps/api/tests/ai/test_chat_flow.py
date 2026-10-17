import pytest
from app.ai.chat import chat_orchestrator
from app.routers.analyses import AnalysisInputs, compute_analysis
from app.schemas.chat import ChatRequest
from app.schemas.enums import ChatMode, VerificationStatus


@pytest.mark.asyncio
async def test_trap_question_refusal():
    analysis = compute_analysis(AnalysisInputs(city_id="blr", category_id="cafe", budget_tier="medium", top_n=5))
    request = ChatRequest(
        message="What is the exact monthly rent in rupees for #1?",
        selected_location_ids=[analysis.locations[0].location_id],
        mode="auto"
    )

    response = await chat_orchestrator.handle_chat(analysis, request)
    assert response.mode == ChatMode.REFUSED_INSUFFICIENT_DATA
    assert response.uncertainty.insufficient_data is True
    assert "financial" in response.blocks[0].text.lower() or "lease" in response.blocks[0].text.lower()


@pytest.mark.asyncio
async def test_deterministic_mode_flow():
    analysis = compute_analysis(AnalysisInputs(city_id="blr", category_id="cafe", budget_tier="medium", top_n=5))
    request = ChatRequest(
        message="Why is #1 ranked at the top?",
        selected_location_ids=[analysis.locations[0].location_id],
        mode="deterministic"
    )

    response = await chat_orchestrator.handle_chat(analysis, request)
    assert response.mode == ChatMode.DETERMINISTIC_REQUESTED
    assert response.verification.status == VerificationStatus.VERIFIED
    assert len(response.blocks) >= 1
    assert response.blocks[0].claims[0].verified is True


@pytest.mark.asyncio
async def test_compare_intent_flow():
    analysis = compute_analysis(AnalysisInputs(city_id="blr", category_id="cafe", budget_tier="medium", top_n=5))
    loc1 = analysis.locations[0].location_id
    loc2 = analysis.locations[1].location_id

    request = ChatRequest(
        message="Compare #1 and #2",
        selected_location_ids=[loc1, loc2],
        mode="deterministic"
    )

    response = await chat_orchestrator.handle_chat(analysis, request)
    assert response.mode == ChatMode.DETERMINISTIC_REQUESTED
    assert len(response.blocks) >= 2
    # Second block should compare signals
    claim_types = [c.type for b in response.blocks for c in b.claims]
    assert any("comparison" in str(ct).lower() for ct in claim_types)
