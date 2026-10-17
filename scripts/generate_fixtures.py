#!/usr/bin/env python3
import json
import base64
import sys
from pathlib import Path

# Add apps/api to path
root_dir = Path(__file__).resolve().parent.parent
api_dir = root_dir / "apps" / "api"
sys.path.insert(0, str(api_dir))

import h3
from app.schemas import (
    ProvenanceClass,
    SignalStatus,
    ConfidenceLevel,
    ClaimType,
    ClaimPolarity,
    ChatMode,
    VerificationStatus,
    Centroid,
    GeoJSONFeature,
    GeoJSONFeatureCollection,
    GeoJSONPolygonGeometry,
    DatasetMeta,
    AnalysisInputs,
    SignalResult,
    EvidenceItem,
    LocationResult,
    AnalysisResult,
    ReportResponse,
    CompareResult,
    SignalDelta,
    ChatResponse,
    Block,
    Claim,
    VerificationSummary,
    UncertaintyInfo,
    MetaResponse,
    CityMeta,
    CategoryMeta,
    BudgetTierMeta,
    SignalMeta,
)

fixtures_dir = root_dir / "contracts" / "fixtures"
fixtures_dir.mkdir(parents=True, exist_ok=True)

# 10 Key Bengaluru locations with realistic coordinates
SAMPLE_ZONES = [
    {"name": "Indiranagar 100ft Rd Corridor", "lat": 12.9784, "lng": 77.6408, "tier": 5},
    {"name": "Koramangala 5th Block Hub", "lat": 12.9352, "lng": 77.6245, "tier": 5},
    {"name": "HSR Layout Sector 1 Commercial", "lat": 12.9116, "lng": 77.6389, "tier": 4},
    {"name": "Jayanagar 4th Block Market", "lat": 12.9299, "lng": 77.5833, "tier": 4},
    {"name": "Whitefield ITPL Main Rd", "lat": 12.9863, "lng": 77.7345, "tier": 4},
    {"name": "Church Street / MG Road", "lat": 12.9749, "lng": 77.6074, "tier": 5},
    {"name": "BTM Layout 2nd Stage Udupi Garden", "lat": 12.9166, "lng": 77.6101, "tier": 3},
    {"name": "Malleshwaram 8th Cross", "lat": 12.9982, "lng": 77.5714, "tier": 3},
    {"name": "Bellandur Outer Ring Road Tech Park", "lat": 12.9304, "lng": 77.6784, "tier": 4},
    {"name": "Kalyan Nagar HRBR Layout", "lat": 13.0189, "lng": 77.6450, "tier": 3},
]

CAFE_WEIGHTS = {
    "competition_density": 0.12,
    "gap_opportunity": 0.12,
    "footfall_anchors": 0.16,
    "transit_access": 0.10,
    "complementary_mix": 0.10,
    "residential_catchment": 0.08,
    "daytime_population": 0.14,
    "road_accessibility": 0.06,
    "rent_efficiency": 0.12,
}

def generate_fixtures():
    # Build inputs
    inputs = AnalysisInputs(
        city_id="blr",
        category_id="cafe",
        budget_tier="medium",
        top_n=10
    )
    analysis_id_str = base64.urlsafe_b64encode(inputs.model_dump_json().encode()).decode().rstrip("=")

    dataset = DatasetMeta(
        id="blr-osm-snapshot",
        mode="snapshot",
        as_of="2026-10",
        attribution="© OpenStreetMap contributors (ODbL)",
        contains_simulated=True
    )

    locations = []
    all_evidence = []
    features = []
    ev_counter = 1

    # Base raw metrics profile for the 10 zones
    raw_profiles = [
        # comp, gap, footfall, transit, comp_mix, res, daytime, road, rent_tier
        [18, 3.4, 88, 75, 42, 60, 92, 80, 5], # Indiranagar
        [22, 2.8, 92, 70, 48, 55, 90, 78, 5], # Koramangala
        [12, 4.1, 78, 65, 35, 75, 82, 85, 4], # HSR
        [10, 4.5, 72, 80, 30, 85, 70, 72, 4], # Jayanagar
        [14, 3.2, 85, 60, 28, 65, 95, 68, 4], # Whitefield
        [25, 2.2, 95, 90, 55, 40, 96, 75, 5], # Church St
        [9,  4.8, 65, 72, 25, 80, 68, 70, 3], # BTM (affordable)
        [8,  4.2, 68, 74, 28, 88, 62, 65, 3], # Malleshwaram
        [16, 3.0, 80, 55, 32, 50, 94, 60, 4], # Bellandur
        [7,  4.6, 60, 65, 22, 78, 60, 68, 3], # Kalyan Nagar
    ]

    for idx, (zone, raw) in enumerate(zip(SAMPLE_ZONES, raw_profiles)):
        rank = idx + 1
        h3_cell = h3.latlng_to_cell(zone["lat"], zone["lng"], 8)
        boundary = h3.cell_to_boundary(h3_cell)
        polygon = [[b[0], b[1]] for b in boundary]
        
        # Signals calculation
        # Location #10 has rent_efficiency unavailable to satisfy prompt requirement
        signals = []
        loc_ev_ids = []

        is_rent_unavailable = (rank == 10)
        
        available_weight_sum = sum(
            w for sid, w in CAFE_WEIGHTS.items() if not (is_rent_unavailable and sid == "rent_efficiency")
        )

        for sig_id, weight in CAFE_WEIGHTS.items():
            ev_id = f"ev_{ev_counter:04d}"
            ev_counter += 1

            if is_rent_unavailable and sig_id == "rent_efficiency":
                sig_res = SignalResult(
                    signal_id=sig_id,
                    score=None,
                    weight=weight,
                    effective_weight=0.0,
                    contribution=0.0,
                    status=SignalStatus.UNAVAILABLE,
                    provenance=ProvenanceClass.UNAVAILABLE,
                    evidence_ids=[]
                )
                signals.append(sig_res)
                continue

            eff_weight = weight / available_weight_sum
            
            # Realistic normalized score
            if sig_id == "competition_density":
                score = round(max(10.0, 100.0 - raw[0] * 3.5), 1)
                ev_kind = "count"
                ev_val = raw[0]
                ev_unit = "competitor POIs"
                prov = ProvenanceClass.MEASURED
            elif sig_id == "gap_opportunity":
                score = round(min(98.0, raw[1] * 20.0), 1)
                ev_kind = "metric"
                ev_val = raw[1]
                ev_unit = "demand/supply ratio"
                prov = ProvenanceClass.ESTIMATED
            elif sig_id == "footfall_anchors":
                score = float(raw[2])
                ev_kind = "count"
                ev_val = round(raw[2] / 4)
                ev_unit = "major anchors"
                prov = ProvenanceClass.ESTIMATED
            elif sig_id == "transit_access":
                score = float(raw[3])
                ev_kind = "count"
                ev_val = round(raw[3] / 6)
                ev_unit = "transit stops"
                prov = ProvenanceClass.MEASURED
            elif sig_id == "complementary_mix":
                score = round(raw[4] * 1.8, 1)
                ev_kind = "count"
                ev_val = raw[4]
                ev_unit = "synergy businesses"
                prov = ProvenanceClass.MEASURED
            elif sig_id == "residential_catchment":
                score = float(raw[5])
                ev_kind = "count"
                ev_val = raw[5] * 15
                ev_unit = "residential units proxy"
                prov = ProvenanceClass.ESTIMATED
            elif sig_id == "daytime_population":
                score = float(raw[6])
                ev_kind = "count"
                ev_val = raw[6] * 10
                ev_unit = "workplace entities"
                prov = ProvenanceClass.ESTIMATED
            elif sig_id == "road_accessibility":
                score = float(raw[7])
                ev_kind = "metric"
                ev_val = round(raw[7] * 0.12, 1)
                ev_unit = "km road network"
                prov = ProvenanceClass.MEASURED
            elif sig_id == "rent_efficiency":
                # Ceiling for medium is 3
                area_tier = zone["tier"]
                ceiling = 3
                if area_tier <= ceiling - 1:
                    score = 100.0
                elif area_tier == ceiling:
                    score = 70.0
                else:
                    score = max(0.0, 70.0 - 30.0 * (area_tier - ceiling))
                ev_kind = "heuristic"
                ev_val = f"Tier {area_tier}/5"
                ev_unit = "rent tier"
                prov = ProvenanceClass.HEURISTIC
            
            contrib = round(eff_weight * score, 1)
            sig_res = SignalResult(
                signal_id=sig_id,
                score=score,
                weight=weight,
                effective_weight=round(eff_weight, 4),
                contribution=contrib,
                status=SignalStatus.OK,
                provenance=prov,
                evidence_ids=[ev_id]
            )
            signals.append(sig_res)

            ev_item = EvidenceItem(
                evidence_id=ev_id,
                location_id=h3_cell,
                signal_id=sig_id,
                kind=ev_kind,
                label=f"{sig_id.replace('_', ' ').title()} in neighbourhood",
                value=ev_val,
                unit=ev_unit,
                provenance=prov,
                source="OpenStreetMap snapshot / heuristics" if prov != ProvenanceClass.HEURISTIC else "Team-assigned rent tiers",
                as_of="2026-10"
            )
            all_evidence.append(ev_item)

        overall_score = round(sum(s.contribution for s in signals), 1)
        coverage = round(sum(s.weight for s in signals if s.status != SignalStatus.UNAVAILABLE), 2)
        confidence = ConfidenceLevel.HIGH if coverage >= 0.9 else (ConfidenceLevel.MEDIUM if coverage >= 0.7 else ConfidenceLevel.LOW)

        # Strengths: top 2 signals with score >= 60
        scored_signals = sorted([s for s in signals if s.score is not None], key=lambda s: s.contribution, reverse=True)
        strengths = [
            f"Strong {s.signal_id.replace('_', ' ')} (score: {s.score:.1f})"
            for s in scored_signals if s.score >= 60.0
        ][:2]
        
        limitations = []
        for s in signals:
            if s.status == SignalStatus.UNAVAILABLE:
                limitations.append(f"{s.signal_id.replace('_', ' ')} data unavailable; weight renormalised.")
            elif s.score is not None and s.score <= 40.0:
                limitations.append(f"Subdued {s.signal_id.replace('_', ' ')} (score: {s.score:.1f}).")

        why_vs_neighbours = [
            f"Outperforms adjacent zones on {scored_signals[0].signal_id.replace('_', ' ')} by {scored_signals[0].contribution:.1f} weighted pts."
        ]

        loc = LocationResult(
            location_id=h3_cell,
            rank=rank,
            display_name=zone["name"],
            centroid=Centroid(lat=zone["lat"], lng=zone["lng"]),
            polygon=polygon,
            overall_score=overall_score,
            confidence=confidence,
            coverage=coverage,
            signals=signals,
            strengths=strengths,
            limitations=limitations,
            why_vs_neighbours=why_vs_neighbours
        )
        locations.append(loc)

        # GeoJSON feature
        # GeoJSON coordinates format is [lng, lat]
        geo_poly = [[[p[1], p[0]] for p in polygon + [polygon[0]]]]
        feat = GeoJSONFeature(
            type="Feature",
            geometry=GeoJSONPolygonGeometry(coordinates=geo_poly),
            properties={
                "location_id": h3_cell,
                "display_name": zone["name"],
                "rank": rank,
                "overall_score": overall_score,
            }
        )
        features.append(feat)

    # Sort locations by overall_score desc, coverage desc, location_id asc
    locations.sort(key=lambda l: (-l.overall_score, -l.coverage, l.location_id))
    for i, loc in enumerate(locations):
        loc.rank = i + 1

    analysis_result = AnalysisResult(
        analysis_id=analysis_id_str,
        inputs=inputs,
        dataset=dataset,
        weights=CAFE_WEIGHTS,
        locations=locations,
        heatmap=GeoJSONFeatureCollection(features=features),
        evidence=all_evidence
    )

    # Save analysis_cafe_medium.json
    with open(fixtures_dir / "analysis_cafe_medium.json", "w", encoding="utf-8") as f:
        f.write(analysis_result.model_dump_json(indent=2))
    print("Wrote analysis_cafe_medium.json")

    # Save report_blr_loc1.json
    loc1 = locations[0]
    loc1_evidence = [e for e in all_evidence if e.location_id == loc1.location_id]
    report = ReportResponse(
        analysis_id=analysis_id_str,
        location=loc1,
        evidence=loc1_evidence,
        dataset=dataset
    )
    with open(fixtures_dir / "report_blr_loc1.json", "w", encoding="utf-8") as f:
        f.write(report.model_dump_json(indent=2))
    print("Wrote report_blr_loc1.json")

    # Save compare_sample.json
    compare_locs = [locations[0], locations[2]]
    deltas = []
    for sig_id in CAFE_WEIGHTS.keys():
        s1 = next((s for s in compare_locs[0].signals if s.signal_id == sig_id), None)
        s2 = next((s for s in compare_locs[1].signals if s.signal_id == sig_id), None)
        scores = {
            compare_locs[0].location_id: s1.score if s1 else None,
            compare_locs[1].location_id: s2.score if s2 else None,
        }
        winner = None
        if s1 and s2 and s1.score is not None and s2.score is not None:
            if s1.score > s2.score:
                winner = compare_locs[0].location_id
                exp = f"{compare_locs[0].display_name} leads by {s1.score - s2.score:.1f} pts."
            elif s2.score > s1.score:
                winner = compare_locs[1].location_id
                exp = f"{compare_locs[1].display_name} leads by {s2.score - s1.score:.1f} pts."
            else:
                exp = "Tied score."
        else:
            exp = "Data incomplete for one or both locations."
        deltas.append(SignalDelta(
            signal_id=sig_id,
            scores=scores,
            winner_location_id=winner,
            delta_explanation=exp
        ))

    compare_res = CompareResult(
        analysis_id=analysis_id_str,
        locations=compare_locs,
        signal_deltas=deltas,
        evidence=[e for e in all_evidence if e.location_id in [l.location_id for l in compare_locs]]
    )
    with open(fixtures_dir / "compare_sample.json", "w", encoding="utf-8") as f:
        f.write(compare_res.model_dump_json(indent=2))
    print("Wrote compare_sample.json")

    # Chat verified
    chat_v = ChatResponse(
        trace_id="4a9b6c21-d102-4c28-94ef-11e298fbb901",
        mode=ChatMode.LLM_VERIFIED,
        verification=VerificationSummary(
            status=VerificationStatus.VERIFIED,
            claims_total=3,
            claims_verified=3,
            claims_removed=0,
            attempts=1
        ),
        blocks=[
            Block(
                text="Indiranagar leads the ranking with an overall score of 78.4.",
                claims=[
                    Claim(
                        claim_id="c1",
                        type=ClaimType.SCORE,
                        location_ids=[loc1.location_id],
                        signal_id=None,
                        polarity=ClaimPolarity.STRENGTH,
                        evidence_ids=[loc1_evidence[0].evidence_id],
                        numbers=[78.4],
                        verified=True
                    )
                ]
            ),
            Block(
                text="The zone benefits from strong daytime population and high footfall anchor density.",
                claims=[
                    Claim(
                        claim_id="c2",
                        type=ClaimType.FACT,
                        location_ids=[loc1.location_id],
                        signal_id="daytime_population",
                        polarity=ClaimPolarity.STRENGTH,
                        evidence_ids=[loc1_evidence[6].evidence_id],
                        numbers=[],
                        verified=True
                    ),
                    Claim(
                        claim_id="c3",
                        type=ClaimType.FACT,
                        location_ids=[loc1.location_id],
                        signal_id="footfall_anchors",
                        polarity=ClaimPolarity.STRENGTH,
                        evidence_ids=[loc1_evidence[2].evidence_id],
                        numbers=[],
                        verified=True
                    )
                ]
            )
        ],
        uncertainty=UncertaintyInfo(insufficient_data=False, missing=[]),
        latency_ms=1450
    )
    with open(fixtures_dir / "chat_verified.json", "w", encoding="utf-8") as f:
        f.write(chat_v.model_dump_json(indent=2))
    print("Wrote chat_verified.json")

    # Chat partially verified
    chat_pv = ChatResponse(
        trace_id="8f12c8b0-a330-41be-9402-ddc9f91a0022",
        mode=ChatMode.LLM_PARTIALLY_VERIFIED,
        verification=VerificationSummary(
            status=VerificationStatus.PARTIALLY_VERIFIED,
            claims_total=3,
            claims_verified=2,
            claims_removed=1,
            attempts=1
        ),
        blocks=[
            Block(
                text="HSR Layout Sector 1 exhibits superior gap opportunity compared to Koramangala.",
                claims=[
                    Claim(
                        claim_id="c1",
                        type=ClaimType.COMPARISON,
                        location_ids=[locations[2].location_id, locations[1].location_id],
                        signal_id="gap_opportunity",
                        polarity=ClaimPolarity.STRENGTH,
                        evidence_ids=[loc1_evidence[1].evidence_id],
                        numbers=[],
                        verified=True
                    )
                ]
            )
        ],
        uncertainty=UncertaintyInfo(insufficient_data=False, missing=["1 unsupported claim removed (unverified rent figure)"]),
        latency_ms=1890
    )
    with open(fixtures_dir / "chat_partially_verified.json", "w", encoding="utf-8") as f:
        f.write(chat_pv.model_dump_json(indent=2))
    print("Wrote chat_partially_verified.json")

    # Chat fallback
    chat_fb = ChatResponse(
        trace_id="b2319f0a-77c8-4721-a189-53e77a164bdf",
        mode=ChatMode.DETERMINISTIC_FALLBACK,
        verification=VerificationSummary(
            status=VerificationStatus.REJECTED_FALLBACK,
            claims_total=2,
            claims_verified=0,
            claims_removed=2,
            attempts=2
        ),
        blocks=[
            Block(
                text="Deterministic explanation: Indiranagar ranks #1 with 78.4 overall score, driven by daytime commercial activity.",
                claims=[
                    Claim(
                        claim_id="c_fallback_1",
                        type=ClaimType.SCORE,
                        location_ids=[loc1.location_id],
                        signal_id=None,
                        polarity=ClaimPolarity.NEUTRAL,
                        evidence_ids=[loc1_evidence[0].evidence_id],
                        numbers=[78.4],
                        verified=True
                    )
                ]
            )
        ],
        uncertainty=UncertaintyInfo(insufficient_data=False, missing=["AI model output failed verification; deterministic narrator activated."]),
        latency_ms=310
    )
    with open(fixtures_dir / "chat_fallback.json", "w", encoding="utf-8") as f:
        f.write(chat_fb.model_dump_json(indent=2))
    print("Wrote chat_fallback.json")

    # Chat refusal (insufficient data trap question)
    chat_ref = ChatResponse(
        trace_id="ec90a12e-1510-45c1-901b-c741005a9643",
        mode=ChatMode.REFUSED_INSUFFICIENT_DATA,
        verification=VerificationSummary(
            status=VerificationStatus.VERIFIED,
            claims_total=0,
            claims_verified=0,
            claims_removed=0,
            attempts=1
        ),
        blocks=[
            Block(
                text="I cannot answer your question about exact monthly rent in rupees because Disha AI does not track or scrape unverified private lease rates.",
                claims=[]
            ),
            Block(
                text="We only maintain a heuristic relative rent tier (Tier 5/5 for Indiranagar) to evaluate relative budget feasibility honestly.",
                claims=[
                    Claim(
                        claim_id="c_ref_1",
                        type=ClaimType.FACT,
                        location_ids=[loc1.location_id],
                        signal_id="rent_efficiency",
                        polarity=ClaimPolarity.NEUTRAL,
                        evidence_ids=[loc1_evidence[8].evidence_id],
                        numbers=[5.0],
                        verified=True
                    )
                ]
            )
        ],
        uncertainty=UncertaintyInfo(
            insufficient_data=True,
            missing=["Exact rupee rent: not tracked in OpenStreetMap or heuristic snapshots"]
        ),
        latency_ms=120
    )
    with open(fixtures_dir / "chat_refusal.json", "w", encoding="utf-8") as f:
        f.write(chat_ref.model_dump_json(indent=2))
    print("Wrote chat_refusal.json")


if __name__ == "__main__":
    generate_fixtures()
