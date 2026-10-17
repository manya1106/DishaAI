import base64
import json

from fastapi import APIRouter, HTTPException, status

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
        return _ANALYSIS_CACHE[cache_key]

    snapshot = loader.get_snapshot(inputs.city_id)
    cells = snapshot.get("cells", {})

    locations, weights = scoring_engine.score_cells(
        cells=cells,
        category_id=inputs.category_id,
        budget_tier=inputs.budget_tier,
        weight_overrides=inputs.weight_overrides,
        top_n=inputs.top_n
    )

    evidence = build_evidence_for_locations(locations, cells, inputs.category_id)

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
        evidence=evidence
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
        weight_overrides=request.weight_overrides
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
