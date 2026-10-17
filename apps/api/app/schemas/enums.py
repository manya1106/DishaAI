from enum import Enum


class ProvenanceClass(str, Enum):
    MEASURED = "measured"
    ESTIMATED = "estimated"
    HEURISTIC = "heuristic"
    SIMULATED = "simulated"
    UNAVAILABLE = "unavailable"


class SignalStatus(str, Enum):
    OK = "ok"
    LOW_CONFIDENCE = "low_confidence"
    UNAVAILABLE = "unavailable"


class ConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ClaimType(str, Enum):
    SCORE = "score"
    RANK = "rank"
    COMPARISON = "comparison"
    FACT = "fact"
    REASONING = "reasoning"


class ClaimPolarity(str, Enum):
    STRENGTH = "strength"
    WEAKNESS = "weakness"
    NEUTRAL = "neutral"


class ChatMode(str, Enum):
    LLM_VERIFIED = "llm_verified"
    LLM_PARTIALLY_VERIFIED = "llm_partially_verified"
    DETERMINISTIC_FALLBACK = "deterministic_fallback"
    DETERMINISTIC_REQUESTED = "deterministic_requested"
    REFUSED_INSUFFICIENT_DATA = "refused_insufficient_data"


class VerificationStatus(str, Enum):
    VERIFIED = "verified"
    PARTIALLY_VERIFIED = "partially_verified"
    REJECTED_FALLBACK = "rejected_fallback"
