from typing import List, Dict, Optional, Any
from pydantic import Field
from .common import BaseSchema
from .chat import Block, VerificationSummary


class TrustMetrics(BaseSchema):
    cases_total: int
    raw_violation_rate: float
    leaked_unsupported: int
    refusal_correct_rate: float
    answer_rate: float
    fallback_rate: float
    latency_p50_ms: int
    latency_p95_ms: int


class EvaluationRunSummary(BaseSchema):
    run_id: str
    created_at: str
    llm_model: str
    metrics: TrustMetrics


class LiveStats(BaseSchema):
    total_chats: int
    verified_rate: float
    partially_verified_rate: float
    fallback_rate: float
    refusal_rate: float
    avg_latency_ms: int


class TrustStatsResponse(BaseSchema):
    latest_eval: Optional[EvaluationRunSummary] = None
    live_stats: LiveStats
    verifier_rules_summary: List[Dict[str, str]]


class TraceDetailResponse(BaseSchema):
    trace_id: str
    created_at: str
    analysis_id: str
    question: str
    selected_location_ids: List[str]
    mode: str
    llm_model: Optional[str] = None
    verification: VerificationSummary
    violations: List[str] = Field(default_factory=list)
    latency_ms: int
    blocks: List[Block]
