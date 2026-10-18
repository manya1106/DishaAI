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
    weight_overrides: dict[str, float] | None = Field(None, description="Optional manual weight overrides")
    target_customers: list[str] = Field(
        default_factory=list,
        description="Wizard answer: who the shop mainly serves (students, young_professionals, families, seniors, tourists). Nudges specific signal weights.",
    )
    category_answers: dict[str, str] = Field(
        default_factory=dict,
        description="Wizard answers to category-specific questions (e.g. cafe.format, pharmacy.is_24x7). Nudges specific signal weights.",
    )
    shop_size_sqft: int | None = Field(None, ge=50, le=20000, description="Shown for context only; not yet factored into scoring.")
    opening_hours: str | None = Field(None, max_length=50, description="Shown for context only; not yet factored into scoring.")


class AnalysisInputs(BaseSchema):
    city_id: str
    category_id: str
    budget_tier: str
    top_n: int
    weight_overrides: dict[str, float] | None = None
    target_customers: list[str] = Field(default_factory=list)
    category_answers: dict[str, str] = Field(default_factory=dict)
    shop_size_sqft: int | None = None
    opening_hours: str | None = None


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
    trace_id: str = Field("", description="Orchestrator trace ID for this computation; fetch via GET /api/v1/trust/agent-trace/{trace_id} to see the real agent hand-off")
    compute_latency_ms: int = Field(0, description="Actual wall-clock time this specific computation took, measured server-side")
    cells_considered: int = Field(0, description="Total H3 cells loaded for this city")
    eligible_cells_considered: int = Field(0, description="H3 cells that passed the minimum-data eligibility filter and were actually ranked")
    was_cached: bool = Field(False, description="True if this exact request (same inputs) was already computed and served from cache rather than recomputed")


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
