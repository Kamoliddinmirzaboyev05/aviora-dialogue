from dataclasses import dataclass

from apps.triggers.models import TriggerSet


@dataclass(frozen=True)
class TriggerMatchResult:
    is_match: bool
    score: int
    matched_positive_terms: list[str]
    matched_negative_terms: list[str]
    reason: str


def match_trigger_set(message_text: str, trigger_set: TriggerSet) -> TriggerMatchResult:
    text = message_text.lower()
    positives = [term for term in trigger_set.positive_keywords if term.lower() in text]
    negatives = [term for term in trigger_set.negative_keywords if term.lower() in text]
    if negatives:
        return TriggerMatchResult(False, 0, positives, negatives, f"Excluded by negative terms: {', '.join(negatives)}")
    score = min(100, 35 + len(positives) * 25)
    is_match = trigger_set.enabled and bool(positives) and score >= trigger_set.minimum_score
    reason = "Matched trigger terms: " + ", ".join(positives) if positives else "No configured trigger terms matched."
    return TriggerMatchResult(is_match, score, positives, negatives, reason)
