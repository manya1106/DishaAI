"""AI Review: an independent, additive pass over the deterministic score.

This does NOT replace the 9-signal scoring engine. scoring/engine.py stays
100% deterministic and untouched (test_golden.py still verifies that
bit-for-bit). This module reads the SAME evidence the engine already
produced, and asks the LLM for a tightly bounded (+/-5%) adjustment with a
one-line reason. The adjustment is only applied if that reason is actually
grounded in the real signal data given to it — an ungrounded or missing
reason reverts the location to its pure math score. When the LLM is
disabled, unreachable, or returns something unusable, every location keeps
its deterministic score unchanged.
"""

import asyncio
import concurrent.futures

from ..config import settings
from ..logging import logger
from ..schemas.analysis import LocationResult
from .adapter import llm_adapter
from .verifier import extract_numbers_from_text, is_number_allowed

MIN_MULTIPLIER = 0.95
MAX_MULTIPLIER = 1.05

# Keep the whole /analyses request well under ~10s: review only the top
# handful of zones (where a close call actually matters) with a tight
# timeout and no retry, so a slow/unreachable LLM falls back to the
# deterministic scores fast instead of stalling the request.
MAX_LOCATIONS_REVIEWED = 5
REVIEW_TIMEOUT_S = 7.0

SYSTEM_PROMPT = """You are the AI Review step in Disha AI's location-scoring pipeline.

A deterministic 9-signal engine has ALREADY computed each zone's math score from
real OpenStreetMap data. You do not recompute or override it. Your only job is to
read the same evidence given below and decide whether real-world judgement should
nudge that score slightly, within a narrow band.

Rules:
- "multiplier" must be a number between 0.95 and 1.05 (1.0 = no change).
- "reason" must be a single short sentence that explicitly names one of the given
  signal_id values or cites one of the given numbers. Never invent a number or
  signal that is not in the evidence below.
- If you have no real basis to adjust a zone, use multiplier 1.0 and reason null.
- Return adjustments for every location_id you were given, even if unchanged.

Return strict JSON only, in this exact shape:
{"adjustments": [{"location_id": "...", "multiplier": 1.0, "reason": "..."}]}
"""


def _build_user_prompt(locations: list[LocationResult], category_id: str) -> str:
    lines = [f"Category: {category_id}", "Zones (this is all the real evidence available; do not invent anything beyond it):"]
    for loc in locations:
        sig_bits = ", ".join(
            f"{s.signal_id}={s.score:.1f}" for s in loc.signals if s.score is not None
        )
        lines.append(
            f'- location_id="{loc.location_id}" name="{loc.display_name}" math_score={loc.overall_score} '
            f"signals: [{sig_bits}] strengths={loc.strengths} limitations={loc.limitations}"
        )
    return "\n".join(lines)


def _is_grounded(reason: str | None, loc: LocationResult) -> bool:
    if not reason or not reason.strip():
        return False
    allowed_numbers = [loc.overall_score] + [
        v for s in loc.signals if s.score is not None for v in (s.score, s.contribution)
    ]
    numbers_in_reason = extract_numbers_from_text(reason)
    if numbers_in_reason:
        return all(is_number_allowed(n, allowed_numbers) for n in numbers_in_reason)
    # No number cited — still acceptable if it actually names a real signal.
    reason_lower = reason.lower()
    return any(s.signal_id.replace("_", " ") in reason_lower for s in loc.signals)


def _rerank(locations: list[LocationResult]) -> list[LocationResult]:
    ordered = sorted(locations, key=lambda loc: (-loc.overall_score, -loc.coverage, loc.location_id))
    return [loc.model_copy(update={"rank": i + 1}) for i, loc in enumerate(ordered)]


async def review_scores(locations: list[LocationResult], category_id: str) -> list[LocationResult]:
    baseline = [loc.model_copy(update={"deterministic_score": loc.overall_score}) for loc in locations]

    if not settings.LLM_ENABLED:
        return _rerank(baseline)

    # Only the top zones actually matter for a "does the AI judgement agree
    # with the math" close call — reviewing all of them would blow the
    # latency budget on a 7B local model for no added signal.
    candidates = baseline[:MAX_LOCATIONS_REVIEWED]

    raw = await llm_adapter.generate_json(
        SYSTEM_PROMPT, _build_user_prompt(candidates, category_id),
        timeout_s=REVIEW_TIMEOUT_S, max_attempts=1,
    )
    if not isinstance(raw, dict):
        return _rerank(baseline)

    raw_adjustments = raw.get("adjustments")
    if not isinstance(raw_adjustments, list):
        return _rerank(baseline)

    by_location = {
        a["location_id"]: a
        for a in raw_adjustments
        if isinstance(a, dict) and isinstance(a.get("location_id"), str)
    }

    reviewed: list[LocationResult] = []
    for loc in baseline:
        adj = by_location.get(loc.location_id)
        if not adj:
            reviewed.append(loc)
            continue

        try:
            multiplier = float(adj.get("multiplier", 1.0))
        except (TypeError, ValueError):
            multiplier = 1.0
        multiplier = max(MIN_MULTIPLIER, min(MAX_MULTIPLIER, multiplier))
        reason = adj.get("reason") if isinstance(adj.get("reason"), str) else None

        if multiplier == 1.0 or not _is_grounded(reason, loc):
            reviewed.append(loc)
            continue

        logger.info(f"AI Review adjusted {loc.location_id} by x{multiplier}: {reason}")
        reviewed.append(loc.model_copy(update={
            "overall_score": round(loc.overall_score * multiplier, 1),
            "ai_adjustment_multiplier": multiplier,
            "ai_adjustment_reason": reason,
        }))

    return _rerank(reviewed)


def review_scores_sync(locations: list[LocationResult], category_id: str) -> list[LocationResult]:
    """Sync bridge so routers/analyses.py (a sync function) can call this
    without itself becoming async. Same pattern as data/db_loader.py's
    _run_sync: runs the coroutine in a fresh thread so it's safe even when
    called from inside FastAPI's already-running event loop.
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, review_scores(locations, category_id)).result()
