from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.authz import get_tenant_db, require_permission
from app.models import entities as m
from app.repositories import incident_repo
from app.schemas.schemas import (
    ConvergenceResponse,
    ProposeRecoveryCommandRequest,
    RecoveryCommandResponse,
    RejectRecoveryCommandRequest,
)
from app.services.recovery import command as recovery_command
from app.services.recovery.convergence import check_convergence

router = APIRouter(tags=["recovery-command"])


def _serialize(rc: m.RecoveryCommand) -> RecoveryCommandResponse:
    return RecoveryCommandResponse(
        id=rc.id, incident_id=rc.incident_id, action=rc.action, target_type=rc.target_type,
        target_id=rc.target_id, amount=rc.amount, reason=rc.reason,
        supporting_evidence=rc.supporting_evidence, expected_effect=rc.expected_effect,
        risk=rc.risk, reversible=rc.reversible, state=rc.state, created_by=rc.created_by,
        reviewed_by=rc.reviewed_by, approved_by=rc.approved_by, execution_mode=rc.execution_mode,
        dry_run_result=rc.dry_run_result, execution_result=rc.execution_result,
        created_at=rc.created_at, updated_at=rc.updated_at,
    )


def _get_command_or_404(db: Session, command_id: str) -> m.RecoveryCommand:
    rc = db.get(m.RecoveryCommand, command_id)
    if rc is None:
        raise HTTPException(404, "recovery command not found")
    return rc


@router.post("/incident/{incident_id}/recovery-commands", response_model=RecoveryCommandResponse)
def propose_recovery_command(
    incident_id: str, body: ProposeRecoveryCommandRequest,
    db: Session = Depends(get_tenant_db),
    user: m.User = Depends(require_permission("RECOMMEND")),
):
    if incident_repo.get_incident(db, incident_id) is None:
        raise HTTPException(404, "incident not found")

    idempotency_key = body.idempotency_key or f"{incident_id}:{body.action}:{body.target_id}"
    rc = recovery_command.propose_command(
        db, incident_id=incident_id, action=body.action, target_type=body.target_type,
        target_id=body.target_id, amount=body.amount, reason=body.reason,
        supporting_evidence=body.supporting_evidence, created_by=user.id,
        idempotency_key=idempotency_key, risk=body.risk, reversible=body.reversible,
    )
    return _serialize(rc)


@router.get("/incident/{incident_id}/recovery-commands", response_model=list[RecoveryCommandResponse])
def list_recovery_commands(incident_id: str, db: Session = Depends(get_tenant_db)):
    if incident_repo.get_incident(db, incident_id) is None:
        raise HTTPException(404, "incident not found")
    commands = (
        db.query(m.RecoveryCommand).filter(m.RecoveryCommand.incident_id == incident_id)
        .order_by(m.RecoveryCommand.created_at).all()
    )
    return [_serialize(rc) for rc in commands]


@router.get("/recovery-commands/{command_id}", response_model=RecoveryCommandResponse)
def get_recovery_command(command_id: str, db: Session = Depends(get_tenant_db)):
    return _serialize(_get_command_or_404(db, command_id))


@router.post("/recovery-commands/{command_id}/dry-run")
def dry_run(command_id: str, db: Session = Depends(get_tenant_db),
            user: m.User = Depends(require_permission("RECOMMEND"))):
    rc = _get_command_or_404(db, command_id)
    return recovery_command.dry_run_command(db, rc, user.id)


@router.post("/recovery-commands/{command_id}/review", response_model=RecoveryCommandResponse)
def review(command_id: str, db: Session = Depends(get_tenant_db),
           user: m.User = Depends(require_permission("INVESTIGATE"))):
    rc = _get_command_or_404(db, command_id)
    try:
        rc = recovery_command.review_command(db, rc, user.id)
    except recovery_command.InvalidRecoveryTransition as e:
        raise HTTPException(409, str(e))
    return _serialize(rc)


@router.post("/recovery-commands/{command_id}/approve", response_model=RecoveryCommandResponse)
def approve(command_id: str, db: Session = Depends(get_tenant_db),
            user: m.User = Depends(require_permission("APPROVE"))):
    rc = _get_command_or_404(db, command_id)
    try:
        rc = recovery_command.approve_command(db, rc, user.id)
    except recovery_command.InvalidRecoveryTransition as e:
        raise HTTPException(409, str(e))
    except PermissionError as e:
        raise HTTPException(403, str(e))
    return _serialize(rc)


@router.post("/recovery-commands/{command_id}/reject", response_model=RecoveryCommandResponse)
def reject(command_id: str, body: RejectRecoveryCommandRequest, db: Session = Depends(get_tenant_db),
           user: m.User = Depends(require_permission("APPROVE"))):
    rc = _get_command_or_404(db, command_id)
    try:
        rc = recovery_command.reject_command(db, rc, user.id, body.reason)
    except recovery_command.InvalidRecoveryTransition as e:
        raise HTTPException(409, str(e))
    return _serialize(rc)


@router.post("/recovery-commands/{command_id}/execute", response_model=RecoveryCommandResponse)
def execute(command_id: str, db: Session = Depends(get_tenant_db),
            user: m.User = Depends(require_permission("EXECUTE"))):
    rc = _get_command_or_404(db, command_id)
    try:
        rc = recovery_command.execute_command(db, rc, user.id)
    except recovery_command.InvalidRecoveryTransition as e:
        raise HTTPException(409, str(e))
    return _serialize(rc)


@router.post("/recovery-commands/{command_id}/verify", response_model=RecoveryCommandResponse)
def verify(command_id: str, db: Session = Depends(get_tenant_db),
           user: m.User = Depends(require_permission("INVESTIGATE"))):
    rc = _get_command_or_404(db, command_id)
    try:
        rc = recovery_command.verify_command(db, rc, user.id)
    except recovery_command.InvalidRecoveryTransition as e:
        raise HTTPException(409, str(e))
    return _serialize(rc)


@router.get("/recovery-commands/{command_id}/convergence", response_model=ConvergenceResponse)
def get_convergence(command_id: str, db: Session = Depends(get_tenant_db)):
    rc = _get_command_or_404(db, command_id)
    return check_convergence(db, rc)
