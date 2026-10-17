from fastapi import APIRouter
from ..schemas import TrustStatsResponse, TraceDetailResponse, LiveStats

router = APIRouter(prefix="/api/v1/trust", tags=["Trust"])


@router.get("/stats", response_model=TrustStatsResponse)
async def get_trust_stats():
    return TrustStatsResponse(
        latest_eval=None,
        live_stats=LiveStats(
            total_chats=0,
            verified_rate=1.0,
            partially_verified_rate=0.0,
            fallback_rate=0.0,
            refusal_rate=0.0,
            avg_latency_ms=0
        ),
        verifier_rules_summary=[
            {"rule": "V1", "name": "Schema Validity", "desc": "Output strictly adheres to block/claim structure"},
            {"rule": "V2", "name": "Evidence Grounding", "desc": "Every claim must cite existing evidence IDs"},
            {"rule": "V3", "name": "Numeric Consistency", "desc": "Numbers must match cited evidence values within rounding tolerance"},
            {"rule": "V4", "name": "Entity Grounding", "desc": "Locations mentioned must be in selected/active analysis set"},
            {"rule": "V5", "name": "Rank/Comparison Validity", "desc": "Comparative claims recomputed against real metrics"},
            {"rule": "V6", "name": "Polarity Consistency", "desc": "Strength claims require score >= 60 or top 2 contributor; weakness <= 35"},
            {"rule": "V7", "name": "Forbidden Topics", "desc": "Uncited revenue, profit, or rupee figures rejected"},
            {"rule": "V8", "name": "Uncited Numbers", "desc": "Sentences containing numbers without matching claim rejected"},
            {"rule": "V9", "name": "Integrity Threshold", "desc": "If >50% of claims fail, switch to deterministic narrator fallback"},
        ]
    )


@router.get("/traces/{trace_id}", response_model=TraceDetailResponse)
async def get_trace_detail(trace_id: str):
    from fastapi import HTTPException, status
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trace not found")
