import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, status

from ..ai.chat import chat_orchestrator
from ..logging import logger
from ..schemas import (
    EvaluationRunSummary,
    LiveStats,
    TraceDetailResponse,
    TrustStatsResponse,
)

router = APIRouter(prefix="/api/v1/trust", tags=["Trust"])

EVAL_RESULTS_FILE = Path(__file__).resolve().parent.parent / "data" / "eval" / "latest_run.json"


def load_latest_eval() -> EvaluationRunSummary | None:
    if not EVAL_RESULTS_FILE.exists():
        return None
    try:
        content = EVAL_RESULTS_FILE.read_text(encoding="utf-8")
        data = json.loads(content)
        return EvaluationRunSummary.model_validate(data)
    except (json.JSONDecodeError, ValueError) as e:
        logger.warning(f"Could not parse eval results file: {e!s}")
        return None


@router.get("/stats", response_model=TrustStatsResponse)
async def get_trust_stats():
    live_dict = chat_orchestrator.get_live_stats()
    live_stats = LiveStats(**live_dict)
    latest_eval = load_latest_eval()

    return TrustStatsResponse(
        latest_eval=latest_eval,
        live_stats=live_stats,
        verifier_rules_summary=[
            {"rule": "V1", "name": "Schema Validity", "desc": "Output strictly adheres to single-sentence block/claim structure."},
            {"rule": "V2", "name": "Evidence Grounding", "desc": "Every claim must cite explicit evidence IDs from the active bundle."},
            {"rule": "V3", "name": "Numeric Consistency", "desc": "Every number in text must match cited evidence values within rounding tolerance."},
            {"rule": "V4", "name": "Entity Grounding", "desc": "Locations and ranks mentioned must be present in the active analysis set."},
            {"rule": "V5", "name": "Rank/Comparison Validity", "desc": "Comparative claims are recomputed against actual score deltas."},
            {"rule": "V6", "name": "Polarity Consistency", "desc": "Strength claims require score >= 50 or top contributor; weaknesses require score <= 45."},
            {"rule": "V7", "name": "Forbidden Topics", "desc": "Speculative currency figures, revenue, profit, or rupee rents are rejected."},
            {"rule": "V8", "name": "Uncited Numbers", "desc": "Any sentence containing numbers without an accompanying claim is rejected."},
            {"rule": "V9", "name": "Integrity Threshold", "desc": "If >50% of statements fail verification, degraded to deterministic fallback."},
        ]
    )


@router.get("/traces/{trace_id}", response_model=TraceDetailResponse)
async def get_trace_detail(trace_id: str):
    trace = chat_orchestrator.get_trace(trace_id)
    if not trace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trace {trace_id} not found in buffer"
        )
    return TraceDetailResponse.model_validate(trace)
