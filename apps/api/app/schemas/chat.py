
from pydantic import Field

from .common import BaseSchema
from .enums import ChatMode, ClaimPolarity, ClaimType, VerificationStatus


class HistoryTurn(BaseSchema):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseSchema):
    message: str = Field(..., max_length=500, description="User question")
    selected_location_ids: list[str] = Field(default_factory=list, max_length=3)
    history: list[HistoryTurn] = Field(default_factory=list, max_length=6)
    mode: str = Field("auto", description="Either 'auto' or 'deterministic'")


class Claim(BaseSchema):
    claim_id: str
    type: ClaimType
    location_ids: list[str] = Field(default_factory=list)
    signal_id: str | None = None
    polarity: ClaimPolarity = ClaimPolarity.NEUTRAL
    evidence_ids: list[str] = Field(..., min_length=1)
    numbers: list[float] = Field(default_factory=list)
    verified: bool = True


class Block(BaseSchema):
    text: str = Field(..., description="Exactly one verified natural language sentence")
    claims: list[Claim] = Field(default_factory=list)


class VerificationSummary(BaseSchema):
    status: VerificationStatus
    claims_total: int
    claims_verified: int
    claims_removed: int
    attempts: int = 1


class UncertaintyInfo(BaseSchema):
    insufficient_data: bool = False
    missing: list[str] = Field(default_factory=list)


class ChatResponse(BaseSchema):
    trace_id: str
    mode: ChatMode
    verification: VerificationSummary
    blocks: list[Block]
    uncertainty: UncertaintyInfo
    latency_ms: int


# --- LLM Raw Structured Output Models (used by adapter before verifier runs) ---


class LLMClaim(BaseSchema):
    type: ClaimType
    location_ids: list[str] = Field(default_factory=list)
    signal_id: str | None = None
    polarity: ClaimPolarity = ClaimPolarity.NEUTRAL
    evidence_ids: list[str] = Field(..., min_length=1)
    numbers: list[float] = Field(default_factory=list)


class LLMBlock(BaseSchema):
    text: str
    claims: list[LLMClaim] = Field(default_factory=list)


class LLMOutput(BaseSchema):
    blocks: list[LLMBlock] = Field(default_factory=list)
    insufficient_data: bool = False
    missing_reason: str | None = None
