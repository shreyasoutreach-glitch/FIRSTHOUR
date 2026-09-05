"""Thin data-access layer for incidents. Services call these instead of
constructing raw queries inline, so the query shape for "give me an
incident's timeline" exists in exactly one place."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import entities as m


def get_incident(db: Session, incident_id: str) -> m.Incident | None:
    return db.get(m.Incident, incident_id)


def list_incident_financial_events(db: Session, incident_id: str) -> list[m.FinancialEvent]:
    incident_events = (
        db.query(m.IncidentEvent).filter(m.IncidentEvent.incident_id == incident_id)
        .order_by(m.IncidentEvent.sequence).all()
    )
    ids = [ie.financial_event_id for ie in incident_events]
    events = db.query(m.FinancialEvent).filter(m.FinancialEvent.id.in_(ids)).all()
    by_id = {e.id: e for e in events}
    return [by_id[i] for i in ids if i in by_id]


def list_communications(db: Session, incident_id: str) -> list[m.CommunicationEvent]:
    return (
        db.query(m.CommunicationEvent).filter(m.CommunicationEvent.incident_id == incident_id)
        .order_by(m.CommunicationEvent.timestamp).all()
    )


def list_attestations(db: Session, incident_id: str) -> list[m.HumanAttestation]:
    return (
        db.query(m.HumanAttestation).filter(m.HumanAttestation.incident_id == incident_id)
        .order_by(m.HumanAttestation.created_at).all()
    )


def list_audit_events(db: Session, incident_id: str | None = None) -> list[m.AuditEvent]:
    q = db.query(m.AuditEvent)
    if incident_id:
        q = q.filter(m.AuditEvent.incident_id == incident_id)
    return q.order_by(m.AuditEvent.created_at).all()
