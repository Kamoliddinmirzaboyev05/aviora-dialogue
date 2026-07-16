from dataclasses import dataclass, field


@dataclass(frozen=True)
class ClassificationResult:
    is_relevant: bool
    intent_type: str
    confidence: float
    detected_problem: str
    urgency: str
    language: str
    sentiment: str
    recommended_action: str
    concise_reason: str
    risk_flags: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class DraftResult:
    text: str
    concise_reason: str
    safety_flags: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class SafetyResult:
    allowed: bool
    flags: list[str]
    reason: str
