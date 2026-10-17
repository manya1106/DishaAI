from typing import Any


def compute_competition_density(features: dict[str, Any], category_id: str) -> float:
    """Raw count of same-category competitors in neighbourhood (lower is better)."""
    cat_feats = features.get(category_id, {})
    return float(cat_feats.get("competitor_density", 0))


def compute_gap_opportunity(features: dict[str, Any], category_id: str) -> float:
    """Demand proxy (anchors + residential) divided by (competitors + 1). Higher is better."""
    cat_feats = features.get(category_id, {})
    competitors = cat_feats.get("competitor_density", 0)
    anchors = features.get("footfall_anchors", 0)
    residential = features.get("residential_catchment", 0)

    demand = (anchors * 1.5) + (residential * 0.8)
    return round(demand / (competitors + 1.0), 2)


def compute_footfall_anchors(features: dict[str, Any]) -> float:
    """Footfall anchors count (malls, colleges, markets, hospitals). Higher is better."""
    return float(features.get("footfall_anchors", 0))


def compute_transit_access(features: dict[str, Any]) -> float:
    """Transit stops accessibility score. Higher is better."""
    return float(features.get("transit_access", 0))


def compute_complementary_mix(features: dict[str, Any], category_id: str) -> float:
    """Count of complementary commercial entities. Higher is better."""
    cat_feats = features.get(category_id, {})
    return float(cat_feats.get("complementary_mix", 0))


def compute_residential_catchment(features: dict[str, Any]) -> float:
    """Residential household proxy count. Higher is better."""
    return float(features.get("residential_catchment", 0))


def compute_daytime_population(features: dict[str, Any]) -> float:
    """Commercial and office daytime activity proxy count. Higher is better."""
    return float(features.get("daytime_population", 0))


def compute_road_accessibility(features: dict[str, Any]) -> float:
    """Road accessibility index (road length km + junction proxy). Higher is better."""
    road_km = features.get("road_accessibility", 0.0)
    junctions = features.get("junction_count", 0)
    return round(road_km + (junctions * 0.4), 2)


def compute_rent_efficiency(area_tier: int, budget_ceiling: int) -> float:
    """
    Heuristic rent efficiency score on a [0, 100] scale based on budget ceiling:
    - If area_tier <= ceiling - 1: score = 100.0
    - If area_tier == ceiling:     score = 70.0
    - If area_tier > ceiling:      score = max(0.0, 70.0 - 30.0 * (area_tier - ceiling))
    """
    if area_tier <= budget_ceiling - 1:
        return 100.0
    elif area_tier == budget_ceiling:
        return 70.0
    else:
        return max(0.0, 70.0 - 30.0 * float(area_tier - budget_ceiling))
