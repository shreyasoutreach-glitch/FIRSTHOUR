from __future__ import annotations
from decimal import Decimal




"""
Recovery Command: the structured, auditable action-layer the enterprise
brief calls "critical" (Section 4). This is deliberately separate from
services/recovery/packet.py, which only ever *reads* and assembles a
document -- nothing in that file can change financial state or the
command's own lifecycle.

State machine (matches the brief exactly):

    PROPOSED -> REVIEWED -> APPROVED -> EXECUTED -> VERIFIED
    PROPOSED -> REJECTED
    REVIEWED -> REJECTED

Every transition here is guarded twice, independently:
1. By RBAC (app.core.authz.require_permission) at the route layer -- "is
   this role allowed to do this kind of thing at all."
2. By RECOVERY_TRANSITIONS in this file -- "is this command in a state
   where this specific transition is legal right now," regardless of role.
A caller with EXECUTE permission still cannot execute a PROPOSED command
that hasn't been approved -- the state machine has no such edge.

Dry run and execute share one computation (_simulate), because a dry run's
entire purpose is showing *exactly* what execute would do before anyone
commits to it. Neither one ever writes to Payout/Contact/FundAccount rows --
this build has no real payment-processor integration, so "execute" only
ever means execution_mode="SIMULATED": the command's own row records what
would have happened, and the authoritative financial tables are untouched.
That is not a shortcut to fix later -- see AUDIT.md section J: a fake
"real" execution path would be actively dishonest, not a missing feature.
"""


import datetime as dt
import uuid

from sqlalchemy.orm import Session

from app.audit.logger import log as audit_log
from app.models import entities as m

RECOVERY_TRANSITIONS: dict[str, set[str]] = {
    "PROPOSED": {"REVIEWED", "REJECTED"},
    "REVIEWED": {"APPROVED", "REJECTED"},
    "APPROVED": {"EXECUTED"},
    "EXECUTED": {"VERIFIED"},
    "REJECTED": set(),
    "VERIFIED": set(),
}

SUPPORTED_ACTIONS = ("FREEZE_PAYOUT", "REVERSE_PAYOUT")


class InvalidRecoveryTransition(ValueError):
    pass


def can_transition(current: str, target: str) -> bool:
    return target in RECOVERY_TRANSITIONS.get(current, set())


def _require_transition(current: str, target: str) -> None:
    if not can_transition(current, target):
        raise InvalidRecoveryTransition(
            f"Cannot move a recovery command from {current} to {target}"
        )


def propose_command(
    db: Session,
    *,
    incident_id: str,
    action: str,
    target_type: str,
    target_id: str,
    amount: float,
    reason: str,
    supporting_evidence: list[str],
    created_by: str,
    idempotency_key: str,
    risk: str = "MEDIUM",
    reversible: bool = True,
    required_approval_role: str = "APPROVER",
) -> m.RecoveryCommand:
    """Creates a new RecoveryCommand in PROPOSED state, or returns the
    existing one if idempotency_key has already been used -- this is what
    "never allow duplicate execution" actually means in practice: a retried
    request (network blip, double-click) converges on the same command
    instead of creating a second one."""
    if action not in SUPPORTED_ACTIONS:
        raise ValueError(f"Unsupported action: {action}. Supported: {SUPPORTED_ACTIONS}")

    existing = db.query(m.RecoveryCommand).filter(
        m.RecoveryCommand.idempotency_key == idempotency_key
    ).first()
    if existing is not None:
        return existing

    command = m.RecoveryCommand(
        id=f"REC_{uuid.uuid4().hex[:10]}",
        incident_id=incident_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        amount=amount,
        reason=reason,
        supporting_evidence=supporting_evidence,
        expected_effect=_expected_effect_text(action),
        risk=risk,
        reversible=reversible,
        required_approval_role=required_approval_role,
        idempotency_key=idempotency_key,
        state="PROPOSED",
        created_by=created_by,
    )
    db.add(command)
    db.flush()

    audit_log(
        db, incident_id=incident_id, actor="HUMAN", actor_user_id=created_by,
        event_type="RECOVERY_COMMAND_PROPOSED",
        summary=f"{action} on {target_type} {target_id}",
        sources=[command.id], detail={"reason": reason},
    )
    db.commit()
    return command


def _expected_effect_text(action: str) -> str:
    return {
        "FREEZE_PAYOUT": "Payout would be held before settlement; funds would not reach the beneficiary.",
        "REVERSE_PAYOUT": "A reversal claim would be initiated with the bank/UPI network; success is not guaranteed and depends on the beneficiary's bank.",
    }.get(action, "")


def _simulate(db: Session, command: m.RecoveryCommand) -> dict:
    """The one place that computes "what would happen" -- used by both
    dry_run (no state change) and execute (state change to EXECUTED, but
    still records SIMULATED, never touches the Payout row itself)."""
    if command.target_type != "payout":
        return {
            "feasible": False,
            "before": {}, "after": {}, "delta": {},
            "risks": ["Unsupported target_type for simulation: " + command.target_type],
            "affected_records": [], "expected_convergence": "",
        }

    payout = db.get(m.Payout, command.target_id)
    if payout is None:
        return {
            "feasible": False,
            "before": {}, "after": {}, "delta": {},
            "risks": ["Target payout not found -- it may belong to a different tenant or never existed."],
            "affected_records": [], "expected_convergence": "",
        }

    before = {"status": payout.status, "amount": payout.amount, "contact_id": payout.contact_id}

    if command.action == "FREEZE_PAYOUT":
        feasible = payout.status in ("queued", "pending", "processing")
        after_status = "frozen" if feasible else payout.status
        risks = [] if feasible else [
            f"Payout is already '{payout.status}' -- it cannot be frozen after settlement. "
            "Consider REVERSE_PAYOUT instead."
        ]
        convergence = (
            "Exposure would move from PENDING to BLOCKED; the payout would never reach the beneficiary."
            if feasible else
            "No state change possible; funds have already moved."
        )
    elif command.action == "REVERSE_PAYOUT":
        feasible = payout.status == "processed"
        after_status = "reversal_requested" if feasible else payout.status
        risks = [] if feasible else [
            f"Payout is '{payout.status}', not 'processed' -- nothing to reverse yet. "
            "Consider FREEZE_PAYOUT instead."
        ]
        risks = risks + (["Reversal success depends on the beneficiary bank/UPI network and is not guaranteed."] if feasible else [])
        convergence = (
            "If the reversal is accepted by the beneficiary's bank, exposure would move from "
            "CONFIRMED_MOVED to RECOVERED; this cannot be confirmed until the bank responds."
            if feasible else
            "No reversal is possible from the current payout state."
        )
    else:
        feasible, after_status, risks, convergence = False, payout.status, ["Unknown action"], ""

    after = {"status": after_status, "amount": payout.amount, "contact_id": payout.contact_id}
    delta = {k: after[k] for k in after if after[k] != before[k]}

    return {
        "feasible": feasible,
        "before": before,
        "after": after,
        "delta": delta,
        "risks": risks,
        "affected_records": [f"PYO:{payout.id}", f"CON:{payout.contact_id}"],
        "expected_convergence": convergence,
    }


def dry_run_command(db: Session, command: m.RecoveryCommand, user_id: str) -> dict:
    result = _simulate(db, command)
    command.dry_run_result = result
    db.flush()
    audit_log(
        db, incident_id=command.incident_id, actor="HUMAN", actor_user_id=user_id,
        event_type="RECOVERY_COMMAND_DRY_RUN", summary=f"Dry run for {command.id}",
        sources=[command.id], detail={"feasible": result["feasible"]},
    )
    db.commit()
    return result


def review_command(db: Session, command: m.RecoveryCommand, user_id: str) -> m.RecoveryCommand:
    _require_transition(command.state, "REVIEWED")
    old_state = command.state
    command.state = "REVIEWED"
    command.reviewed_by = user_id
    command.updated_at = dt.datetime.now(dt.timezone.utc)
    audit_log(
        db, incident_id=command.incident_id, actor="HUMAN", actor_user_id=user_id,
        event_type="RECOVERY_COMMAND_STATE_CHANGED", summary=f"{old_state} -> REVIEWED",
        sources=[command.id], before_state={"state": old_state}, after_state={"state": "REVIEWED"},
    )
    db.commit()
    return command


def approve_command(db: Session, command: m.RecoveryCommand, user_id: str) -> m.RecoveryCommand:
    _require_transition(command.state, "APPROVED")
    if command.created_by == user_id:
        raise PermissionError("A recovery command cannot be approved by the same user who proposed it.")
    old_state = command.state
    command.state = "APPROVED"
    command.approved_by = user_id
    command.updated_at = dt.datetime.now(dt.timezone.utc)
    audit_log(
        db, incident_id=command.incident_id, actor="HUMAN", actor_user_id=user_id,
        event_type="RECOVERY_COMMAND_STATE_CHANGED", summary=f"{old_state} -> APPROVED",
        sources=[command.id], before_state={"state": old_state}, after_state={"state": "APPROVED"},
    )
    db.commit()
    return command


def reject_command(db: Session, command: m.RecoveryCommand, user_id: str, reason: str = "") -> m.RecoveryCommand:
    _require_transition(command.state, "REJECTED")
    old_state = command.state
    command.state = "REJECTED"
    command.updated_at = dt.datetime.now(dt.timezone.utc)
    audit_log(
        db, incident_id=command.incident_id, actor="HUMAN", actor_user_id=user_id,
        event_type="RECOVERY_COMMAND_STATE_CHANGED", summary=f"{old_state} -> REJECTED: {reason}",
        sources=[command.id], before_state={"state": old_state}, after_state={"state": "REJECTED"},
    )
    db.commit()
    return command


def execute_command(db: Session, command: m.RecoveryCommand, user_id: str) -> m.RecoveryCommand:
    """Simulated execution only -- see module docstring. Idempotent: calling
    this twice on an already-EXECUTED command returns it unchanged rather
    than re-running (and re-auditing) the simulation, since
    RECOVERY_TRANSITIONS has no EXECUTED -> EXECUTED edge and this check
    happens before we'd otherwise raise on that."""
    if command.state == "EXECUTED":
        return command
    _require_transition(command.state, "EXECUTED")

    result = _simulate(db, command)
    old_state = command.state
    command.state = "EXECUTED"
    command.execution_mode = "SIMULATED"
    command.execution_result = result
    command.executed_at = dt.datetime.now(dt.timezone.utc)
    command.updated_at = command.executed_at
    audit_log(
        db, incident_id=command.incident_id, actor="HUMAN", actor_user_id=user_id,
        event_type="RECOVERY_COMMAND_EXECUTED", summary=f"{old_state} -> EXECUTED (SIMULATED)",
        sources=[command.id], detail={"feasible": result["feasible"]},
        before_state={"state": old_state}, after_state={"state": "EXECUTED", "execution_mode": "SIMULATED"},
    )
    db.commit()
    return command


def verify_command(db: Session, command: m.RecoveryCommand, user_id: str) -> m.RecoveryCommand:
    """Runs the convergence check (see services/recovery/convergence.py)
    against the command's own simulated result and records CONVERGED /
    STILL_DIVERGENT -- imported lazily to avoid a circular import."""
    from app.services.recovery.convergence import check_convergence

    _require_transition(command.state, "VERIFIED")
    convergence = check_convergence(db, command)
    old_state = command.state
    command.state = "VERIFIED"
    command.updated_at = dt.datetime.now(dt.timezone.utc)
    audit_log(
        db, incident_id=command.incident_id, actor="SYSTEM", actor_user_id=user_id,
        event_type="RECOVERY_COMMAND_VERIFIED",
        summary=f"Convergence: {convergence['status']}",
        sources=[command.id], detail=convergence,
        before_state={"state": old_state}, after_state={"state": "VERIFIED"},
    )
    db.commit()
    return command





