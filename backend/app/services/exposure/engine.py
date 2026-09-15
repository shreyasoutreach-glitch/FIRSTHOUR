from __future__ import annotations
from sqlalchemy.orm import Session
from app.models import entities as m
from app.services.graph.builder import blast_radius
from decimal import Decimal

def compute_exposure(db: Session, incident_id: str = None, fevents: list[m.FinancialEvent] = None) -> dict:
    if fevents is None and incident_id is not None:
        incident_events = (
            db.query(m.IncidentEvent).filter(m.IncidentEvent.incident_id == incident_id).all()
        )
        fevent_ids = [ie.financial_event_id for ie in incident_events]
        fevents = db.query(m.FinancialEvent).filter(m.FinancialEvent.id.in_(fevent_ids)).all()
    elif fevents is None:
        fevents = []

    confirmed_ids, pending_ids, attempted_ids = [], [], []
    confirmed_total = pending_total = attempted_total = Decimal(0)
    contact_ids: set[str] = set()

    originals = {}
    refunds_by_original = {}
    reversals_by_original = {}

    for fe in fevents:
        fe.attributes = fe.attributes or {}
        if fe.event_type == "payout":
            payout = db.get(m.Payout, fe.source_record_id) if db else None
            if payout:
                contact_ids.add(payout.contact_id)
            if "_legacy_status" not in fe.attributes:
                status = payout.status if payout else "processed"
                fe.attributes["_legacy_status"] = status
            originals[fe.id] = fe
        elif fe.event_type == "payment":
            if "_legacy_status" not in fe.attributes:
                fe.attributes["_legacy_status"] = "processed"
            originals[fe.id] = fe
        elif fe.event_type == "refund":
            orig_id = fe.attributes.get("original_event_id")
            if orig_id:
                refunds_by_original.setdefault(orig_id, []).append(fe)
        elif fe.event_type == "reversal":
            orig_id = fe.attributes.get("original_event_id")
            if orig_id:
                reversals_by_original.setdefault(orig_id, []).append(fe)
        else:
            originals[fe.id] = fe

    for orig_id, fe in originals.items():
        status = fe.attributes.get("_legacy_status", "processed")
        if status in ("failed", "cancelled"):
            attempted_ids.append(fe.id)
            attempted_total += fe.amount
            continue
        elif status in ("queued", "pending", "processing"):
            pending_ids.append(fe.id)
            pending_total += fe.amount
            continue
        
        confirmed = fe.amount
        
        is_reversed = False
        revs = reversals_by_original.get(orig_id, [])
        if revs or status == "reversed":
            is_reversed = True
            
        if is_reversed:
            attempted_ids.append(fe.id)
            attempted_total += fe.amount
            continue

        total_refunded = Decimal(0)
        seen_refund_ids = set()
        for ref in refunds_by_original.get(orig_id, []):
            if ref.id not in seen_refund_ids:
                total_refunded += ref.amount
                seen_refund_ids.add(ref.id)
                
        net_amount = confirmed - total_refunded
        if net_amount < Decimal(0):
            net_amount = Decimal(0)
            
        confirmed_ids.append(fe.id)
        confirmed_total += net_amount

    radius = blast_radius(db, list(contact_ids), depth=3) if contact_ids and db else {
        "connected_event_count": 0, "connected_amount": Decimal(0), "affected_entities": 0,
        "affected_fund_accounts": 0, "pending_exposure": Decimal(0), "traversal_depth": 3,
    }
    
    radius_conn = Decimal(str(radius.get("connected_amount", "0")))
    related_total = max(Decimal(0), radius_conn - confirmed_total - pending_total)

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
