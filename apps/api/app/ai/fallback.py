from ..schemas.chat import LLMBlock, LLMClaim, LLMOutput
from ..schemas.enums import ClaimPolarity, ClaimType
from .evidence import EvidenceBundle


def classify_intent(message: str) -> str:
    m = message.lower()
    if any(k in m for k in ["compare", "versus", "vs", "difference", "ahead of", "better than"]):
        return "compare"
    if any(k in m for k in ["why", "reason", "rank", "lead", "top"]):
        return "why_ranked"
    if any(k in m for k in ["strength", "advantage", "benefit", "good"]):
        return "strengths"
    if any(k in m for k in ["limitation", "weakness", "drawback", "risk", "con"]):
        return "limitations"
    if any(k in m for k in ["missing", "data", "gap", "source", "provenance", "unavailable"]):
        return "data_gaps"
    return "general_summary"


class DeterministicNarrator:
    def narrate(self, message: str, bundle: EvidenceBundle) -> LLMOutput:
        intent = classify_intent(message)
        locs = bundle.selected_locations
        if not locs:
            return LLMOutput(
                blocks=[LLMBlock(
                    text="No locations were selected for analysis in this zone.",
                    claims=[]
                )]
            )

        loc1 = locs[0]
        # Find first valid evidence ID for loc1
        loc1_ev_ids = []
        for s in loc1.signals.values():
            loc1_ev_ids.extend(s.get("evidence_ids", []))
        default_ev_id = loc1_ev_ids[0] if loc1_ev_ids else next(iter(bundle.evidence_lookup.keys()))

        blocks: list[LLMBlock] = []

        if intent == "compare" and len(locs) >= 2:
            loc2 = locs[1]
            round(loc1.overall_score - loc2.overall_score, 1)
            
            # Find signal with biggest delta
            lead_sig = None
            max_lead = -999.0
            for sid, s1 in loc1.signals.items():
                s2 = loc2.signals.get(sid, {})
                sc1 = s1.get("score")
                sc2 = s2.get("score")
                if sc1 is not None and sc2 is not None:
                    d = sc1 - sc2
                    if d > max_lead:
                        max_lead = d
                        lead_sig = sid

            sig_name = lead_sig.replace("_", " ") if lead_sig else "key location signals"
            sig_ev_ids = loc1.signals.get(lead_sig, {}).get("evidence_ids", [default_ev_id]) if lead_sig else [default_ev_id]

            blocks.append(LLMBlock(
                text=f"{loc1.display_name} ranks #{loc1.rank} with an overall score of {loc1.overall_score}.",
                claims=[LLMClaim(
                    type=ClaimType.SCORE,
                    location_ids=[loc1.location_id],
                    polarity=ClaimPolarity.STRENGTH,
                    evidence_ids=[default_ev_id],
                    numbers=[float(loc1.rank), float(loc1.overall_score)]
                )]
            ))
            blocks.append(LLMBlock(
                text=f"{loc1.display_name} outperforms {loc2.display_name} primarily on {sig_name}.",
                claims=[LLMClaim(
                    type=ClaimType.COMPARISON,
                    location_ids=[loc1.location_id, loc2.location_id],
                    signal_id=lead_sig,
                    polarity=ClaimPolarity.STRENGTH,
                    evidence_ids=sig_ev_ids,
                    numbers=[]
                )]
            ))

        elif intent == "strengths":
            scored = sorted(
                [(sid, s) for sid, s in loc1.signals.items() if s.get("score") is not None],
                key=lambda x: x[1].get("contribution", 0),
                reverse=True
            )
            top_sig = scored[0] if scored else None
            if top_sig:
                sid, s_data = top_sig
                evs = s_data.get("evidence_ids", [default_ev_id])
                blocks.append(LLMBlock(
                    text=f"The primary strength for {loc1.display_name} is {sid.replace('_', ' ')} with a relative score of {s_data['score']}.",
                    claims=[LLMClaim(
                        type=ClaimType.FACT,
                        location_ids=[loc1.location_id],
                        signal_id=sid,
                        polarity=ClaimPolarity.STRENGTH,
                        evidence_ids=evs,
                        numbers=[float(s_data['score'])]
                    )]
                ))
            else:
                blocks.append(LLMBlock(
                    text=f"{loc1.display_name} currently has no standout high-scoring strengths.",
                    claims=[LLMClaim(
                        type=ClaimType.FACT,
                        location_ids=[loc1.location_id],
                        evidence_ids=[default_ev_id]
                    )]
                ))

        elif intent == "limitations":
            low_scored = [
                (sid, s) for sid, s in loc1.signals.items()
                if s.get("score") is not None and s.get("score") <= 35.0
            ]
            if low_scored:
                sid, s_data = low_scored[0]
                evs = s_data.get("evidence_ids", [default_ev_id])
                blocks.append(LLMBlock(
                    text=f"A notable limitation for {loc1.display_name} is {sid.replace('_', ' ')} with a subdued score of {s_data['score']}.",
                    claims=[LLMClaim(
                        type=ClaimType.FACT,
                        location_ids=[loc1.location_id],
                        signal_id=sid,
                        polarity=ClaimPolarity.WEAKNESS,
                        evidence_ids=evs,
                        numbers=[float(s_data['score'])]
                    )]
                ))
            else:
                blocks.append(LLMBlock(
                    text=f"{loc1.display_name} maintains balanced signal distribution with no severe limitations below threshold.",
                    claims=[LLMClaim(
                        type=ClaimType.FACT,
                        location_ids=[loc1.location_id],
                        evidence_ids=[default_ev_id]
                    )]
                ))

        elif intent == "data_gaps":
            if bundle.unavailable_signals:
                unavail = bundle.unavailable_signals[0]
                blocks.append(LLMBlock(
                    text=f"Data coverage observation: {unavail} is currently unavailable and weights were renormalised.",
                    claims=[LLMClaim(
                        type=ClaimType.FACT,
                        location_ids=[loc1.location_id],
                        evidence_ids=[default_ev_id]
                    )]
                ))
            else:
                blocks.append(LLMBlock(
                    text=f"All nine location intelligence signals are populated for {loc1.display_name} with {loc1.confidence} confidence.",
                    claims=[LLMClaim(
                        type=ClaimType.FACT,
                        location_ids=[loc1.location_id],
                        evidence_ids=[default_ev_id]
                    )]
                ))

        else:  # why_ranked or general summary
            blocks.append(LLMBlock(
                text=f"{loc1.display_name} ranks #{loc1.rank} overall with a verified score of {loc1.overall_score}.",
                claims=[LLMClaim(
                    type=ClaimType.SCORE,
                    location_ids=[loc1.location_id],
                    polarity=ClaimPolarity.STRENGTH,
                    evidence_ids=[default_ev_id],
                    numbers=[float(loc1.rank), float(loc1.overall_score)]
                )]
            ))
            scored = sorted(
                [(sid, s) for sid, s in loc1.signals.items() if s.get("score") is not None],
                key=lambda x: x[1].get("contribution", 0),
                reverse=True
            )
            if scored:
                top_sid, top_s = scored[0]
                top_evs = top_s.get("evidence_ids", [default_ev_id])
                blocks.append(LLMBlock(
                    text=f"{loc1.display_name} performs strongly on {top_sid.replace('_', ' ')} with a score of {top_s['score']}.",
                    claims=[LLMClaim(
                        type=ClaimType.FACT,
                        location_ids=[loc1.location_id],
                        signal_id=top_sid,
                        polarity=ClaimPolarity.STRENGTH,
                        evidence_ids=top_evs,
                        numbers=[float(top_s['score'])]
                    )]
                ))

        return LLMOutput(blocks=blocks)


deterministic_narrator = DeterministicNarrator()
