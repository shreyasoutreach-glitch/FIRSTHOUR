from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.authz import get_tenant_db, require_permission
from app.models import entities as m
from app.services.integrations import razorpayx

router = APIRouter(tags=["merchant"])


def _upsert_external_payout(db: Session, merchant_id: str, raw: dict) -> str:
    n = razorpayx.normalize_payout(raw)
    payout_id = n["external_id"]
    if not payout_id:
        return ""

    existing = db.get(m.Payout, payout_id)
    if existing:
        existing.amount = n["amount"]
        existing.currency = n["currency"]
        existing.purpose = n["purpose"]
        existing.mode = n["mode"]
        existing.narration = n["narration"]
        existing.reference_id = n["reference_id"]
        existing.status = n["status"]
        existing.created_at = n["created_at"]
        return payout_id

    contact_id = n["contact_id"] or f"RZP_CONTACT_{payout_id}"
    contact = db.get(m.Contact, contact_id)
    if contact is None:
        contact = m.Contact(
            id=contact_id,
            merchant_id=merchant_id,
            name=n["contact_name"],
            type=n["contact_type"],
            phone=n["phone"],
            email=n["email"],
            upi_id=n["vpa"],
            created_at=n["created_at"],
        )
        db.add(contact)
        db.flush()

    fund_id = n["fund_account_id"] or f"RZP_FA_{payout_id}"
    fund = db.get(m.FundAccount, fund_id)
    if fund is None:
        fund = m.FundAccount(
            id=fund_id,
            contact_id=contact.id,
            account_type=n["account_type"],
            masked_bank_account=n["masked_bank_account"],
            masked_ifsc=n["masked_ifsc"],
            vpa=n["vpa"],
            created_at=n["created_at"],
        )
        db.add(fund)
        db.flush()

    db.add(
        m.Payout(
            id=payout_id,
            merchant_id=merchant_id,
            contact_id=contact.id,
            fund_account_id=fund.id,
            amount=n["amount"],
            currency=n["currency"],
            purpose=n["purpose"],
            mode=n["mode"],
            narration=n["narration"],
            reference_id=n["reference_id"],
            status=n["status"],
            created_at=n["created_at"],
            is_injected=False,
        )
    )
    return payout_id


@router.get("/merchant/{merchant_id}/connection")
def get_connection_status(merchant_id: str, db: Session = Depends(get_tenant_db)):
    merchant = db.get(m.Merchant, merchant_id)
    if merchant is None:
        raise HTTPException(404, "merchant not found")

    live = razorpayx.configured()
    return {
        "merchant_id": merchant.id,
        "merchant_name": merchant.name,
        "workspace": "RazorpayX Live" if live else "Demo / Sandbox Workspace",
        "connected": live,
        "read_only": not live,
        "scopes": ["Payments", "Payouts", "Contacts", "Fund Accounts", "Events"],
        "provider": "razorpayx",
        "integration_status": "configured" if live else "not_configured",
    }


@router.post("/merchant/{merchant_id}/sync")
def sync_razorpay_payouts(
    merchant_id: str,
    db: Session = Depends(get_tenant_db),
    _user: m.User = Depends(require_permission("INVESTIGATE")),
):
    merchant = db.get(m.Merchant, merchant_id)
    if merchant is None:
        raise HTTPException(404, "merchant not found")

    try:
        raw_payouts = razorpayx.fetch_payouts()
    except razorpayx.RazorpayXNotConfigured as exc:
        raise HTTPException(503, str(exc))
    except razorpayx.RazorpayXAPIError as exc:
        raise HTTPException(exc.status, exc.detail)

    imported = []
    for raw in raw_payouts:
        payout_id = _upsert_external_payout(db, merchant_id, raw)
        if payout_id:
            imported.append(payout_id)

    db.commit()
    return {
        "provider": "razorpayx",
        "merchant_id": merchant_id,
        "fetched": len(raw_payouts),
        "imported_or_updated": len(imported),
        "payout_ids": imported,
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
