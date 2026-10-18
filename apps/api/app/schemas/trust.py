from pydantic import Field

from .chat import Block, VerificationSummary
from .common import BaseSchema


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
    latest_eval: EvaluationRunSummary | None = None
    live_stats: LiveStats
    verifier_rules_summary: list[dict[str, str]]


class TraceDetailResponse(BaseSchema):
    trace_id: str
    created_at: str
    analysis_id: str
    question: str
    selected_location_ids: list[str]
    mode: str
    llm_model: str | None = None
    verification: VerificationSummary
    violations: list[str] = Field(default_factory=list)
    latency_ms: int
    blocks: list[Block]


class AgentHandoff(BaseSchema):
    step: int
    sender: str
    recipient: str
    payload: dict = Field(default_factory=dict)
    timestamp: str


class AgentTraceResponse(BaseSchema):
    trace_id: str
    handoffs: list[AgentHandoff]
