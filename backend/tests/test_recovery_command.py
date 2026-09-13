"""
Unit tests for the Recovery Command service: state machine transitions,
idempotency, dry-run/execute simulation correctness, and the
propose-approve separation of duties.
"""
from __future__ import annotations

import datetime as dt

import pytest

from app.services.recovery import command as rc
from app.models import entities as m


def _seed_payout(db, status="queued", amount=500000):
    db.add(m.Merchant(id="MER_RC", name="RC Test Co", category="retail"))
    db.add(m.Contact(id="CON_RC", merchant_id="MER_RC", name="Vendor",
                     created_at=dt.datetime(2026, 1, 1)))
    db.add(m.FundAccount(id="FA_RC", contact_id="CON_RC", vpa="vendor@upi"))
    payout = m.Payout(id="PYO_RC", merchant_id="MER_RC", contact_id="CON_RC",
                      fund_account_id="FA_RC", amount=amount, status=status,
                      created_at=dt.datetime(2026, 6, 1))
    db.add(payout)
    db.add(m.Incident(id="INC_RC", merchant_id="MER_RC", state="INCIDENT_CONFIRMED"))
    db.commit()
    return payout


def test_propose_creates_command_in_proposed_state(db_session):
    _seed_payout(db_session)
    command = rc.propose_command(
        db_session, incident_id="INC_RC", action="FREEZE_PAYOUT", target_type="payout",
        target_id="PYO_RC", amount=500000, reason="suspicious", supporting_evidence=[],
        created_by="USR_1", idempotency_key="key1",
    )
    assert command.state == "PROPOSED"
    assert command.created_by == "USR_1"


def test_propose_is_idempotent(db_session):
    _seed_payout(db_session)
    c1 = rc.propose_command(
        db_session, incident_id="INC_RC", action="FREEZE_PAYOUT", target_type="payout",
        target_id="PYO_RC", amount=500000, reason="suspicious", supporting_evidence=[],
        created_by="USR_1", idempotency_key="same_key",
    )
    c2 = rc.propose_command(
        db_session, incident_id="INC_RC", action="FREEZE_PAYOUT", target_type="payout",
        target_id="PYO_RC", amount=500000, reason="different reason text", supporting_evidence=[],
        created_by="USR_2", idempotency_key="same_key",
    )
    assert c1.id == c2.id
    assert db_session.query(m.RecoveryCommand).count() == 1


def test_propose_rejects_unsupported_action(db_session):
    _seed_payout(db_session)
    with pytest.raises(ValueError):
        rc.propose_command(
            db_session, incident_id="INC_RC", action="DELETE_EVERYTHING", target_type="payout",
            target_id="PYO_RC", amount=500000, reason="x", supporting_evidence=[],
            created_by="USR_1", idempotency_key="k",
        )


def test_full_lifecycle_propose_to_verified(db_session):
    _seed_payout(db_session, status="queued")
    command = rc.propose_command(
        db_session, incident_id="INC_RC", action="FREEZE_PAYOUT", target_type="payout",
        target_id="PYO_RC", amount=500000, reason="suspicious", supporting_evidence=["EVD_1"],
        created_by="USR_PROPOSER", idempotency_key="lifecycle",
    )
    command = rc.review_command(db_session, command, "USR_REVIEWER")
    assert command.state == "REVIEWED"
    command = rc.approve_command(db_session, command, "USR_APPROVER")
    assert command.state == "APPROVED"
    assert command.approved_by == "USR_APPROVER"
    command = rc.execute_command(db_session, command, "USR_EXECUTOR")
    assert command.state == "EXECUTED"
    assert command.execution_mode == "SIMULATED"
    assert command.execution_result["feasible"] is True
    command = rc.verify_command(db_session, command, "USR_SYSTEM")
    assert command.state == "VERIFIED"


def test_cannot_skip_straight_to_approved(db_session):
    _seed_payout(db_session)
    command = rc.propose_command(
        db_session, incident_id="INC_RC", action="FREEZE_PAYOUT", target_type="payout",
        target_id="PYO_RC", amount=500000, reason="x", supporting_evidence=[],
        created_by="USR_1", idempotency_key="skip1",
    )
    with pytest.raises(rc.InvalidRecoveryTransition):
        rc.approve_command(db_session, command, "USR_2")


def test_cannot_execute_before_approved(db_session):
    _seed_payout(db_session)
    command = rc.propose_command(
        db_session, incident_id="INC_RC", action="FREEZE_PAYOUT", target_type="payout",
        target_id="PYO_RC", amount=500000, reason="x", supporting_evidence=[],
        created_by="USR_1", idempotency_key="skip2",
    )
    rc.review_command(db_session, command, "USR_2")
    with pytest.raises(rc.InvalidRecoveryTransition):
        rc.execute_command(db_session, command, "USR_3")


def test_proposer_cannot_approve_own_command(db_session):
    """The exact separation-of-duties property the brief calls out."""
    _seed_payout(db_session)
    command = rc.propose_command(
        db_session, incident_id="INC_RC", action="FREEZE_PAYOUT", target_type="payout",
        target_id="PYO_RC", amount=500000, reason="x", supporting_evidence=[],
        created_by="USR_SAME", idempotency_key="selfapprove",
    )
    rc.review_command(db_session, command, "USR_SAME")
    with pytest.raises(PermissionError):
        rc.approve_command(db_session, command, "USR_SAME")


def test_execute_is_idempotent(db_session):
    _seed_payout(db_session, status="queued")
    command = rc.propose_command(
        db_session, incident_id="INC_RC", action="FREEZE_PAYOUT", target_type="payout",
        target_id="PYO_RC", amount=500000, reason="x", supporting_evidence=[],
        created_by="USR_1", idempotency_key="idem_exec",
    )
    rc.review_command(db_session, command, "USR_2")
    rc.approve_command(db_session, command, "USR_3")
    first = rc.execute_command(db_session, command, "USR_4")
    first_executed_at = first.executed_at
    second = rc.execute_command(db_session, command, "USR_4")
    assert second.executed_at == first_executed_at  # not re-executed


def test_dry_run_never_mutates_the_real_payout(db_session):
    payout = _seed_payout(db_session, status="queued")
    command = rc.propose_command(
        db_session, incident_id="INC_RC", action="FREEZE_PAYOUT", target_type="payout",
        target_id="PYO_RC", amount=500000, reason="x", supporting_evidence=[],
        created_by="USR_1", idempotency_key="dryrun1",
    )
    result = rc.dry_run_command(db_session, command, "USR_1")
    assert result["feasible"] is True
    assert result["after"]["status"] == "frozen"

    db_session.refresh(payout)
    assert payout.status == "queued"  # untouched -- simulation only


def test_freeze_infeasible_on_already_processed_payout(db_session):
    _seed_payout(db_session, status="processed")
    command = rc.propose_command(
        db_session, incident_id="INC_RC", action="FREEZE_PAYOUT", target_type="payout",
        target_id="PYO_RC", amount=500000, reason="x", supporting_evidence=[],
        created_by="USR_1", idempotency_key="infeasible1",
    )
    result = rc.dry_run_command(db_session, command, "USR_1")
    assert result["feasible"] is False
    assert len(result["risks"]) > 0


def test_reverse_payout_feasible_only_when_processed(db_session):
    _seed_payout(db_session, status="processed")
    command = rc.propose_command(
        db_session, incident_id="INC_RC", action="REVERSE_PAYOUT", target_type="payout",
        target_id="PYO_RC", amount=500000, reason="x", supporting_evidence=[],
        created_by="USR_1", idempotency_key="reverse1",
    )
    result = rc.dry_run_command(db_session, command, "USR_1")
    assert result["feasible"] is True
    assert result["after"]["status"] == "reversal_requested"


def test_execute_never_writes_to_the_real_payout_table(db_session):
    payout = _seed_payout(db_session, status="queued")
    command = rc.propose_command(
        db_session, incident_id="INC_RC", action="FREEZE_PAYOUT", target_type="payout",
        target_id="PYO_RC", amount=500000, reason="x", supporting_evidence=[],
        created_by="USR_1", idempotency_key="noreal1",
    )
    rc.review_command(db_session, command, "USR_2")
    rc.approve_command(db_session, command, "USR_3")
    rc.execute_command(db_session, command, "USR_4")

    db_session.refresh(payout)
    assert payout.status == "queued"  # the AUTHORITATIVE record never changes
