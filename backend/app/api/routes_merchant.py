from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.authz import get_tenant_db
from app.models import entities as m

router = APIRouter(tags=["merchant"])


@router.get("/merchant/{merchant_id}/connection")
def get_connection_status(merchant_id: str, db: Session = Depends(get_tenant_db)):
    merchant = db.get(m.Merchant, merchant_id)
    if merchant is None:
        raise HTTPException(404, "merchant not found")
    return {
        "merchant_id": merchant.id,
        "merchant_name": merchant.name,
        "workspace": "Demo / Sandbox Workspace",
        "connected": True,
        "read_only": True,
        "scopes": ["Payments", "Payouts", "Contacts", "Fund Accounts", "Events"],
    }


@router.get("/merchant/{merchant_id}/baseline")
def get_baseline(merchant_id: str, db: Session = Depends(get_tenant_db)):
    from app.services.incident.detector import build_baseline

    baseline = build_baseline(db, merchant_id)
    contact_count = db.query(m.Contact).filter(m.Contact.merchant_id == merchant_id).count()
    payout_count = db.query(m.Payout).filter(m.Payout.merchant_id == merchant_id, m.Payout.is_injected.is_(False)).count()
    return {
        "merchant_id": merchant_id,
        "median_payout": baseline.median_payout,
        "mad_payout": baseline.mad_payout,
        "largest_historical_payout": baseline.largest_historical_payout,
        "beneficiary_count": contact_count,
        "historical_payout_count": payout_count,
        "normal_hours": f"{baseline.normal_hour_start:02d}:00-{baseline.normal_hour_end:02d}:30",
    }
