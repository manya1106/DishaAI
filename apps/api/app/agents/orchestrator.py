"""In-process orchestrator for the Disha AI agent swarm.

Phase 1 scope only (plan.md §Phase 1): a dispatcher that logs hand-offs
to a TraceStore. It does not yet sequence Scoring/Narrator/Verifier
agents or touch any router — that wiring is Phase 5, gated separately.
"""

from .contracts import AgentMessage, AgentRole, TraceStore


class Orchestrator:
    def __init__(self):
        self.trace_store = TraceStore()

    def dispatch(
        self,
        trace_id: str,
        sender: AgentRole,
        recipient: AgentRole,
        payload: dict | None = None,
    ) -> AgentMessage:
        """Record one agent-to-agent hand-off and return the envelope.

        This does not itself invoke the recipient agent — callers (e.g.
        a future handle_chat_request in Phase 5) call the recipient
        directly and use dispatch() purely to log the hand-off for the
        trace view. Keeping dispatch() side-effect-free beyond logging
        means it can be unit-tested with no agent, LLM, or DB involved.
        """
        step = self.trace_store.next_step(trace_id)
        message = AgentMessage(
            trace_id=trace_id,
            step=step,
            sender=sender,
            recipient=recipient,
            payload=payload or {},
        )
        self.trace_store.record(message)
        return message

    def get_trace(self, trace_id: str) -> list[AgentMessage]:
        return self.trace_store.get_trace(trace_id)


orchestrator = Orchestrator()
