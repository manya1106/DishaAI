import pytest

from app.ai import score_review
from app.schemas.analysis import LocationResult, SignalResult
from app.schemas.common import Centroid
from app.schemas.enums import ConfidenceLevel, ProvenanceClass, SignalStatus


def _make_location(location_id: str, rank: int, overall_score: float) -> LocationResult:
    return LocationResult(
        location_id=location_id,
        rank=rank,
        display_name=f"Zone {location_id}",
        centroid=Centroid(lat=12.9, lng=77.6),
        polygon=[[12.9, 77.6], [12.91, 77.6], [12.91, 77.61], [12.9, 77.61]],
        overall_score=overall_score,
        confidence=ConfidenceLevel.HIGH,
        coverage=1.0,
        signals=[
            SignalResult(
                signal_id="footfall_anchors",
                score=80.0,
                weight=0.2,
                effective_weight=0.2,
                contribution=16.0,
                status=SignalStatus.OK,
                provenance=ProvenanceClass.MEASURED,
                evidence_ids=[],
            )
        ],
        strengths=["Strong footfall anchors (score: 80.0, contrib: 16.0 pts)"],
        limitations=[],
        why_vs_neighbours=[],
    )


@pytest.fixture
def two_locations():
    return [_make_location("a", 1, 70.0), _make_location("b", 2, 60.0)]


def test_llm_disabled_leaves_scores_unchanged(two_locations, monkeypatch):
    monkeypatch.setattr(score_review.settings, "LLM_ENABLED", False)
    result = score_review.review_scores_sync(two_locations, "cafe")

    assert [r.overall_score for r in result] == [70.0, 60.0]
    assert all(r.ai_adjustment_multiplier == 1.0 for r in result)
    assert all(r.ai_adjustment_reason is None for r in result)
    assert [r.deterministic_score for r in result] == [70.0, 60.0]
    assert [r.rank for r in result] == [1, 2]


def test_grounded_adjustment_is_applied_and_bounded(two_locations, monkeypatch):
    monkeypatch.setattr(score_review.settings, "LLM_ENABLED", True)

    async def fake_generate_json(system_prompt, user_prompt, **kwargs):
        return {
            "adjustments": [
                # Grounded: cites the real footfall_anchors score (80.0) and
                # requests a multiplier beyond the allowed band, which must
                # be clamped rather than trusted verbatim.
                {"location_id": "a", "multiplier": 1.5, "reason": "footfall_anchors score of 80.0 is unusually strong"},
                {"location_id": "b", "multiplier": 1.0, "reason": None},
            ]
        }

    monkeypatch.setattr(score_review.llm_adapter, "generate_json", fake_generate_json)

    result = score_review.review_scores_sync(two_locations, "cafe")
    loc_a = next(r for r in result if r.location_id == "a")
    loc_b = next(r for r in result if r.location_id == "b")

    assert loc_a.ai_adjustment_multiplier == score_review.MAX_MULTIPLIER
    assert loc_a.overall_score == round(70.0 * score_review.MAX_MULTIPLIER, 1)
    assert loc_a.deterministic_score == 70.0
    assert loc_a.ai_adjustment_reason is not None

    assert loc_b.ai_adjustment_multiplier == 1.0
    assert loc_b.overall_score == 60.0


def test_ungrounded_reason_is_discarded(two_locations, monkeypatch):
    monkeypatch.setattr(score_review.settings, "LLM_ENABLED", True)

    async def fake_generate_json(system_prompt, user_prompt, **kwargs):
        return {
            "adjustments": [
                {
                    "location_id": "a",
                    "multiplier": 1.05,
                    "reason": "this zone has 999 nearby competitors and a rent of 50000 rupees",
                },
            ]
        }

    monkeypatch.setattr(score_review.llm_adapter, "generate_json", fake_generate_json)

    result = score_review.review_scores_sync(two_locations, "cafe")
    loc_a = next(r for r in result if r.location_id == "a")

    assert loc_a.ai_adjustment_multiplier == 1.0
    assert loc_a.overall_score == 70.0


def test_malformed_llm_response_falls_back_to_deterministic(two_locations, monkeypatch):
    monkeypatch.setattr(score_review.settings, "LLM_ENABLED", True)

    async def fake_generate_json(system_prompt, user_prompt, **kwargs):
        return {"not_adjustments": "garbage"}

    monkeypatch.setattr(score_review.llm_adapter, "generate_json", fake_generate_json)

    result = score_review.review_scores_sync(two_locations, "cafe")
    assert [r.overall_score for r in result] == [70.0, 60.0]
    assert all(r.ai_adjustment_multiplier == 1.0 for r in result)


def test_adjustment_can_change_ranking(monkeypatch):
    close_locations = [_make_location("a", 1, 70.0), _make_location("b", 2, 68.0)]
    monkeypatch.setattr(score_review.settings, "LLM_ENABLED", True)

    async def fake_generate_json(system_prompt, user_prompt, **kwargs):
        return {
            "adjustments": [
                {"location_id": "a", "multiplier": 1.0, "reason": None},
                {"location_id": "b", "multiplier": 1.05, "reason": "footfall_anchors score of 80.0 supports a slight uplift"},
            ]
        }

    monkeypatch.setattr(score_review.llm_adapter, "generate_json", fake_generate_json)

    result = score_review.review_scores_sync(close_locations, "cafe")
    assert result[0].location_id == "b"
    assert result[0].rank == 1
    assert result[1].location_id == "a"
    assert result[1].rank == 2
