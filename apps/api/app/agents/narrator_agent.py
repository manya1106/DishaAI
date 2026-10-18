"""Narrator Agent: drafts natural-language explanations from an evidence bundle.

Wraps ai/adapter.py (LLM) and ai/fallback.py (deterministic narrator)
unchanged — see plan.md §4.1. This agent only drafts; it never decides
what reaches the user. The Orchestrator (via ai/chat.py's
ChatOrchestrator) sends every draft to the Verifier Agent before
anything ships.
"""

from ..ai.adapter import llm_adapter
from ..ai.evidence import EvidenceBundle
from ..ai.fallback import deterministic_narrator
from ..schemas.chat import LLMOutput


class NarratorAgent:
    async def draft_llm(self, system_prompt: str, user_prompt: str) -> LLMOutput | None:
        """Ask the configured LLM for a draft. Returns None if disabled/unavailable."""
        return await llm_adapter.generate(system_prompt, user_prompt)

    def draft_deterministic(self, message: str, bundle: EvidenceBundle) -> LLMOutput:
        """Template-based draft that needs no LLM call; always available."""
        return deterministic_narrator.narrate(message, bundle)


narrator_agent = NarratorAgent()
