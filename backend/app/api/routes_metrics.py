from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.authz import get_tenant_db
from app.evaluation.harness import run_full_evaluation
from app.models import entities as m

router = APIRouter(tags=["metrics"])


@router.get("/metrics")
def get_metrics(db: Session = Depends(get_tenant_db)):
    return {
        "merchants": db.query(m.Merchant).count(),
        "payments": db.query(m.Payment).count(),
        "payouts": db.query(m.Payout).count(),
        "contacts": db.query(m.Contact).count(),
        "fund_accounts": db.query(m.FundAccount).count(),
        "financial_events": db.query(m.FinancialEvent).count(),
        "incidents": db.query(m.Incident).count(),
        "evidence_artifacts": db.query(m.EvidenceArtifact).count(),
        "extracted_claims": db.query(m.ExtractedClaim).count(),
        "audit_events": db.query(m.AuditEvent).count(),
    }


@router.get("/evaluation")
def get_evaluation():
    return run_full_evaluation()
