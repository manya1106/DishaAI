from typing import Any

from pydantic import BaseModel, ConfigDict

from ..schemas.analysis import AnalysisResult


class SlimEvidenceItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ev_id: str
    location_id: str
    signal_id: str
    label: str
    value: Any
    unit: str | None = None
    provenance: str


class SlimLocationEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")
    location_id: str
    display_name: str
    rank: int
    overall_score: float
    confidence: str
    signals: dict[str, dict[str, Any]]
    strengths: list[str]
    limitations: list[str]
    why_vs_neighbours: list[str]


class EvidenceBundle(BaseModel):
    model_config = ConfigDict(extra="forbid")
    analysis_id: str
    category_id: str
    budget_tier: str
    selected_locations: list[SlimLocationEvidence]
    evidence_lookup: dict[str, SlimEvidenceItem]
    allowed_numbers: list[float]
    allowed_names: list[str]
    unavailable_signals: list[str]


def build_evidence_bundle(
    analysis: AnalysisResult,
    selected_location_ids: list[str]
) -> EvidenceBundle:
    # If no locations selected, default to top 2 locations
    if not selected_location_ids:
        selected_location_ids = [l.location_id for l in analysis.locations[:2]]

    selected_locs = [l for l in analysis.locations if l.location_id in selected_location_ids]
    if not selected_locs:
        selected_locs = analysis.locations[:2]

    evidence_lookup: dict[str, SlimEvidenceItem] = {}
    allowed_numbers: list[float] = []
    allowed_names: list[str] = []
    unavailable_signals: list[str] = []

    # Map raw evidence items
    ev_map = {e.evidence_id: e for e in analysis.evidence}

    alias_counter = 1
    ev_id_mapping = {}

    slim_locations = []
    for loc in selected_locs:
        allowed_names.append(loc.display_name.lower())
        allowed_numbers.append(float(loc.rank))
        allowed_numbers.append(float(loc.overall_score))

        sig_dict = {}
        for s in loc.signals:
            if s.score is not None:
                allowed_numbers.append(float(s.score))
                allowed_numbers.append(float(s.contribution))
            else:
                unavailable_signals.append(f"{loc.display_name}: {s.signal_id}")

            # Assign short alias for each evidence item
            loc_aliases = []
            for raw_ev_id in s.evidence_ids:
                if raw_ev_id in ev_map:
                    item = ev_map[raw_ev_id]
                    if raw_ev_id not in ev_id_mapping:
                        alias = f"ev_{alias_counter:03d}"
                        alias_counter += 1
                        ev_id_mapping[raw_ev_id] = alias
                        
                        # Add numeric value if float/int
                        if isinstance(item.value, (int, float)):
                            allowed_numbers.append(float(item.value))
                        
                        evidence_lookup[alias] = SlimEvidenceItem(
                            ev_id=alias,
                            location_id=item.location_id,
                            signal_id=item.signal_id,
                            label=item.label,
                            value=item.value,
                            unit=item.unit,
                            provenance=item.provenance.value if hasattr(item.provenance, "value") else str(item.provenance)
                        )
                    loc_aliases.append(ev_id_mapping[raw_ev_id])

            sig_dict[s.signal_id] = {
                "score": s.score,
                "weight": s.weight,
                "effective_weight": s.effective_weight,
                "contribution": s.contribution,
                "provenance": s.provenance.value if hasattr(s.provenance, "value") else str(s.provenance),
                "evidence_ids": loc_aliases
            }

        slim_locations.append(SlimLocationEvidence(
            location_id=loc.location_id,
            display_name=loc.display_name,
            rank=loc.rank,
            overall_score=loc.overall_score,
            confidence=loc.confidence.value if hasattr(loc.confidence, "value") else str(loc.confidence),
            signals=sig_dict,
            strengths=loc.strengths,
            limitations=loc.limitations,
            why_vs_neighbours=loc.why_vs_neighbours
        ))

    # Also allow all ranked location names in context
    for l in analysis.locations:
        allowed_names.append(l.display_name.lower())

    return EvidenceBundle(
        analysis_id=analysis.analysis_id,
        category_id=analysis.inputs.category_id,
        budget_tier=analysis.inputs.budget_tier,
        selected_locations=slim_locations,
        evidence_lookup=evidence_lookup,
        allowed_numbers=list(set(allowed_numbers)),
        allowed_names=list(set(allowed_names)),
        unavailable_signals=list(set(unavailable_signals))
    )
