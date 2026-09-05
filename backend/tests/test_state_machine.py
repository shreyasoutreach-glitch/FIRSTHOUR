import pytest

from app.services.incident.state_machine import InvalidTransition, can_transition, transition


def test_ingesting_to_reconstructing_allowed():
    assert can_transition("INGESTING", "RECONSTRUCTING")


def test_cannot_skip_straight_to_recovery_ready():
    assert not can_transition("INGESTING", "RECOVERY_READY")


def test_conflicting_evidence_is_reachable_from_any_review_state():
    assert can_transition("EVIDENCE_REVIEW", "CONFLICTING_EVIDENCE")
    assert can_transition("HUMAN_CONTEXT", "CONFLICTING_EVIDENCE")


def test_escalated_is_terminal():
    assert can_transition("RECOVERY_READY", "ESCALATED")
    assert not can_transition("ESCALATED", "INGESTING")


def test_invalid_transition_raises():
    with pytest.raises(InvalidTransition):
        transition("INGESTING", "ESCALATED")
