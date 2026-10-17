import pytest
from app.ai.evidence import EvidenceBundle, SlimEvidenceItem, SlimLocationEvidence
from app.ai.verifier import verifier
from app.schemas.chat import LLMBlock, LLMClaim, LLMOutput
from app.schemas.enums import ClaimPolarity, ClaimType, VerificationStatus


@pytest.fixture
def mock_bundle():
    lookup = {
        "ev_001": SlimEvidenceItem(
            ev_id="ev_001",
            location_id="loc_1",
            signal_id="competition_density",
            label="Competitor count",
            value=14,
            unit="POIs",
            provenance="measured"
        ),
        "ev_002": SlimEvidenceItem(
            ev_id="ev_002",
            location_id="loc_1",
            signal_id="daytime_population",
            label="Daytime score",
            value=85.0,
            unit="score",
            provenance="estimated"
        ),
        "ev_003": SlimEvidenceItem(
            ev_id="ev_003",
            location_id="loc_2",
            signal_id="daytime_population",
            label="Daytime score",
            value=60.0,
            unit="score",
            provenance="estimated"
        ),
        "ev_004": SlimEvidenceItem(
            ev_id="ev_004",
            location_id="loc_1",
            signal_id="rent_efficiency",
            label="Rent tier",
            value="Tier 3/5",
            unit="heuristic tier",
            provenance="heuristic"
        ),
    }

    loc1 = SlimLocationEvidence(
        location_id="loc_1",
        display_name="Indiranagar Core",
        rank=1,
        overall_score=78.5,
        confidence="high",
        signals={
            "competition_density": {"score": 64.0, "contribution": 7.7, "evidence_ids": ["ev_001"]},
            "daytime_population": {"score": 85.0, "contribution": 11.9, "evidence_ids": ["ev_002"]},
            "rent_efficiency": {"score": 70.0, "contribution": 8.4, "evidence_ids": ["ev_004"]},
            "transit_access": {"score": 30.0, "contribution": 3.0, "evidence_ids": []},
        },
        strengths=["Strong daytime population"],
        limitations=["Subdued transit access"],
        why_vs_neighbours=[]
    )

    loc2 = SlimLocationEvidence(
        location_id="loc_2",
        display_name="Koramangala Hub",
        rank=2,
        overall_score=72.0,
        confidence="high",
        signals={
            "daytime_population": {"score": 60.0, "contribution": 8.4, "evidence_ids": ["ev_003"]},
        },
        strengths=[],
        limitations=[],
        why_vs_neighbours=[]
    )

    return EvidenceBundle(
        analysis_id="test_analysis",
        category_id="cafe",
        budget_tier="medium",
        selected_locations=[loc1, loc2],
        evidence_lookup=lookup,
        allowed_numbers=[1.0, 2.0, 14.0, 78.5, 72.0, 64.0, 85.0, 60.0, 70.0, 30.0],
        allowed_names=["indiranagar core", "koramangala hub"],
        unavailable_signals=[]
    )


def test_v1_empty_output_fails(mock_bundle):
    output = LLMOutput(blocks=[])
    _blocks, violations, status = verifier.verify(output, mock_bundle)
    assert status == VerificationStatus.REJECTED_FALLBACK
    assert any("V1" in v for v in violations)


def test_v2_unknown_evidence_id_fails(mock_bundle):
    output = LLMOutput(blocks=[
        LLMBlock(
            text="Indiranagar leads with score 78.5.",
            claims=[LLMClaim(
                type=ClaimType.SCORE,
                location_ids=["loc_1"],
                evidence_ids=["ev_999_fake"],
                numbers=[78.5]
            )]
        )
    ])
    _blocks, violations, status = verifier.verify(output, mock_bundle)
    assert any("V2_UNKNOWN_EVIDENCE_ID" in v for v in violations)
    assert status == VerificationStatus.REJECTED_FALLBACK


def test_v3_invented_number_fails(mock_bundle):
    output = LLMOutput(blocks=[
        LLMBlock(
            text="Indiranagar has an invented score of 999.0.",
            claims=[LLMClaim(
                type=ClaimType.SCORE,
                location_ids=["loc_1"],
                evidence_ids=["ev_001"],
                numbers=[999.0]
            )]
        )
    ])
    _blocks, violations, _status = verifier.verify(output, mock_bundle)
    assert any("V3" in v for v in violations)


def test_v4_unknown_rank_fails(mock_bundle):
    output = LLMOutput(blocks=[
        LLMBlock(
            text="Zone ranks #99 in the analysis.",
            claims=[LLMClaim(
                type=ClaimType.RANK,
                location_ids=["loc_1"],
                evidence_ids=["ev_001"],
                numbers=[]
            )]
        )
    ])
    _blocks, violations, _status = verifier.verify(output, mock_bundle)
    assert any("V4_UNKNOWN_RANK" in v for v in violations)


def test_v5_contradictory_comparison_fails(mock_bundle):
    # Claiming loc_2 beats loc_1 on daytime_population when loc_1 has 85 and loc_2 has 60
    output = LLMOutput(blocks=[
        LLMBlock(
            text="Koramangala beats Indiranagar on daytime population.",
            claims=[LLMClaim(
                type=ClaimType.COMPARISON,
                location_ids=["loc_2", "loc_1"],
                signal_id="daytime_population",
                polarity=ClaimPolarity.STRENGTH,
                evidence_ids=["ev_003"],
                numbers=[]
            )]
        )
    ])
    _blocks, violations, _status = verifier.verify(output, mock_bundle)
    assert any("V5_CONTRADICTORY_COMPARISON" in v for v in violations)


def test_v6_polarity_strength_on_weak_signal_fails(mock_bundle):
    # Claiming transit_access (score 30.0) is a strength
    output = LLMOutput(blocks=[
        LLMBlock(
            text="Indiranagar has strong transit access.",
            claims=[LLMClaim(
                type=ClaimType.FACT,
                location_ids=["loc_1"],
                signal_id="transit_access",
                polarity=ClaimPolarity.STRENGTH,
                evidence_ids=["ev_001"],
                numbers=[]
            )]
        )
    ])
    _blocks, violations, _status = verifier.verify(output, mock_bundle)
    assert any("V6_POLARITY_MISMATCH" in v for v in violations)


def test_v7_forbidden_rupee_currency_fails(mock_bundle):
    output = LLMOutput(blocks=[
        LLMBlock(
            text="Expected monthly rent in rupees is ₹85,000.",
            claims=[LLMClaim(
                type=ClaimType.FACT,
                location_ids=["loc_1"],
                evidence_ids=["ev_004"],
                numbers=[]
            )]
        )
    ])
    _blocks, violations, _status = verifier.verify(output, mock_bundle)
    assert any("V7_FORBIDDEN_TOPIC" in v for v in violations)


def test_v8_uncited_numbers_fails(mock_bundle):
    # Text contains number 42 with no claims
    output = LLMOutput(blocks=[
        LLMBlock(
            text="There are 42 coffee lovers nearby.",
            claims=[]
        )
    ])
    _blocks, violations, _status = verifier.verify(output, mock_bundle)
    assert any("V8_UNCITED_NUMBERS" in v for v in violations)


def test_valid_response_passes(mock_bundle):
    output = LLMOutput(blocks=[
        LLMBlock(
            text="Indiranagar Core ranks #1 with an overall score of 78.5.",
            claims=[LLMClaim(
                type=ClaimType.SCORE,
                location_ids=["loc_1"],
                evidence_ids=["ev_001"],
                numbers=[1.0, 78.5],
                polarity=ClaimPolarity.STRENGTH
            )]
        )
    ])
    blocks, violations, status = verifier.verify(output, mock_bundle)
    assert status == VerificationStatus.VERIFIED
    assert len(violations) == 0
    assert len(blocks) == 1
