from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.audit.logger import log as audit_log
from app.core.authz import get_tenant_db, require_permission
from app.models import entities as m
from app.repositories import incident_repo
from app.schemas.schemas import AttestationRequest, AttestationResponse, NextQuestionResponse
from app.services.exposure.engine import compute_exposure
from app.services.graph.builder import build_incident_graph
from app.services.human.questions import candidate_questions_for_incident, next_question
from app.services.incident.state_machine import can_transition
from app.services.recovery.packet import build_recovery_packet

router = APIRouter(tags=["incident"])


def _serialize_incident(incident: m.Incident) -> dict:
    return {
        "id": incident.id,
        "merchant_id": incident.merchant_id,
        "state": incident.state,
        "scenario": incident.scenario,
        "incident_evidence_score": incident.incident_evidence_score,
        "score_components": incident.score_components,
        "window_start": incident.window_start,
        "window_end": incident.window_end,
        "dataset_version": incident.dataset_version,
        "config_version": incident.config_version,
        "created_at": incident.created_at,
    }


@router.get("/incidents")
def list_incidents(db: Session = Depends(get_tenant_db)):
    incidents = db.query(m.Incident).order_by(m.Incident.created_at.desc()).all()
    return [_serialize_incident(i) for i in incidents]


@router.get("/incident/{incident_id}")
def get_incident(incident_id: str, db: Session = Depends(get_tenant_db)):
    incident = incident_repo.get_incident(db, incident_id)
    if incident is None:
        raise HTTPException(404, "incident not found")
    merchant = db.get(m.Merchant, incident.merchant_id)
    payouts_for_baseline = db.query(m.Payout).filter(m.Payout.merchant_id == incident.merchant_id).all()
    import statistics
    amounts = [p.amount for p in payouts_for_baseline if not p.is_injected]
    median = statistics.median(amounts) if amounts else 0.0

    fevents = incident_repo.list_incident_financial_events(db, incident_id)
    beneficiary_ids = set()
    new_beneficiary_ids = set()
    for fe in fevents:
        payout = db.get(m.Payout, fe.source_record_id)
        if payout:
            beneficiary_ids.add(payout.contact_id)
            contact = db.get(m.Contact, payout.contact_id)
            if contact and incident.window_start and contact.created_at >= incident.window_start - __import__("datetime").timedelta(hours=1):
                new_beneficiary_ids.add(contact.id)

    total_exposed = sum(fe.amount for fe in fevents)
    window_seconds = (
        (incident.window_end - incident.window_start).total_seconds()
        if incident.window_start and incident.window_end else 0
    )

    return {
        **_serialize_incident(incident),
        "merchant_name": merchant.name if merchant else "",
        "headline": {
            "total_exposed": total_exposed,
            "payout_count": len(fevents),
            "beneficiary_count": len(beneficiary_ids),
            "new_beneficiary_count": len(new_beneficiary_ids),
            "window_seconds": window_seconds,
            "median_baseline_payout": median,
            "multiple_of_median": round(total_exposed / len(fevents) / median, 1) if median and fevents else 0,
        },
    }


@router.get("/incident/{incident_id}/timeline")
def get_timeline(incident_id: str, db: Session = Depends(get_tenant_db)):
    incident = incident_repo.get_incident(db, incident_id)
    if incident is None:
        raise HTTPException(404, "incident not found")

    fevents = incident_repo.list_incident_financial_events(db, incident_id)
    comms = incident_repo.list_communications(db, incident_id)

    spine = []
    for c in comms:
        spine.append({
            "type": "communication",
            "timestamp": c.timestamp,
            "label": "COMMUNICATION EVENT",
            "detail": c.body_text,
            "channel": c.channel,
            "correlation_status": c.correlation_status,
            "source_artifact_id": c.source_artifact_id,
            "id": c.id,
        })
    for fe in fevents:
        payout = db.get(m.Payout, fe.source_record_id)
        contact = db.get(m.Contact, payout.contact_id) if payout else None
        prior_count = 0
        if payout:
            prior_count = (
                db.query(m.Payout)
                .filter(m.Payout.contact_id == payout.contact_id, m.Payout.created_at < payout.created_at)
                .count()
            )
        spine.append({
            "type": "payout",
            "timestamp": fe.timestamp,
            "label": "NEW BENEFICIARY" if prior_count == 0 else "SAME BENEFICIARY",
            "amount": fe.amount,
            "beneficiary": contact.name if contact else "",
            "beneficiary_contact_id": contact.id if contact else "",
            "id": fe.id,
            "source_reference": fe.source_record_id,
            "attributes": fe.attributes,
        })

    spine.sort(key=lambda e: e["timestamp"])
    return spine


@router.get("/incident/{incident_id}/graph")
def get_graph(incident_id: str, db: Session = Depends(get_tenant_db)):
    if incident_repo.get_incident(db, incident_id) is None:
        raise HTTPException(404, "incident not found")
    return build_incident_graph(db, incident_id)


@router.get("/incident/{incident_id}/exposure")
def get_exposure(incident_id: str, db: Session = Depends(get_tenant_db)):
    if incident_repo.get_incident(db, incident_id) is None:
        raise HTTPException(404, "incident not found")
    return compute_exposure(db, incident_id)


@router.get("/incident/{incident_id}/evidence")
def get_evidence(incident_id: str, db: Session = Depends(get_tenant_db)):
    if incident_repo.get_incident(db, incident_id) is None:
        raise HTTPException(404, "incident not found")
    comms = incident_repo.list_communications(db, incident_id)
    artifact_ids = {c.source_artifact_id for c in comms}
    artifacts = db.query(m.EvidenceArtifact).filter(m.EvidenceArtifact.id.in_(artifact_ids)).all()
    claims = db.query(m.ExtractedClaim).filter(m.ExtractedClaim.source_artifact_id.in_(artifact_ids)).all()
    return {
        "artifacts": [{
            "id": a.id, "filename": a.filename, "mime_type": a.mime_type, "sha256": a.sha256,
            "source_label": a.source_label, "extraction_status": a.extraction_status,
            "uploaded_at": a.uploaded_at,
        } for a in artifacts],
        "claims": [{
            "id": c.id, "source_artifact_id": c.source_artifact_id, "claim_type": c.claim_type,
            "claim_value": c.claim_value, "verification_status": c.verification_status,
            "matched_financial_event_id": c.matched_financial_event_id,
        } for c in claims],
        "communications": [{
            "id": c.id, "channel": c.channel, "sender_label": c.sender_label, "body_text": c.body_text,
            "timestamp": c.timestamp, "correlation_status": c.correlation_status,
        } for c in comms],
    }


@router.get("/incident/{incident_id}/questions/next", response_model=NextQuestionResponse)
def get_next_question(incident_id: str, db: Session = Depends(get_tenant_db)):
    incident = incident_repo.get_incident(db, incident_id)
    if incident is None:
        raise HTTPException(404, "incident not found")

    fevents = incident_repo.list_incident_financial_events(db, incident_id)
    comms = incident_repo.list_communications(db, incident_id)
    new_beneficiary = any((incident.score_components or {}).get("new_beneficiary", 0) > 0 for _ in [0])
    is_high_amount = (incident.score_components or {}).get("amount_anomaly", 0) > 0.5
    dormant = (incident.score_components or {}).get("dormant_entity", 0) > 0.3

    candidates = candidate_questions_for_incident(
        has_new_beneficiary=new_beneficiary,
        has_communication_evidence=len(comms) > 0,
        is_high_amount=is_high_amount,
        has_dormant_reactivation=dormant,
    )
    answered = {a.question_id for a in incident_repo.list_attestations(db, incident_id)}
    nxt = next_question(candidates, answered)
    if nxt is None:
        return NextQuestionResponse(question_id=None, question_text=None, priority=None,
                                     remaining_count=0)
    remaining = len([c for c in candidates if c.question_id not in answered])
    return NextQuestionResponse(question_id=nxt.question_id, question_text=nxt.question_text,
                                 priority=nxt.priority, remaining_count=remaining)


@router.post("/incident/{incident_id}/attestation", response_model=AttestationResponse)
def post_attestation(incident_id: str, body: AttestationRequest, db: Session = Depends(get_tenant_db),
                     user: m.User = Depends(require_permission("INVESTIGATE"))):
    incident = incident_repo.get_incident(db, incident_id)
    if incident is None:
        raise HTTPException(404, "incident not found")

    fevents = incident_repo.list_incident_financial_events(db, incident_id)
    comms = incident_repo.list_communications(db, incident_id)
    candidates = candidate_questions_for_incident(
        has_new_beneficiary=True, has_communication_evidence=len(comms) > 0,
        is_high_amount=True, has_dormant_reactivation=False,
    )
    matched = next((c for c in candidates if c.question_id == body.question_id), None)
    if matched is None:
        raise HTTPException(400, "unknown question_id")

    attestation = m.HumanAttestation(
        id=f"ATT_{uuid.uuid4().hex[:10]}",
        incident_id=incident_id,
        question_id=body.question_id,
        question_text=matched.question_text,
        answer=body.answer,
        note=body.note,
        affected_predicate=matched.affected_predicate,
    )
    db.add(attestation)
    db.flush()

    audit_log(db, incident_id=incident_id, actor="HUMAN", actor_user_id=user.id,
              event_type="ATTESTATION_ADDED",
              summary=f"{matched.affected_predicate} = {body.answer}",
              sources=[attestation.id], detail={"question": matched.question_text})

    old_state = incident.state
    new_state = old_state
    if old_state in ("EVIDENCE_REVIEW", "RECONSTRUCTING", "INGESTING"):
        new_state = "HUMAN_CONTEXT"
    if body.question_id == "q_authorized_payouts" and body.answer == "NO":
        if can_transition(new_state, "INCIDENT_CONFIRMED") or new_state == "HUMAN_CONTEXT":
            new_state = "INCIDENT_CONFIRMED"

    if new_state != old_state:
        incident.state = new_state
        audit_log(db, incident_id=incident_id, actor="SYSTEM", event_type="CASE_STATE_CHANGED",
                  summary=f"{old_state} -> {new_state}", sources=[], detail={})

    db.commit()
    db.refresh(attestation)

    return AttestationResponse(
        id=attestation.id, incident_id=incident_id, question_id=attestation.question_id,
        question_text=attestation.question_text, answer=attestation.answer,
        affected_predicate=attestation.affected_predicate, created_at=attestation.created_at,
        message="Recorded. This does not rewrite financial records; it adds your context to the case.",
        new_state=incident.state,
    )


@router.get("/incident/{incident_id}/recovery-packet")
def get_recovery_packet(incident_id: str, db: Session = Depends(get_tenant_db)):
    if incident_repo.get_incident(db, incident_id) is None:
        raise HTTPException(404, "incident not found")
    packet = build_recovery_packet(db, incident_id)

    incident = incident_repo.get_incident(db, incident_id)
    if can_transition(incident.state, "EXPOSURE_ASSESSED"):
        incident.state = "EXPOSURE_ASSESSED"
    if can_transition(incident.state, "RECOVERY_READY"):
        incident.state = "RECOVERY_READY"
        audit_log(db, incident_id=incident_id, actor="SYSTEM", event_type="RECOVERY_PACKET_GENERATED",
                  summary="Recovery packet generated", sources=[], detail={})
    db.commit()
    return packet


@router.get("/incident/{incident_id}/audit")
def get_audit(incident_id: str, db: Session = Depends(get_tenant_db)):
    events = incident_repo.list_audit_events(db, incident_id)
    return [{
        "id": e.id, "actor": e.actor, "event_type": e.event_type, "summary": e.summary,
        "sources": e.sources, "detail": e.detail, "created_at": e.created_at,
    } for e in events]
