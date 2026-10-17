from typing import Any

from ..schemas.analysis import EvidenceItem, LocationResult, SignalDelta
from ..schemas.enums import ProvenanceClass


def build_evidence_for_locations(
    locations: list[LocationResult],
    cells_dict: dict[str, Any],
    category_id: str
) -> list[EvidenceItem]:
    """Generates explicit evidence items with stable IDs and provenance for each scored signal."""
    evidence_items: list[EvidenceItem] = []

    for loc in locations:
        cell = cells_dict.get(loc.location_id)
        if not cell:
            continue

        features = cell.get("features", {})
        cat_features = features.get(category_id, {})

        for sig in loc.signals:
            ev_id = f"ev_{loc.location_id}_{sig.signal_id}"
            
            if sig.signal_id == "competition_density":
                val = cat_features.get("competitor_density", 0)
                unit = "competitors"
                label = f"{category_id.title()} competitors in neighbourhood"
                source = "OpenStreetMap snapshot"
            elif sig.signal_id == "gap_opportunity":
                anchors = features.get("footfall_anchors", 0)
                res = features.get("residential_catchment", 0)
                comp = cat_features.get("competitor_density", 0)
                val = round(((anchors * 1.5) + (res * 0.8)) / (comp + 1.0), 2)
                unit = "demand/supply ratio"
                label = "Gap opportunity index"
                source = "Derived demand proxy / OSM"
            elif sig.signal_id == "footfall_anchors":
                val = features.get("footfall_anchors", 0)
                unit = "major anchors"
                label = "Malls, colleges, markets & hospitals"
                source = "OpenStreetMap snapshot"
            elif sig.signal_id == "transit_access":
                val = features.get("transit_access", 0)
                unit = "transit stops"
                label = "Bus stops and metro access points"
                source = "OpenStreetMap snapshot"
            elif sig.signal_id == "complementary_mix":
                val = cat_features.get("complementary_mix", 0)
                unit = "synergy businesses"
                label = "Complementary commercial entities"
                source = "OpenStreetMap snapshot"
            elif sig.signal_id == "residential_catchment":
                val = features.get("residential_catchment", 0)
                unit = "residential units proxy"
                label = "Apartments & residential buildings"
                source = "OpenStreetMap snapshot"
            elif sig.signal_id == "daytime_population":
                val = features.get("daytime_population", 0)
                unit = "daytime establishments"
                label = "Offices, commercial & tech park entities"
                source = "OpenStreetMap snapshot"
            elif sig.signal_id == "road_accessibility":
                val = features.get("road_accessibility", 0.0)
                unit = "km road length"
                label = "Primary & secondary road network length"
                source = "OpenStreetMap snapshot"
            elif sig.signal_id == "rent_efficiency":
                tier = cell.get("rent_tier", "Unknown")
                val = f"Rent Tier {tier}/5"
                unit = "heuristic tier"
                label = "Commercial rent feasibility tier"
                source = "Team-assigned rent tiers (unverified)"
            else:
                val = 0
                unit = "units"
                label = sig.signal_id
                source = "Disha AI Engine"

            evidence_items.append(EvidenceItem(
                evidence_id=ev_id,
                location_id=loc.location_id,
                signal_id=sig.signal_id,
                kind="heuristic" if sig.provenance == ProvenanceClass.HEURISTIC else "metric",
                label=label,
                value=val,
                unit=unit,
                provenance=sig.provenance,
                source=source,
                as_of="2026-10"
            ))

    return evidence_items


def build_comparison_deltas(locations: list[LocationResult]) -> list[SignalDelta]:
    """Computes per-signal score differentials across 2 or 3 compared locations."""
    deltas: list[SignalDelta] = []
    if len(locations) < 2:
        return deltas

    all_signal_ids = [s.signal_id for s in locations[0].signals]

    for sid in all_signal_ids:
        scores: dict[str, float | None] = {}
        for loc in locations:
            matching = next((s for s in loc.signals if s.signal_id == sid), None)
            scores[loc.location_id] = matching.score if matching else None

        # Determine winner for this signal
        valid_scores = [(lid, sc) for lid, sc in scores.items() if sc is not None]
        winner = None
        exp = "Equal scores."

        if valid_scores:
            valid_scores.sort(key=lambda x: x[1], reverse=True)
            top_lid, top_score = valid_scores[0]
            if len(valid_scores) > 1 and top_score > valid_scores[1][1]:
                winner = top_lid
                top_loc = next(l for l in locations if l.location_id == top_lid)
                runner_up = next(l for l in locations if l.location_id == valid_scores[1][0])
                diff = round(top_score - valid_scores[1][1], 1)
                exp = f"{top_loc.display_name} leads {runner_up.display_name} by +{diff} pts."
            elif len(valid_scores) > 1 and top_score == valid_scores[1][1]:
                exp = "Tied score across top locations."
            else:
                top_loc = next(l for l in locations if l.location_id == top_lid)
                winner = top_lid
                exp = f"{top_loc.display_name} is the sole location with available data."

        deltas.append(SignalDelta(
            signal_id=sid,
            scores=scores,
            winner_location_id=winner,
            delta_explanation=exp
        ))

    return deltas
