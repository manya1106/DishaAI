"""Typed message envelope and trace store for the Disha AI agent swarm.

See plan.md §4.2 for the design rationale. Agents never call each other's
Python methods directly across the swarm boundary — they exchange
AgentMessage envelopes through the Orchestrator, and every hand-off is
recorded in the TraceStore so a single request's agent-to-agent sequence
can be shown (e.g. to judges) via GET /api/v1/trust/agent-trace/{trace_id}
once Phase 6 wires up the route.
"""

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import Field

from ..schemas.common import BaseSchema

AgentRole = Literal["orchestrator", "scoring", "narrator", "verifier"]


class AgentMessage(BaseSchema):
    trace_id: str = Field(..., description="Shared across every hand-off within one end-user request")
    step: int = Field(..., ge=0, description="Ordinal position of this hand-off within the trace")
    sender: AgentRole
    recipient: AgentRole
    payload: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class TraceStore:
    """In-memory store of agent hand-offs, keyed by trace_id.

    Mirrors the existing ring-buffer pattern in ai/chat.py (_TRACE_BUFFER)
    rather than introducing a new persistence mechanism. Phase D may later
    back this with the `agent_runs` Postgres table (plan.md §6.1) without
    changing this class's public interface.
    """

    def __init__(self, max_traces: int = 200):
        self._max_traces = max_traces
        self._messages: dict[str, list[AgentMessage]] = {}
        self._order: list[str] = []

    def record(self, message: AgentMessage) -> None:
        if message.trace_id not in self._messages:
            self._order.append(message.trace_id)
            self._messages[message.trace_id] = []
            if len(self._order) > self._max_traces:
                oldest = self._order.pop(0)
                self._messages.pop(oldest, None)
        self._messages[message.trace_id].append(message)

    def get_trace(self, trace_id: str) -> list[AgentMessage]:
        return list(self._messages.get(trace_id, []))

    def next_step(self, trace_id: str) -> int:
        return len(self._messages.get(trace_id, []))
