import pytest

from app.scoring.engine import scoring_engine


def test_students_boosts_footfall_anchors_weight_for_cafe():
    base = scoring_engine.get_category_weights("cafe")
    multipliers = scoring_engine.compute_answer_multipliers("cafe", target_customers=["students"])
    modified = scoring_engine.get_category_weights("cafe", multipliers=multipliers)

    assert sum(modified.values()) == pytest.approx(1.0, abs=1e-3)
    # footfall_anchors should have gained relative weight vs. its base share
    assert modified["footfall_anchors"] / sum(modified.values()) > base["footfall_anchors"] / sum(base.values())


def test_category_answer_modifier_applies_for_pharmacy_24x7():
    base = scoring_engine.get_category_weights("pharmacy")
    multipliers = scoring_engine.compute_answer_multipliers(
        "pharmacy", category_answers={"is_24x7": "true"}
    )
    modified = scoring_engine.get_category_weights("pharmacy", multipliers=multipliers)

    assert sum(modified.values()) == pytest.approx(1.0, abs=1e-3)
    assert modified["transit_access"] > base["transit_access"]


def test_no_wizard_answers_leaves_weights_unchanged():
    base = scoring_engine.get_category_weights("gym")
    multipliers = scoring_engine.compute_answer_multipliers("gym")
    modified = scoring_engine.get_category_weights("gym", multipliers=multipliers)

    assert modified == base


def test_score_cells_accepts_target_customers_without_error():
    from app.data.loader import loader

    snapshot = loader.get_snapshot("blr")
    locations, weights = scoring_engine.score_cells(
        snapshot["cells"], "cafe", "medium", top_n=5, target_customers=["students"]
    )
    assert len(locations) == 5
    assert sum(weights.values()) == pytest.approx(1.0, abs=1e-3)
