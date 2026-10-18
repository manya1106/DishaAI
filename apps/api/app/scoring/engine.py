from pathlib import Path
from typing import Any

import yaml

from ..schemas.analysis import Centroid, LocationResult, SignalResult
from ..schemas.enums import ConfidenceLevel, ProvenanceClass, SignalStatus
from .signals import (
    compute_competition_density,
    compute_complementary_mix,
    compute_daytime_population,
    compute_footfall_anchors,
    compute_gap_opportunity,
    compute_rent_efficiency,
    compute_residential_catchment,
    compute_road_accessibility,
    compute_transit_access,
)

CONFIG_DIR = Path(__file__).resolve().parent / "configs"


def load_config(filename: str) -> dict:
    with open(CONFIG_DIR / filename, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def calculate_percentile_ranks(values: list[float], invert: bool = False) -> list[float]:
    """
    Computes relative percentile rank (0 to 100) for each element in values.
    Ties receive the average rank.
    If invert=True (e.g. lower is better), inverts so lower raw values get higher scores.
    """
    n = len(values)
    if n == 0:
        return []
    if n == 1:
        return [100.0]

    # Pair each value with its original index
    indexed = sorted(enumerate(values), key=lambda x: x[1])
    
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        # Find tie group
        while j < n and indexed[j][1] == indexed[i][1]:
            j += 1
        
        # Average rank for tie group (1-indexed rank)
        avg_rank = (i + 1 + j) / 2.0
        # Percentile scale: 0 to 100
        percentile = ((avg_rank - 1.0) / (n - 1.0)) * 100.0
        
        for k in range(i, j):
            orig_idx = indexed[k][0]
            if invert:
                ranks[orig_idx] = round(100.0 - percentile, 1)
            else:
                ranks[orig_idx] = round(percentile, 1)
        i = j

    return ranks


class ScoringEngine:
    def __init__(self):
        self._weights_config = load_config("weights.yaml")
        self._budget_config = load_config("budget_tiers.yaml")
        self._answer_modifiers_config = load_config("answer_modifiers.yaml")

    def compute_answer_multipliers(
        self,
        category_id: str,
        target_customers: list[str] | None = None,
        category_answers: dict[str, str] | None = None,
    ) -> dict[str, float]:
        """Combine wizard-answer multipliers into one per-signal factor.

        Mirrors SiteScout's "answer_modifiers" concept (plan.md-adjacent):
        each selected answer nudges specific signal weights, applied
        multiplicatively, never as a hard override.
        """
        multipliers: dict[str, float] = {}

        def apply(mods: dict[str, float]) -> None:
            for signal_id, factor in mods.items():
                multipliers[signal_id] = multipliers.get(signal_id, 1.0) * factor

        tc_config = self._answer_modifiers_config.get("target_customers", {})
        for tc in target_customers or []:
            apply(tc_config.get(tc, {}))

        cat_config = self._answer_modifiers_config.get("category_answers", {}).get(category_id, {})
        for question_id, answer in (category_answers or {}).items():
            answer_key = str(answer).lower()
            apply(cat_config.get(question_id, {}).get(answer_key, {}))

        return multipliers

    def get_category_weights(
        self,
        category_id: str,
        overrides: dict[str, float] | None = None,
        multipliers: dict[str, float] | None = None,
    ) -> dict[str, float]:
        categories = self._weights_config.get("categories", {})
        base = dict(categories.get(category_id, categories.get("cafe", {})))

        if multipliers:
            for k, factor in multipliers.items():
                if k in base:
                    base[k] = base[k] * factor

        if overrides:
            for k, v in overrides.items():
                if k in base and v >= 0:
                    base[k] = v

        if multipliers or overrides:
            # Renormalize to sum to 1.0
            total = sum(base.values())
            if total > 0:
                base = {k: round(v / total, 4) for k, v in base.items()}
        return base

    def get_budget_ceiling(self, budget_tier: str) -> int:
        tiers = self._budget_config.get("budget_tiers", {})
        return tiers.get(budget_tier, {}).get("max_acceptable_tier", 3)

    def score_cells(
        self,
        cells: dict[str, Any],
        category_id: str,
        budget_tier: str,
        weight_overrides: dict[str, float] | None = None,
        top_n: int = 10,
        target_customers: list[str] | None = None,
        category_answers: dict[str, str] | None = None,
    ) -> tuple[list[LocationResult], dict[str, float]]:
        answer_multipliers = self.compute_answer_multipliers(category_id, target_customers, category_answers)
        weights = self.get_category_weights(category_id, weight_overrides, answer_multipliers)
        budget_ceiling = self.get_budget_ceiling(budget_tier)

        eligible_cells = [c for c in cells.values() if not c.get("ineligible", False)]
        if not eligible_cells:
            return [], weights

        [c["cell_id"] for c in eligible_cells]

        # 1. Compute raw values across all eligible cells
        raw_competition = [compute_competition_density(c["features"], category_id) for c in eligible_cells]
        raw_gap = [compute_gap_opportunity(c["features"], category_id) for c in eligible_cells]
        raw_footfall = [compute_footfall_anchors(c["features"]) for c in eligible_cells]
        raw_transit = [compute_transit_access(c["features"]) for c in eligible_cells]
        raw_complementary = [compute_complementary_mix(c["features"], category_id) for c in eligible_cells]
        raw_residential = [compute_residential_catchment(c["features"]) for c in eligible_cells]
        raw_daytime = [compute_daytime_population(c["features"]) for c in eligible_cells]
        raw_road = [compute_road_accessibility(c["features"]) for c in eligible_cells]

        # 2. Percentile normalisation (0-100)
        norm_competition = calculate_percentile_ranks(raw_competition, invert=True)  # lower competition is better
        norm_gap = calculate_percentile_ranks(raw_gap, invert=False)
        norm_footfall = calculate_percentile_ranks(raw_footfall, invert=False)
        norm_transit = calculate_percentile_ranks(raw_transit, invert=False)
        norm_complementary = calculate_percentile_ranks(raw_complementary, invert=False)
        norm_residential = calculate_percentile_ranks(raw_residential, invert=False)
        norm_daytime = calculate_percentile_ranks(raw_daytime, invert=False)
        norm_road = calculate_percentile_ranks(raw_road, invert=False)

        # 3. Assemble signals per cell and compute overall score with missing-data renormalisation
        locations: list[LocationResult] = []

        for idx, cell in enumerate(eligible_cells):
            cell_id = cell["cell_id"]
            area_tier = cell.get("rent_tier")
            
            # Check availability of signals
            signal_scores: dict[str, float | None] = {
                "competition_density": norm_competition[idx],
                "gap_opportunity": norm_gap[idx],
                "footfall_anchors": norm_footfall[idx],
                "transit_access": norm_transit[idx],
                "complementary_mix": norm_complementary[idx],
                "residential_catchment": norm_residential[idx],
                "daytime_population": norm_daytime[idx],
                "road_accessibility": norm_road[idx],
            }

            if area_tier is not None:
                signal_scores["rent_efficiency"] = compute_rent_efficiency(area_tier, budget_ceiling)
            else:
                signal_scores["rent_efficiency"] = None

            # Missing data renormalisation
            available_weight_sum = sum(
                weights[sid] for sid, score in signal_scores.items() if score is not None
            )

            signal_results: list[SignalResult] = []
            contributions = []

            for sig_id, weight in weights.items():
                score = signal_scores.get(sig_id)
                if score is not None and available_weight_sum > 0:
                    eff_weight = weight / available_weight_sum
                    contrib = round(eff_weight * score, 1)
                    sig_status = SignalStatus.OK
                    if sig_id in ["competition_density", "transit_access", "complementary_mix", "road_accessibility"]:
                        prov = ProvenanceClass.MEASURED
                    elif sig_id == "rent_efficiency":
                        prov = ProvenanceClass.HEURISTIC
                    else:
                        prov = ProvenanceClass.ESTIMATED
                    
                    signal_results.append(SignalResult(
                        signal_id=sig_id,
                        score=score,
                        weight=weight,
                        effective_weight=round(eff_weight, 4),
                        contribution=contrib,
                        status=sig_status,
                        provenance=prov,
                        evidence_ids=[f"ev_{cell_id}_{sig_id}"]
                    ))
                    contributions.append(contrib)
                else:
                    signal_results.append(SignalResult(
                        signal_id=sig_id,
                        score=None,
                        weight=weight,
                        effective_weight=0.0,
                        contribution=0.0,
                        status=SignalStatus.UNAVAILABLE,
                        provenance=ProvenanceClass.UNAVAILABLE,
                        evidence_ids=[]
                    ))

            overall_score = round(sum(contributions), 1)
            coverage = round(available_weight_sum, 2)
            confidence = (
                ConfidenceLevel.HIGH if coverage >= 0.9
                else (ConfidenceLevel.MEDIUM if coverage >= 0.7 else ConfidenceLevel.LOW)
            )

            # Strengths: top 2 contributing signals with score >= 60
            scored = sorted([s for s in signal_results if s.score is not None], key=lambda s: s.contribution, reverse=True)
            strengths = [
                f"Strong {s.signal_id.replace('_', ' ')} (score: {s.score:.1f}, contrib: {s.contribution:.1f} pts)"
                for s in scored if s.score >= 60.0
            ][:2]

            # Limitations: signals with score <= 35 or unavailable
            limitations = []
            for s in signal_results:
                if s.status == SignalStatus.UNAVAILABLE:
                    limitations.append(f"{s.signal_id.replace('_', ' ')} data unavailable; weights renormalised.")
                elif s.score is not None and s.score <= 35.0:
                    limitations.append(f"Subdued {s.signal_id.replace('_', ' ')} (score: {s.score:.1f}).")

            locations.append(LocationResult(
                location_id=cell_id,
                rank=0,  # assigned after deterministic sort
                display_name=cell["display_name"],
                centroid=Centroid(lat=cell["centroid"]["lat"], lng=cell["centroid"]["lng"]),
                polygon=cell["polygon"],
                overall_score=overall_score,
                confidence=confidence,
                coverage=coverage,
                signals=signal_results,
                strengths=strengths,
                limitations=limitations,
                why_vs_neighbours=[]
            ))

        # 4. Deterministic tie-breaking sort: (-overall_score, -coverage, location_id asc)
        locations.sort(key=lambda l: (-l.overall_score, -l.coverage, l.location_id))

        # Assign ranks
        for i, loc in enumerate(locations):
            loc.rank = i + 1

        # Populate why_vs_neighbours comparing with adjacent ranks
        for i, loc in enumerate(locations):
            if i > 0:
                prev_loc = locations[i - 1]
                # Find biggest gap
                gap_signals = []
                for s_curr in loc.signals:
                    s_prev = next((s for s in prev_loc.signals if s.signal_id == s_curr.signal_id), None)
                    if s_curr.score is not None and s_prev and s_prev.score is not None:
                        diff = s_prev.contribution - s_curr.contribution
                        gap_signals.append((s_curr.signal_id, diff))
                gap_signals.sort(key=lambda x: x[1], reverse=True)
                if gap_signals:
                    top_lead = gap_signals[0]
                    loc.why_vs_neighbours.append(
                        f"Ranks behind #{prev_loc.rank} ({prev_loc.display_name}) primarily due to {top_lead[0].replace('_', ' ')} (-{abs(top_lead[1]):.1f} weighted pts)."
                    )
            if i < len(locations) - 1:
                next_loc = locations[i + 1]
                advantage_signals = []
                for s_curr in loc.signals:
                    s_next = next((s for s in next_loc.signals if s.signal_id == s_curr.signal_id), None)
                    if s_curr.score is not None and s_next and s_next.score is not None:
                        diff = s_curr.contribution - s_next.contribution
                        advantage_signals.append((s_curr.signal_id, diff))
                advantage_signals.sort(key=lambda x: x[1], reverse=True)
                if advantage_signals:
                    top_adv = advantage_signals[0]
                    loc.why_vs_neighbours.append(
                        f"Outperforms #{next_loc.rank} ({next_loc.display_name}) on {top_adv[0].replace('_', ' ')} (+{top_adv[1]:.1f} weighted pts)."
                    )

        return locations[:top_n], weights


scoring_engine = ScoringEngine()
