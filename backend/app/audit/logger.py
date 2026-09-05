"""Every important operation writes one of these. This is what powers the
Audit screen's event stream + provenance inspector."""
from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.models import entities as m


def log(db: Session, *, incident_id: str, actor: str, event_type: str, summary: str,
        sources: list[str] | None = None, detail: dict | None = None) -> m.AuditEvent:
    event = m.AuditEvent(
        id=f"AUD_{uuid.uuid4().hex[:12]}",
        incident_id=incident_id,
        actor=actor,
        event_type=event_type,
        summary=summary,
        sources=sources or [],
        detail=detail or {},
    )
    db.add(event)
    db.flush()
    return event
