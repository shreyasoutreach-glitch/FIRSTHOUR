"""
Convergence tests -- must prove both directions: a clean lifecycle reports
CONVERGED, and a world that has changed since execution reports
STILL_DIVERGENT with the actual discrepancy, not a static badge.
"""
from __future__ import annotations

import datetime as dt

from app.services.recovery import command as rc
from app.services.recovery.convergence import check_convergence
from app.models import entities as m


def _seed_payout(db, status="queued", amount=500000):
    db.add(m.Merchant(id="MER_CONV", name="Convergence Test Co", category="retail"))
    db.add(m.Contact(id="CON_CONV", merchant_id="MER_CONV", name="Vendor",
                     created_at=dt.datetime(2026, 1, 1)))
    db.add(m.FundAccount(id="FA_CONV", contact_id="CON_CONV", vpa="vendor@upi"))
    payout = m.Payout(id="PYO_CONV", merchant_id="MER_CONV", contact_id="CON_CONV",
                      fund_account_id="FA_CONV", amount=amount, status=status,
                      created_at=dt.datetime(2026, 6, 1))
    db.add(payout)
    db.add(m.Incident(id="INC_CONV", merchant_id="MER_CONV", state="INCIDENT_CONFIRMED"))
    db.commit()
    return payout


def _run_full_lifecycle(db):
    command = rc.propose_command(
        db, incident_id="INC_CONV", action="FREEZE_PAYOUT", target_type="payout",
        target_id="PYO_CONV", amount=500000, reason="suspicious", supporting_evidence=[],
        created_by="USR_1", idempotency_key="conv1",
    )
    rc.review_command(db, command, "USR_2")
    rc.approve_command(db, command, "USR_3")
    rc.execute_command(db, command, "USR_4")
    return command


def test_clean_lifecycle_converges(db_session):
    _seed_payout(db_session, status="queued")
    command = _run_full_lifecycle(db_session)
    result = check_convergence(db_session, command)
    assert result["status"] == "CONVERGED"
    assert result["discrepancies"] == []
    assert all(c["passed"] for c in result["checks"])


def test_convergence_is_replay_consistent(db_session):
    """Same inputs, same outputs -- calling it twice must not flip the
    answer."""
    _seed_payout(db_session, status="queued")
    command = _run_full_lifecycle(db_session)
    r1 = check_convergence(db_session, command)
    r2 = check_convergence(db_session, command)
    assert r1["status"] == r2["status"] == "CONVERGED"


def test_target_changing_after_execution_causes_divergence(db_session):
    """If a Chaos-Lab-style mutation changes the target payout's status
    after the recovery command executed, convergence must detect that the
    world no longer matches what was simulated -- this is the check
    actually catching something."""
    payout = _seed_payout(db_session, status="queued")
    command = _run_full_lifecycle(db_session)
    assert command.execution_result["after"]["status"] == "frozen"

    # Something else moved the payout to "processed" after the fact.
    payout.status = "processed"
    db_session.commit()

    result = check_convergence(db_session, command)
    assert result["status"] == "STILL_DIVERGENT"
    assert any("no longer matches" in d for d in result["discrepancies"])


def test_duplicate_commands_for_same_target_cause_divergence(db_session):
    _seed_payout(db_session, status="queued")
    command = _run_full_lifecycle(db_session)

    # A second, separate command somehow targets the same payout+action
    # (bypassing propose_command's own idempotency check by using a
    # different idempotency_key on purpose, to simulate a real bug/bypass).
    duplicate = m.RecoveryCommand(
        id="REC_DUPLICATE", incident_id="INC_CONV", action="FREEZE_PAYOUT",
        target_type="payout", target_id="PYO_CONV", amount=500000,
        idempotency_key="a_totally_different_key", created_by="USR_ROGUE", state="PROPOSED",
    )
    db_session.add(duplicate)
    db_session.commit()

    result = check_convergence(db_session, command)
    assert result["status"] == "STILL_DIVERGENT"
    assert any("non-rejected recovery commands" in d for d in result["discrepancies"])


def test_amount_mismatch_causes_divergence(db_session):
    _seed_payout(db_session, status="queued", amount=500000)
    command = _run_full_lifecycle(db_session)

    command.amount = 999999  # simulate a data-entry mismatch
    db_session.commit()

    result = check_convergence(db_session, command)
    assert result["status"] == "STILL_DIVERGENT"
    assert any("amount" in d.lower() for d in result["discrepancies"])


def test_verify_transitions_to_verified_and_records_convergence(db_session):
    _seed_payout(db_session, status="queued")
    command = _run_full_lifecycle(db_session)
    verified = rc.verify_command(db_session, command, "USR_SYSTEM")
    assert verified.state == "VERIFIED"

    audit_events = (
        db_session.query(m.AuditEvent)
        .filter(m.AuditEvent.event_type == "RECOVERY_COMMAND_VERIFIED")
        .all()
    )
    assert len(audit_events) == 1
    assert audit_events[0].detail["status"] == "CONVERGED"
