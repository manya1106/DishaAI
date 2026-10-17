from app.scoring.signals import (
    compute_competition_density,
    compute_gap_opportunity,
    compute_rent_efficiency,
)


def test_competition_density():
    features = {"cafe": {"competitor_density": 14}}
    assert compute_competition_density(features, "cafe") == 14.0
    assert compute_competition_density({}, "cafe") == 0.0


def test_gap_opportunity():
    features = {
        "cafe": {"competitor_density": 3},
        "footfall_anchors": 10,
        "residential_catchment": 20,
    }
    # demand = (10 * 1.5) + (20 * 0.8) = 15 + 16 = 31
    # gap = 31 / (3 + 1) = 7.75
    assert compute_gap_opportunity(features, "cafe") == 7.75


def test_rent_efficiency():
    # Ceiling = 3 (medium budget)
    assert compute_rent_efficiency(area_tier=2, budget_ceiling=3) == 100.0  # below ceiling
    assert compute_rent_efficiency(area_tier=3, budget_ceiling=3) == 70.0   # at ceiling
    assert compute_rent_efficiency(area_tier=4, budget_ceiling=3) == 40.0   # 1 tier above
    assert compute_rent_efficiency(area_tier=5, budget_ceiling=3) == 10.0   # 2 tiers above
    assert compute_rent_efficiency(area_tier=6, budget_ceiling=3) == 0.0    # capped at 0
