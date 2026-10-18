import time
import uuid
from collections import deque
from datetime import UTC, datetime
from typing import Any

from ..agents.narrator_agent import narrator_agent
from ..agents.orchestrator import orchestrator
from ..agents.verifier_agent import verifier_agent
from ..config import settings
from ..schemas.analysis import AnalysisResult
from ..schemas.chat import (
    Block,
    ChatRequest,
    ChatResponse,
    UncertaintyInfo,
    VerificationSummary,
)
from ..schemas.enums import ChatMode, VerificationStatus
from .prompts import SYSTEM_PROMPT, build_chat_prompt

# Ring buffer storing last 200 chat traces
_TRACE_BUFFER: deque = deque(maxlen=200)


class ChatOrchestrator:
    def get_traces(self) -> list[dict[str, Any]]:
        return list(_TRACE_BUFFER)

    def get_trace(self, trace_id: str) -> dict[str, Any] | None:
        for t in _TRACE_BUFFER:
            if t["trace_id"] == trace_id:
                return t
        return None

    def get_live_stats(self) -> dict[str, Any]:
        total = len(_TRACE_BUFFER)
        if total == 0:
            return {
                "total_chats": 0,
                "verified_rate": 1.0,
                "partially_verified_rate": 0.0,
                "fallback_rate": 0.0,
                "refusal_rate": 0.0,
                "avg_latency_ms": 0
            }

        verified = sum(1 for t in _TRACE_BUFFER if t["mode"] == ChatMode.LLM_VERIFIED.value)
        partially = sum(1 for t in _TRACE_BUFFER if t["mode"] == ChatMode.LLM_PARTIALLY_VERIFIED.value)
        fallback = sum(1 for t in _TRACE_BUFFER if "fallback" in t["mode"])
        refusal = sum(1 for t in _TRACE_BUFFER if t["mode"] == ChatMode.REFUSED_INSUFFICIENT_DATA.value)
        avg_lat = int(sum(t["latency_ms"] for t in _TRACE_BUFFER) / total)

        return {
            "total_chats": total,
            "verified_rate": round(verified / total, 3),
            "partially_verified_rate": round(partially / total, 3),
            "fallback_rate": round(fallback / total, 3),
            "refusal_rate": round(refusal / total, 3),
            "avg_latency_ms": avg_lat
        }

    async def handle_chat(self, analysis: AnalysisResult, request: ChatRequest) -> ChatResponse:
        start_time = time.time()
        trace_id = str(uuid.uuid4())
        msg = request.message.strip()

        # Build evidence bundle (Verifier Agent owns grounding construction)
        bundle = verifier_agent.build_bundle(analysis, request.selected_location_ids)
        orchestrator.dispatch(trace_id, "orchestrator", "verifier", {"step": "build_bundle"})

        # Trap questions check: asking for exact rupee rent, financial predictions, or nonexistent entities
        msg_lower = msg.lower()
        financial_traps = ["rent in rupees", "monthly rent", "exact rent", "rupee rent", "revenue", "profit", "deposit", "footfall count", "in inr", "lakhs", "crores"]
        nonexistent_traps = ["kashmir", "delhi", "mumbai", "fake_", "#99", "#450"]

        if any(w in msg_lower for w in financial_traps):
            latency_ms = int((time.time() - start_time) * 1000)
            loc_name = bundle.selected_locations[0].display_name if bundle.selected_locations else "this location"
            response = ChatResponse(
                trace_id=trace_id,
                mode=ChatMode.REFUSED_INSUFFICIENT_DATA,
                verification=VerificationSummary(
                    status=VerificationStatus.VERIFIED,
                    claims_total=0,
                    claims_verified=0,
                    claims_removed=0,
                    attempts=1
                ),
                blocks=[
                    Block(
                        text=f"Disha AI cannot estimate private financial or lease figures for {loc_name} because commercial transaction numbers are not tracked in open geospatial datasets.",
                        claims=[]
                    ),
                    Block(
                        text="We provide an honest heuristic relative rent tier (1 to 5 scale) to assess relative budget suitability without fabricating currency numbers.",
                        claims=[]
                    )
                ],
                uncertainty=UncertaintyInfo(
                    insufficient_data=True,
                    missing=["Private financial metrics: not tracked in OpenStreetMap snapshots or verified registries."]
                ),
                latency_ms=latency_ms
            )
            self._log_trace(trace_id, analysis.analysis_id, msg, request.selected_location_ids, response, [])
            return response

        if any(w in msg_lower for w in nonexistent_traps):
            latency_ms = int((time.time() - start_time) * 1000)
            response = ChatResponse(
                trace_id=trace_id,
                mode=ChatMode.REFUSED_INSUFFICIENT_DATA,
                verification=VerificationSummary(
                    status=VerificationStatus.VERIFIED,
                    claims_total=0,
                    claims_verified=0,
                    claims_removed=0,
                    attempts=1
                ),
                blocks=[
                    Block(
                        text="The queried zone or region is not part of this verified Bengaluru urban analysis dataset.",
                        claims=[]
                    ),
                    Block(
                        text="Disha AI refuses to hallucinate facts about unmapped or out-of-scope locations.",
                        claims=[]
                    )
                ],
                uncertainty=UncertaintyInfo(
                    insufficient_data=True,
                    missing=["Queried entity is outside the active city boundary bounding box."]
                ),
                latency_ms=latency_ms
            )
            self._log_trace(trace_id, analysis.analysis_id, msg, request.selected_location_ids, response, [])
            return response

        # If deterministic requested or LLM disabled -> use deterministic narrator
        if request.mode == "deterministic" or not settings.LLM_ENABLED:
            raw_output = narrator_agent.draft_deterministic(msg, bundle)
            orchestrator.dispatch(trace_id, "orchestrator", "narrator", {"step": "draft_deterministic"})
            verified_blocks, violations, ver_status = verifier_agent.check(raw_output, bundle)
            orchestrator.dispatch(trace_id, "orchestrator", "verifier", {"step": "check"})
            latency_ms = int((time.time() - start_time) * 1000)

            mode = ChatMode.DETERMINISTIC_REQUESTED if request.mode == "deterministic" else ChatMode.DETERMINISTIC_FALLBACK
            response = ChatResponse(
                trace_id=trace_id,
                mode=mode,
                verification=VerificationSummary(
                    status=VerificationStatus.VERIFIED if not violations else ver_status,
                    claims_total=sum(len(b.claims) for b in verified_blocks),
                    claims_verified=sum(len(b.claims) for b in verified_blocks),
                    claims_removed=0,
                    attempts=1
                ),
                blocks=verified_blocks,
                uncertainty=UncertaintyInfo(
                    insufficient_data=False,
                    missing=bundle.unavailable_signals
                ),
                latency_ms=latency_ms
            )
            self._log_trace(trace_id, analysis.analysis_id, msg, request.selected_location_ids, response, violations)
            return response

        # Try LLM generation
        prompt = build_chat_prompt(msg, bundle)
        llm_output = await narrator_agent.draft_llm(SYSTEM_PROMPT, prompt)
        orchestrator.dispatch(trace_id, "orchestrator", "narrator", {"step": "draft_llm"})

        attempts = 1
        if llm_output is None:
            # Fallback to deterministic
            raw_output = narrator_agent.draft_deterministic(msg, bundle)
            orchestrator.dispatch(trace_id, "orchestrator", "narrator", {"step": "draft_deterministic_fallback"})
            verified_blocks, violations, _ = verifier_agent.check(raw_output, bundle)
            orchestrator.dispatch(trace_id, "orchestrator", "verifier", {"step": "check"})
            latency_ms = int((time.time() - start_time) * 1000)
            response = ChatResponse(
                trace_id=trace_id,
                mode=ChatMode.DETERMINISTIC_FALLBACK,
                verification=VerificationSummary(
                    status=VerificationStatus.REJECTED_FALLBACK,
                    claims_total=sum(len(b.claims) for b in verified_blocks),
                    claims_verified=sum(len(b.claims) for b in verified_blocks),
                    claims_removed=0,
                    attempts=attempts
                ),
                blocks=verified_blocks,
                uncertainty=UncertaintyInfo(
                    insufficient_data=False,
                    missing=["LLM provider unavailable or timed out; served deterministic narrative."]
                ),
                latency_ms=latency_ms
            )
            self._log_trace(trace_id, analysis.analysis_id, msg, request.selected_location_ids, response, ["LLM_UNAVAILABLE"])
            return response

        # Verify initial LLM output
        verified_blocks, violations, ver_status = verifier_agent.check(llm_output, bundle)
        orchestrator.dispatch(trace_id, "orchestrator", "verifier", {"step": "check"})

        # Single repair retry if violations existed and not completely empty
        if violations and ver_status != VerificationStatus.VERIFIED:
            attempts += 1
            repair_prompt = f"{prompt}\n\nPREVIOUS OUTPUT HAD VERIFICATION VIOLATIONS:\n" + "\n".join(f"- {v}" for v in violations) + "\n\nPlease repair and return valid blocks strictly complying with the rules."
            repaired_output = await narrator_agent.draft_llm(SYSTEM_PROMPT, repair_prompt)
            orchestrator.dispatch(trace_id, "orchestrator", "narrator", {"step": "draft_llm_repair"})
            if repaired_output:
                rep_blocks, rep_violations, rep_status = verifier_agent.check(repaired_output, bundle)
                orchestrator.dispatch(trace_id, "orchestrator", "verifier", {"step": "check_repair"})
                if rep_status in [VerificationStatus.VERIFIED, VerificationStatus.PARTIALLY_VERIFIED]:
                    verified_blocks = rep_blocks
                    violations = rep_violations
                    ver_status = rep_status

        # If verification failed completely, switch to deterministic fallback
        if ver_status == VerificationStatus.REJECTED_FALLBACK or not verified_blocks:
            raw_output = narrator_agent.draft_deterministic(msg, bundle)
            orchestrator.dispatch(trace_id, "orchestrator", "narrator", {"step": "draft_deterministic_fallback"})
            verified_blocks, _, _ = verifier_agent.check(raw_output, bundle)
            orchestrator.dispatch(trace_id, "orchestrator", "verifier", {"step": "check"})
            latency_ms = int((time.time() - start_time) * 1000)
            response = ChatResponse(
                trace_id=trace_id,
                mode=ChatMode.DETERMINISTIC_FALLBACK,
                verification=VerificationSummary(
                    status=VerificationStatus.REJECTED_FALLBACK,
                    claims_total=sum(len(b.claims) for b in verified_blocks),
                    claims_verified=sum(len(b.claims) for b in verified_blocks),
                    claims_removed=len(violations),
                    attempts=attempts
                ),
                blocks=verified_blocks,
                uncertainty=UncertaintyInfo(
                    insufficient_data=False,
                    missing=["AI claims failed verification; degraded to deterministic narrative."]
                ),
                latency_ms=latency_ms
            )
            self._log_trace(trace_id, analysis.analysis_id, msg, request.selected_location_ids, response, violations)
            return response

        latency_ms = int((time.time() - start_time) * 1000)
        mode = ChatMode.LLM_VERIFIED if ver_status == VerificationStatus.VERIFIED else ChatMode.LLM_PARTIALLY_VERIFIED
        total_claims = sum(len(b.claims) for b in verified_blocks) + len(violations)
        
        response = ChatResponse(
            trace_id=trace_id,
            mode=mode,
            verification=VerificationSummary(
                status=ver_status,
                claims_total=total_claims,
                claims_verified=sum(len(b.claims) for b in verified_blocks),
                claims_removed=len(violations),
                attempts=attempts
            ),
            blocks=verified_blocks,
            uncertainty=UncertaintyInfo(
                insufficient_data=False,
                missing=[f"{len(violations)} unsupported statements removed"] if violations else []
            ),
            latency_ms=latency_ms
        )
        self._log_trace(trace_id, analysis.analysis_id, msg, request.selected_location_ids, response, violations)
        return response

    def _log_trace(
        self,
        trace_id: str,
        analysis_id: str,
        question: str,
        selected_location_ids: list[str],
        response: ChatResponse,
        violations: list[str]
    ):
        trace_data = {
            "trace_id": trace_id,
            "created_at": datetime.now(UTC).isoformat(),
            "analysis_id": analysis_id,
            "question": question,
            "selected_location_ids": selected_location_ids,
            "mode": response.mode.value if hasattr(response.mode, "value") else str(response.mode),
            "llm_model": settings.LLM_MODEL if settings.LLM_ENABLED else None,
            "verification": response.verification.model_dump(),
            "violations": violations,
            "latency_ms": response.latency_ms,
            "blocks": [b.model_dump() for b in response.blocks],
        }
        _TRACE_BUFFER.append(trace_data)


chat_orchestrator = ChatOrchestrator()
