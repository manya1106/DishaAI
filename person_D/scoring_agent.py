"""
scoring_agent.py — Phase 2 Scoring Agent wrapper (Person D).
Wraps scoring engine and DB loader behind an autonomous agent interface.
Returns typed scoring results and grounded evidence bundles.
"""

import sys
from pathlib import Path
from typing import Any

person_d_dir = Path(__file__).resolve().parent
repo_root = person_d_dir.parent
for p in [str(person_d_dir), str(repo_root), str(repo_root / "apps/api")]:
    if p not in sys.path:
        sys.path.insert(0, p)

from app.ai.evidence import build_evidence_bundle
from app.schemas import (
    AnalysisInputs,
    AnalysisResult,
    DatasetMeta,
    GeoJSONFeature,
    GeoJSONFeatureCollection,
    GeoJSONPolygonGeometry,
)
from app.scoring.engine import scoring_engine
from app.scoring.explain import build_evidence_for_locations

from person_D.loader import db_loader


class ScoringAgent:
    """
    Autonomous Scoring Agent:
    - Purely deterministic; no LLM interaction or hallucination.
    - Loads geospatial features from PostgreSQL/PostGIS (or snapshot fallback).
    - Computes 9-signal percentile normalisation, tie-breaking, and ranking.
    - Builds grounded evidence bundles for the Narrator and Verifier agents.
    """

    def __init__(self):
        self.engine = scoring_engine
        self.loader = db_loader

    def handle(self, message_payload: dict[str, Any]) -> dict[str, Any]:
        """
        Handles incoming agent request payload.
        Expected keys in message_payload:
            - city_id: str (default 'blr')
            - category_id: str (e.g. 'cafe')
            - budget_tier: str (e.g. 'medium')
            - weight_overrides: dict[str, float] | None
            - top_n: int (default 10)
            - selected_location_ids: list[str] | None
        """
        city_id = message_payload.get("city_id", "blr")
        category_id = message_payload.get("category_id", "cafe")
        budget_tier = message_payload.get("budget_tier", "medium")
        weight_overrides = message_payload.get("weight_overrides")
        top_n = message_payload.get("top_n", 10)
        selected_location_ids = message_payload.get("selected_location_ids", [])

        # Load cells from DB-backed loader
        snapshot = self.loader.get_snapshot(city_id)
        cells = snapshot.get("cells", {})

        # Compute deterministic scores
        locations, effective_weights = self.engine.score_cells(
            cells=cells,
            category_id=category_id,
            budget_tier=budget_tier,
            weight_overrides=weight_overrides,
            top_n=top_n,
        )

        evidence = build_evidence_for_locations(locations, cells, category_id)

        # Build heatmap features
        features = []
        for loc in locations:
            geo_poly = [[[p[1], p[0]] for p in loc.polygon + [loc.polygon[0]]]] if loc.polygon else []
            features.append(
                GeoJSONFeature(
                    type="Feature",
                    geometry=GeoJSONPolygonGeometry(coordinates=geo_poly),
                    properties={
                        "location_id": loc.location_id,
                        "display_name": loc.display_name,
                        "rank": loc.rank,
                        "overall_score": loc.overall_score,
                    },
                )
            )

        dataset = DatasetMeta(
            id=snapshot.get("dataset_id", "blr-postgis"),
            mode="database",
            as_of=snapshot.get("as_of", "2026-10"),
            attribution=snapshot.get("attribution", "© OpenStreetMap contributors (PostGIS)"),
            contains_simulated=snapshot.get("is_synthetic", False),
        )

        analysis_inputs = AnalysisInputs(
            city_id=city_id,
            category_id=category_id,
            budget_tier=budget_tier,
            weight_overrides=weight_overrides or {},
            top_n=top_n,
        )

        analysis = AnalysisResult(
            analysis_id=f"analysis_{city_id}_{category_id}_{budget_tier}",
            inputs=analysis_inputs,
            dataset=dataset,
            weights=effective_weights,
            locations=locations,
            heatmap=GeoJSONFeatureCollection(features=features),
            evidence=evidence,
        )

        # Build grounded evidence bundle
        evidence_bundle = build_evidence_bundle(analysis, selected_location_ids)

        return {
            "status": "success",
            "city_id": city_id,
            "category_id": category_id,
            "budget_tier": budget_tier,
            "top_locations": [loc.model_dump() for loc in locations],
            "weights": effective_weights,
            "effective_weights": effective_weights,
            "evidence_bundle": evidence_bundle.model_dump(),
        }


scoring_agent = ScoringAgent()
