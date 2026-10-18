import base64
import json
import time
import uuid

from fastapi import APIRouter, HTTPException, status

from ..agents.orchestrator import orchestrator
from ..agents.scoring_agent import scoring_agent
from ..config import settings
from ..data.loader import loader
from ..schemas import (
    AnalysisInputs,
    AnalysisRequest,
    AnalysisResult,
    CompareRequest,
    CompareResult,
    DatasetMeta,
    GeoJSONFeature,
    GeoJSONFeatureCollection,
    GeoJSONPolygonGeometry,
    ReportResponse,
    WeightAdjustment,
)
from ..scoring.engine import scoring_engine
from ..scoring.explain import build_comparison_deltas, build_evidence_for_locations

router = APIRouter(prefix="/api/v1/analyses", tags=["Analyses"])

# In-memory LRU cache of computed analyses
_ANALYSIS_CACHE: dict[str, AnalysisResult] = {}


def encode_analysis_id(inputs: AnalysisInputs) -> str:
    raw = inputs.model_dump_json()
    return base64.urlsafe_b64encode(raw.encode("utf-8")).decode("utf-8").rstrip("=")


def decode_analysis_id(analysis_id: str) -> AnalysisInputs:
    try:
        padding = "=" * (4 - (len(analysis_id) % 4)) if len(analysis_id) % 4 != 0 else ""
        raw = base64.urlsafe_b64decode(analysis_id + padding).decode("utf-8")
        data = json.loads(raw)
        return AnalysisInputs.model_validate(data)
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid analysis_id token: {e!s}"
        )


def compute_analysis(inputs: AnalysisInputs) -> AnalysisResult:
    cache_key = encode_analysis_id(inputs)
    if cache_key in _ANALYSIS_CACHE:
        cached = _ANALYSIS_CACHE[cache_key]
        # Still log a hand-off so the trace honestly reflects what happened
        # on *this* request: a cache hit, not a silent re-run of the swarm.
        trace_id = str(uuid.uuid4())
        orchestrator.dispatch(trace_id, "orchestrator", "scoring", {"step": "cache_hit", "analysis_id": cache_key})
        return cached.model_copy(update={"trace_id": trace_id, "compute_latency_ms": 0, "was_cached": True})

    trace_id = str(uuid.uuid4())
    start_time = time.time()

    snapshot = loader.get_snapshot(inputs.city_id)
    cells = snapshot.get("cells", {})

    orchestrator.dispatch(
        trace_id, "orchestrator", "scoring",
        {"step": "score_cells", "category_id": inputs.category_id, "budget_tier": inputs.budget_tier, "cell_count": len(cells)},
    )

    locations, weights = scoring_agent.score(
        city_id=inputs.city_id,
        category_id=inputs.category_id,
        budget_tier=inputs.budget_tier,
        weight_overrides=inputs.weight_overrides,
        top_n=inputs.top_n,
        target_customers=inputs.target_customers,
        category_answers=inputs.category_answers,
    )

    orchestrator.dispatch(
        trace_id, "scoring", "orchestrator",
        {"step": "ranked", "locations_returned": len(locations)},
    )

    evidence = build_evidence_for_locations(locations, cells, inputs.category_id)
    weight_adjustments = [
        WeightAdjustment(**entry)
        for entry in scoring_engine.compute_answer_multiplier_breakdown(
            inputs.category_id, inputs.target_customers, inputs.category_answers
        )
    ]
    compute_latency_ms = int((time.time() - start_time) * 1000)

    # Build heatmap features
    features = []
    for loc in locations:
        geo_poly = [[[p[1], p[0]] for p in loc.polygon + [loc.polygon[0]]]]
        features.append(GeoJSONFeature(
            type="Feature",
            geometry=GeoJSONPolygonGeometry(coordinates=geo_poly),
            properties={
                "location_id": loc.location_id,
                "display_name": loc.display_name,
                "rank": loc.rank,
                "overall_score": loc.overall_score,
            }
        ))

    dataset = DatasetMeta(
        id=snapshot.get("dataset_id", "blr-osm-snapshot"),
        mode=settings.DATA_MODE,
        as_of=snapshot.get("as_of", "2026-10"),
        attribution=snapshot.get("attribution", "© OpenStreetMap contributors (ODbL)"),
        contains_simulated=snapshot.get("is_synthetic", False) or settings.DATA_MODE == "synthetic"
    )

    result = AnalysisResult(
        analysis_id=cache_key,
        inputs=inputs,
        dataset=dataset,
        weights=weights,
        locations=locations,
        heatmap=GeoJSONFeatureCollection(features=features),
        evidence=evidence,
        trace_id=trace_id,
        compute_latency_ms=compute_latency_ms,
        cells_considered=snapshot.get("cell_count", len(cells)),
        eligible_cells_considered=snapshot.get("eligible_cell_count", len(cells)),
        was_cached=False,
        weight_adjustments=weight_adjustments,
    )

    # Limit cache to 100 entries
    if len(_ANALYSIS_CACHE) > 100:
        _ANALYSIS_CACHE.pop(next(iter(_ANALYSIS_CACHE)))
    _ANALYSIS_CACHE[cache_key] = result
    return result


@router.post("", response_model=AnalysisResult)
async def create_analysis(request: AnalysisRequest):
    inputs = AnalysisInputs(
        city_id=request.city_id,
        category_id=request.category_id,
        budget_tier=request.budget_tier,
        top_n=request.top_n,
        weight_overrides=request.weight_overrides,
        target_customers=request.target_customers,
        category_answers=request.category_answers,
        shop_size_sqft=request.shop_size_sqft,
        opening_hours=request.opening_hours,
    )
    return compute_analysis(inputs)


@router.get("/{analysis_id}", response_model=AnalysisResult)
async def get_analysis(analysis_id: str):
    inputs = decode_analysis_id(analysis_id)
    return compute_analysis(inputs)


@router.get("/{analysis_id}/locations/{location_id}", response_model=ReportResponse)
async def get_location_report(analysis_id: str, location_id: str):
    analysis = compute_analysis(decode_analysis_id(analysis_id))
    loc = next((l for l in analysis.locations if l.location_id == location_id), None)
    if not loc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location {location_id} not found in this analysis"
        )

    loc_evidence = [e for e in analysis.evidence if e.location_id == location_id]
    return ReportResponse(
        analysis_id=analysis_id,
        location=loc,
        evidence=loc_evidence,
        dataset=analysis.dataset
    )


@router.post("/{analysis_id}/compare", response_model=CompareResult)
async def compare_locations(analysis_id: str, request: CompareRequest):
    analysis = compute_analysis(decode_analysis_id(analysis_id))
    loc_map = {l.location_id: l for l in analysis.locations}
    
    selected_locs = []
    for lid in request.location_ids:
        if lid in loc_map:
            selected_locs.append(loc_map[lid])
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Location {lid} not found in this analysis"
            )

    deltas = build_comparison_deltas(selected_locs)
    compare_evidence = [e for e in analysis.evidence if e.location_id in request.location_ids]

    return CompareResult(
        analysis_id=analysis_id,
        locations=selected_locs,
        signal_deltas=deltas,
        evidence=compare_evidence
    )
