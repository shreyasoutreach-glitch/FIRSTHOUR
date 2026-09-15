from __future__ import annotations
from decimal import Decimal

def _clean_decimals(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    if isinstance(obj, dict):
        return {k: _clean_decimals(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_clean_decimals(x) for x in obj]
    return obj

"""Every important operation writes one of these. This is what powers the
Audit screen's event stream + provenance inspector."""


import uuid

from sqlalchemy.orm import Session

from app.models import entities as m


def log(db: Session, *, incident_id: str, actor: str, event_type: str, summary: str,
        sources: list[str] | None = None, detail: dict | None = None,
        actor_user_id: str = "", before_state: dict | None = None,
        after_state: dict | None = None) -> m.AuditEvent:
    event = m.AuditEvent(
        id=f"AUD_{uuid.uuid4().hex[:12]}",
        incident_id=incident_id,
        actor=actor,
        actor_user_id=actor_user_id,
        event_type=event_type,
        summary=summary,
        sources=sources or [],
        detail=detail or {},
        before_state=before_state or {},
        after_state=after_state or {},
    )
    db.add(event)
    db.flush()
    return event


