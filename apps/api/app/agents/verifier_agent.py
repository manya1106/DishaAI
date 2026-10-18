"""Verifier Agent: builds grounding evidence and gates Narrator drafts.

Wraps ai/evidence.py and ai/verifier.py unchanged (rules V1-V9) — see
plan.md §4.1. Nothing the Narrator Agent drafts reaches the user until
this agent has checked it.
"""

from ..ai.evidence import EvidenceBundle, build_evidence_bundle
from ..ai.verifier import verifier
from ..schemas.analysis import AnalysisResult
from ..schemas.chat import Block, LLMOutput
from ..schemas.enums import VerificationStatus


class VerifierAgent:
    def build_bundle(self, analysis: AnalysisResult, selected_location_ids: list[str]) -> EvidenceBundle:
        return build_evidence_bundle(analysis, selected_location_ids)

    def check(
        self,
        draft: LLMOutput,
        bundle: EvidenceBundle,
    ) -> tuple[list[Block], list[str], VerificationStatus]:
        return verifier.verify(draft, bundle)


verifier_agent = VerifierAgent()
