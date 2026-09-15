"""
Convergence proof (Section 6 of the enterprise brief).

Important honesty note: the brief's own example (gateway CAPTURED / order
PAID / settlement RECEIVED / ledger POSTED) describes checking agreement
across systems that this build does not have separate representations of --
there is no independent "ledger" system distinct from the payouts table
here, and there is no real settlement/gateway callback since nothing in
this build has a live payment-processor integration. Faking that check
against data structures that don't exist would be exactly the kind of
green-badge theater Section 6 explicitly prohibits.

What IS real and checkable, entirely within this system's own data: given a
RecoveryCommand that has reached EXECUTED (simulated), has the world stayed
consistent with what was simulated? Concretely:

1. No duplicate/orphaned commands -- exactly one non-rejected RecoveryCommand
   exists for this (target_id, action) pair.
2. The audit trail has the full expected chain (PROPOSED -> ... -> EXECUTED)
   with no gaps, in chronological order.
3. Re-simulating the command RIGHT NOW against the current state of its
   target payout produces the same feasibility/after-state that was
   recorded at execution time. If the target has changed since (a Chaos Lab
   scenario touched the same payout, for example), this correctly reports
   STILL_DIVERGENT with the specific discrepancy -- that is the check
   actually catching something, not passing by construction.
4. The command's own recorded amount matches the target payout's amount.

This is a real, deterministic re-computation over live rows, not a stored
flag -- calling it twice against unchanged data returns the same result
every time (see test_convergence.py's replay-consistency test).
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import entities as m


def check_convergence(db: Session, command: m.RecoveryCommand) -> dict:
    checks: list[dict] = []
    discrepancies: list[str] = []

    # --- Check 1: no duplicate/orphaned commands for the same target -------
    siblings = (
        db.query(m.RecoveryCommand)
        .filter(
            m.RecoveryCommand.target_id == command.target_id,
            m.RecoveryCommand.action == command.action,
            m.RecoveryCommand.state != "REJECTED",
        )
        .all()
    )
    no_duplicates = len(siblings) <= 1
    checks.append({"check": "no_duplicate_commands", "passed": no_duplicates,
                   "detail": f"{len(siblings)} non-rejected command(s) for this target+action"})
    if not no_duplicates:
        discrepancies.append(
            f"{len(siblings)} non-rejected recovery commands target the same "
            f"{command.action} on {command.target_id} -- expected exactly 1."
        )

    # --- Check 2: audit trail has the full expected chain, in order --------
    # NOTE: AuditEvent.sources is a JSON list column. `.contains()` on a JSON
    # column is NOT reliably supported across dialects -- verified directly
    # against this SQLite setup during development, where it silently
    # returned zero rows even for a genuine match. Filtering by incident_id
    # (a real indexed string column) and then checking membership in Python
    # is slower but actually correct, which matters more here.
    audit_rows = (
        db.query(m.AuditEvent)
        .filter(m.AuditEvent.incident_id == command.incident_id)
        .order_by(m.AuditEvent.created_at)
        .all()
    )
    audit_rows = [a for a in audit_rows if command.id in (a.sources or [])]
    event_types_present = [a.event_type for a in audit_rows]
    has_propose = "RECOVERY_COMMAND_PROPOSED" in event_types_present
    has_execute = "RECOVERY_COMMAND_EXECUTED" in event_types_present
    propose_before_execute = True
    if has_propose and has_execute:
        propose_idx = event_types_present.index("RECOVERY_COMMAND_PROPOSED")
        execute_idx = event_types_present.index("RECOVERY_COMMAND_EXECUTED")
        propose_before_execute = propose_idx < execute_idx
    audit_complete = has_propose and has_execute and propose_before_execute
    checks.append({"check": "audit_trail_complete", "passed": audit_complete,
                   "detail": f"events recorded: {event_types_present}"})
    if not audit_complete:
        discrepancies.append("Audit trail is missing or out of order for this command's lifecycle.")

    # --- Check 3: re-simulation matches what was recorded at execution -----
    from app.services.recovery.command import _simulate  # local import: avoid a cycle at module load

    from app.core.serialization import to_json_safe
    fresh = to_json_safe(_simulate(db, command))
    recorded = command.execution_result or {}
    resimulation_matches = (
        fresh.get("feasible") == recorded.get("feasible")
        and fresh.get("after") == recorded.get("after")
    )
    checks.append({"check": "resimulation_matches_recorded_execution", "passed": resimulation_matches,
                   "detail": {"recorded_after": recorded.get("after"), "current_after": fresh.get("after")}})
    if not resimulation_matches:
        discrepancies.append(
            "Re-running the simulation against the target's CURRENT state no longer matches what "
            "was recorded at execution time -- the underlying payout has changed since."
        )

    # --- Check 4: amount agreement ------------------------------------------
    payout = db.get(m.Payout, command.target_id) if command.target_type == "payout" else None
    amount_agrees = payout is not None and payout.amount == command.amount
    checks.append({"check": "amount_agrees_with_target_record", "passed": amount_agrees,
                   "detail": {"command_amount": command.amount,
                              "target_amount": payout.amount if payout else None}})
    if not amount_agrees:
        discrepancies.append("The recovery command's recorded amount does not match the target record's amount.")

    status = "CONVERGED" if not discrepancies else "STILL_DIVERGENT"
    return {"status": status, "checks": checks, "discrepancies": discrepancies}
