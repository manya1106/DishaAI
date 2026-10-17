from typing import Any

from pydantic import Field

from .common import BaseSchema, Centroid, GeoJSONFeatureCollection
from .enums import ConfidenceLevel, ProvenanceClass, SignalStatus
from .meta import DatasetMeta


class AnalysisRequest(BaseSchema):
    city_id: str = Field("blr", description="City identifier")
    category_id: str = Field(..., description="Business category: cafe, pharmacy, or gym")
    budget_tier: str = Field(..., description="Budget tier: low, medium, or high")
    top_n: int = Field(10, ge=1, le=50, description="Number of top ranked zones to return")
    weight_overrides: dict[str, float] | None = Field(None, description="Optional weight overrides")


class AnalysisInputs(BaseSchema):
    city_id: str
    category_id: str
    budget_tier: str
    top_n: int
    weight_overrides: dict[str, float] | None = None


class SignalResult(BaseSchema):
    signal_id: str
    score: float | None = None
    weight: float
    effective_weight: float
    contribution: float
    status: SignalStatus
    provenance: ProvenanceClass
    evidence_ids: list[str]


class EvidenceItem(BaseSchema):
    evidence_id: str
    location_id: str
    signal_id: str
    kind: str  # "count", "metric", "heuristic", "unavailable"
    label: str
    value: Any  # number, string, or boolean
    unit: str | None = None
    provenance: ProvenanceClass
    source: str
    as_of: str


class LocationResult(BaseSchema):
    location_id: str
    rank: int
    display_name: str
    centroid: Centroid
    polygon: list[list[float]]  # list of [lat, lng] boundary vertices
    overall_score: float
    confidence: ConfidenceLevel
    coverage: float
    signals: list[SignalResult]
    strengths: list[str]
    limitations: list[str]
    why_vs_neighbours: list[str]


class AnalysisResult(BaseSchema):
    analysis_id: str
    inputs: AnalysisInputs
    dataset: DatasetMeta
    weights: dict[str, float]
    locations: list[LocationResult]
    heatmap: GeoJSONFeatureCollection
    evidence: list[EvidenceItem]


class ReportResponse(BaseSchema):
    analysis_id: str
    location: LocationResult
    evidence: list[EvidenceItem]
    dataset: DatasetMeta


class CompareRequest(BaseSchema):
    location_ids: list[str] = Field(..., min_length=2, max_length=3)


class SignalDelta(BaseSchema):
    signal_id: str
    scores: dict[str, float | None]  # location_id -> score
    winner_location_id: str | None = None
    delta_explanation: str


class CompareResult(BaseSchema):
    analysis_id: str
    locations: list[LocationResult]
    signal_deltas: list[SignalDelta]
    evidence: list[EvidenceItem]
