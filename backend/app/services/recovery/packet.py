"""
Recovery Packet assembly. Templates + computed values only -- no narrative
invention of facts. Every material line item carries a source reference so
the frontend can render a clickable provenance affordance next to it.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import entities as m
from app.services.exposure.engine import compute_exposure
from app.services.graph.builder import build_incident_graph


def build_recovery_packet(db: Session, incident_id: str) -> dict:
    incident = db.get(m.Incident, incident_id)
    if incident is None:
        raise ValueError("incident not found")
    merchant = db.get(m.Merchant, incident.merchant_id)

    incident_events = (
        db.query(m.IncidentEvent).filter(m.IncidentEvent.incident_id == incident_id)
        .order_by(m.IncidentEvent.sequence).all()
    )
    fevents = [db.get(m.FinancialEvent, ie.financial_event_id) for ie in incident_events]

    transactions = []
    beneficiaries: dict[str, dict] = {}
    for fe in fevents:
        payout = db.get(m.Payout, fe.source_record_id)
        contact = db.get(m.Contact, payout.contact_id) if payout else None
        transactions.append({
            "payout_id": payout.id if payout else fe.source_record_id,
            "amount": fe.amount,
            "timestamp": fe.timestamp.isoformat(),
            "beneficiary": contact.name if contact else "unknown",
            "beneficiary_contact_id": contact.id if contact else "",
            "status": payout.status if payout else "unknown",
            "source_reference": fe.id,
        })
        if contact:
            beneficiaries[contact.id] = {
                "contact_id": contact.id,
                "name": contact.name,
                "type": contact.type,
                "created_at": contact.created_at.isoformat(),
                "is_new": (contact.created_at >= (incident.window_start or contact.created_at)),
            }

    comms = db.query(m.CommunicationEvent).filter(m.CommunicationEvent.incident_id == incident_id).all()
    communication_evidence = [{
        "id": c.id,
        "channel": c.channel,
        "timestamp": c.timestamp.isoformat(),
        "sender": c.sender_label,
        "body_text": c.body_text,
        "correlation_status": c.correlation_status,
        "source_artifact_id": c.source_artifact_id,
    } for c in comms]

    attestations = (
        db.query(m.HumanAttestation).filter(m.HumanAttestation.incident_id == incident_id)
        .order_by(m.HumanAttestation.created_at).all()
    )
    attestation_rows = [{
        "question": a.question_text, "answer": a.answer, "note": a.note,
        "actor": a.actor, "timestamp": a.created_at.isoformat(),
    } for a in attestations]

    evidence_artifact_ids = {c.source_artifact_id for c in comms}
    evidence_index = []
    for aid in evidence_artifact_ids:
        artifact = db.get(m.EvidenceArtifact, aid)
        if artifact:
            evidence_index.append({
                "artifact_id": artifact.id, "filename": artifact.filename,
                "sha256": artifact.sha256, "source_label": artifact.source_label,
                "extraction_status": artifact.extraction_status,
            })

    exposure = compute_exposure(db, incident_id)

    outstanding_predicates = {"authorization_status", "beneficiary_familiarity", "instruction_origin",
                               "device_control", "dormancy_explanation"}
    answered = {a.affected_predicate for a in attestations}
    outstanding_questions = sorted(outstanding_predicates - answered)

    return {
        "case_id": incident.id,
        "merchant_name": merchant.name if merchant else "",
        "incident_summary": (
            f"{len(transactions)} payouts totaling ₹{sum(t['amount'] for t in transactions):,.0f} "
            f"moved to {len(beneficiaries)} beneficiary(ies) between "
            f"{incident.window_start.strftime('%H:%M:%S') if incident.window_start else '—'} and "
            f"{incident.window_end.strftime('%H:%M:%S') if incident.window_end else '—'}."
        ),
        "incident_window": {
            "start": incident.window_start.isoformat() if incident.window_start else None,
            "end": incident.window_end.isoformat() if incident.window_end else None,
        },
        "incident_evidence_score": incident.incident_evidence_score,
        "score_components": incident.score_components,
        "total_exposure": exposure,
        "chronology": transactions,
        "transaction_table": transactions,
        "beneficiary_information": list(beneficiaries.values()),
        "communication_evidence": communication_evidence,
        "human_attestations": attestation_rows,
        "evidence_index": evidence_index,
        "outstanding_questions": outstanding_questions,
        "official_next_steps": [
            "File a report with your bank's fraud/dispute desk using the payout reference IDs above.",
            "Report to the National Cyber Crime Reporting Portal (cybercrime.gov.in) or dial 1930.",
            "Notify your Razorpay account manager with this case ID for platform-side review.",
            "Preserve the original evidence artifacts (do not forward/delete the source messages).",
        ],
        "state": incident.state,
        "dataset_version": incident.dataset_version,
        "config_version": incident.config_version,
    }
