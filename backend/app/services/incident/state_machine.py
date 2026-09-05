"""
Incident state machine. CONFLICTING_EVIDENCE is a first-class legitimate
state (not an error path) per the architecture doc -- evidence that
disagrees with itself is a real outcome, not a bug.
"""
from __future__ import annotations

ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "INGESTING": {"RECONSTRUCTING", "CONFLICTING_EVIDENCE"},
    "RECONSTRUCTING": {"EVIDENCE_REVIEW", "CONFLICTING_EVIDENCE"},
    "EVIDENCE_REVIEW": {"HUMAN_CONTEXT", "CONFLICTING_EVIDENCE"},
    "HUMAN_CONTEXT": {"INCIDENT_CONFIRMED", "CONFLICTING_EVIDENCE"},
    "INCIDENT_CONFIRMED": {"EXPOSURE_ASSESSED"},
    "EXPOSURE_ASSESSED": {"RECOVERY_READY"},
    "RECOVERY_READY": {"ESCALATED"},
    "CONFLICTING_EVIDENCE": {"EVIDENCE_REVIEW", "HUMAN_CONTEXT"},
    "ESCALATED": set(),
}


class InvalidTransition(ValueError):
    pass


def can_transition(current: str, target: str) -> bool:
    return target in ALLOWED_TRANSITIONS.get(current, set())


def transition(current: str, target: str) -> str:
    if not can_transition(current, target):
        raise InvalidTransition(f"Cannot move from {current} to {target}")
    return target
