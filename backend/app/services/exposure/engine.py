"""
Exposure engine. The architecture doc is explicit that CONFIRMED_MOVED,
PENDING, ATTEMPTED and RELATED must never be collapsed into one frightening
total -- each is its own deterministic aggregation, and every total must
drill down to exact payout/payment IDs rather than being reported as an
opaque number.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import entities as m
from app.services.graph.builder import blast_radius


def compute_exposure(db: Session, incident_id: str) -> dict:
    incident_events = (
        db.query(m.IncidentEvent).filter(m.IncidentEvent.incident_id == incident_id).all()
    )
    fevent_ids = [ie.financial_event_id for ie in incident_events]
    fevents = db.query(m.FinancialEvent).filter(m.FinancialEvent.id.in_(fevent_ids)).all()

    confirmed_ids, pending_ids, attempted_ids = [], [], []
    confirmed_total = pending_total = attempted_total = 0.0
    contact_ids: set[str] = set()

    for fe in fevents:
        payout = db.get(m.Payout, fe.source_record_id) if fe.event_type == "payout" else None
        status = payout.status if payout else "processed"
        if payout:
            contact_ids.add(payout.contact_id)

        if status == "processed":
            confirmed_ids.append(fe.id)
            confirmed_total += fe.amount
        elif status in ("queued", "pending", "processing"):
            pending_ids.append(fe.id)
            pending_total += fe.amount
        elif status in ("failed", "reversed", "cancelled"):
            attempted_ids.append(fe.id)
            attempted_total += fe.amount
        else:
            confirmed_ids.append(fe.id)
            confirmed_total += fe.amount

    radius = blast_radius(db, list(contact_ids), depth=3) if contact_ids else {
        "connected_event_count": 0, "connected_amount": 0.0, "affected_entities": 0,
        "affected_fund_accounts": 0, "pending_exposure": 0.0, "traversal_depth": 3,
    }
    related_total = max(0.0, radius["connected_amount"] - confirmed_total - pending_total)

    return {
        "confirmed_moved": {"total": confirmed_total, "financial_event_ids": confirmed_ids},
        "pending": {"total": pending_total, "financial_event_ids": pending_ids},
        "attempted": {"total": attempted_total, "financial_event_ids": attempted_ids},
        "related": {
            "total": related_total,
            "affected_entities": radius["affected_entities"],
            "affected_fund_accounts": radius["affected_fund_accounts"],
        },
        "blast_radius": radius,
    }
