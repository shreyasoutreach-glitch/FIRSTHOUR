from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import entities as m


def get_merchant(db: Session, merchant_id: str) -> m.Merchant | None:
    return db.get(m.Merchant, merchant_id)


def get_flagship_merchant(db: Session) -> m.Merchant | None:
    return db.query(m.Merchant).filter(m.Merchant.is_flagship.is_(True)).first()


def merchant_payout_history(db: Session, merchant_id: str) -> list[m.Payout]:
    return (
        db.query(m.Payout).filter(m.Payout.merchant_id == merchant_id)
        .order_by(m.Payout.created_at).all()
    )
