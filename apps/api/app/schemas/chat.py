from typing import List, Optional
from pydantic import Field
from .common import BaseSchema
from .enums import ClaimType, ClaimPolarity, ChatMode, VerificationStatus


class HistoryTurn(BaseSchema):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseSchema):
    message: str = Field(..., max_length=500, description="User question")
    selected_location_ids: List[str] = Field(default_factory=list, max_length=3)
    history: List[HistoryTurn] = Field(default_factory=list, max_length=6)
    mode: str = Field("auto", description="Either 'auto' or 'deterministic'")


class Claim(BaseSchema):
    claim_id: str
    type: ClaimType
    location_ids: List[str] = Field(default_factory=list)
    signal_id: Optional[str] = None
    polarity: ClaimPolarity = ClaimPolarity.NEUTRAL
    evidence_ids: List[str] = Field(..., min_length=1)
    numbers: List[float] = Field(default_factory=list)
    verified: bool = True


class Block(BaseSchema):
    text: str = Field(..., description="Exactly one verified natural language sentence")
    claims: List[Claim] = Field(default_factory=list)


class VerificationSummary(BaseSchema):
    status: VerificationStatus
    claims_total: int
    claims_verified: int
    claims_removed: int
    attempts: int = 1


class UncertaintyInfo(BaseSchema):
    insufficient_data: bool = False
    missing: List[str] = Field(default_factory=list)


class ChatResponse(BaseSchema):
    trace_id: str
    mode: ChatMode
    verification: VerificationSummary
    blocks: List[Block]
    uncertainty: UncertaintyInfo
    latency_ms: int


# --- LLM Raw Structured Output Models (used by adapter before verifier runs) ---


class LLMClaim(BaseSchema):
    type: ClaimType
    location_ids: List[str] = Field(default_factory=list)
    signal_id: Optional[str] = None
    polarity: ClaimPolarity = ClaimPolarity.NEUTRAL
    evidence_ids: List[str] = Field(..., min_length=1)
    numbers: List[float] = Field(default_factory=list)


class LLMBlock(BaseSchema):
    text: str
    claims: List[LLMClaim] = Field(default_factory=list)


class LLMOutput(BaseSchema):
    blocks: List[LLMBlock] = Field(default_factory=list)
    insufficient_data: bool = False
    missing_reason: Optional[str] = None
