"""
Chaos Lab scenario mutations. Each scenario really writes new rows to the
database (new Contact/FundAccount/Payout/CommunicationEvent), then runs the
exact same detector used by the seed script and by a real incident -- there
is no separate "demo path" for the scoring logic itself.
"""
from __future__ import annotations

import datetime as dt
import uuid

from sqlalchemy.orm import Session

from app.audit.logger import log as audit_log
from app.core.tenancy import tenant_scope
from app.models import entities as m
from app.services.incident.detector import create_incident_from_payouts

CHAOS_MERCHANT_ID = "MER_HARBOR"


def _new_contact_and_fund_account(db: Session, merchant_id: str, name: str, created_at: dt.datetime) -> m.Contact:
    contact = m.Contact(
        id=f"CON_{uuid.uuid4().hex[:8]}", merchant_id=merchant_id, name=name, type="vendor",
        phone=f"9{uuid.uuid4().int % 10**9:09d}", upi_id=f"{name.lower().replace(' ', '')}@upi",
        created_at=created_at,
    )
    db.add(contact)
    db.flush()
    fund_account = m.FundAccount(
        id=f"FA_{uuid.uuid4().hex[:8]}", contact_id=contact.id, account_type="vpa",
        vpa=contact.upi_id, created_at=created_at,
    )
    db.add(fund_account)
    db.flush()
    return contact


def _make_payout(db: Session, merchant_id: str, contact: m.Contact, amount: float,
                  created_at: dt.datetime, reference_id: str = "") -> m.Payout:
    fund_account = db.query(m.FundAccount).filter(m.FundAccount.contact_id == contact.id).first()
    payout = m.Payout(
        id=f"PYO_{uuid.uuid4().hex[:8]}", merchant_id=merchant_id, contact_id=contact.id,
        fund_account_id=fund_account.id, amount=amount, purpose="vendor_bill", mode="IMPS",
        narration="Urgent vendor settlement", reference_id=reference_id or uuid.uuid4().hex[:10],
        status="processed", created_at=created_at, is_injected=True,
    )
    db.add(payout)
    db.flush()
    return payout


def _add_communication(db: Session, artifact_id: str, incident_id: str, sender: str, body: str,
                        amount: float, beneficiary_text: str, timestamp: dt.datetime,
                        correlated_financial_event_id: str, resolved_contact_id: str,
                        status: str = "CORROBORATED") -> m.CommunicationEvent:
    comm = m.CommunicationEvent(
        id=f"COM_{uuid.uuid4().hex[:8]}", source_artifact_id=artifact_id, incident_id=incident_id,
        sender_label=sender, channel="whatsapp", body_text=body, mentioned_amount=amount,
        mentioned_beneficiary_text=beneficiary_text, resolved_contact_id=resolved_contact_id,
        timestamp=timestamp, correlation_status=status,
        correlated_financial_event_id=correlated_financial_event_id,
    )
    db.add(comm)
    db.flush()
    return comm


def _ensure_artifact(db: Session, merchant_id: str, incident_id: str, filename: str, text: str) -> m.EvidenceArtifact:
    import hashlib
    artifact = m.EvidenceArtifact(
        id=f"EVD_{uuid.uuid4().hex[:10]}", incident_id=incident_id, merchant_id=merchant_id,
        filename=filename, mime_type="text/plain", sha256=hashlib.sha256(text.encode()).hexdigest(),
        source_label="whatsapp", raw_text=text, extraction_status="text_ready",
    )
    db.add(artifact)
    db.flush()
    return artifact


def inject_scenario(db: Session, scenario: str, merchant_id: str = CHAOS_MERCHANT_ID) -> dict:
    merchant = db.get(m.Merchant, merchant_id)
    if merchant is None:
        raise ValueError(f"Unknown merchant: {merchant_id}")
    # db arrives here unscoped (from get_system_db) since we don't know the
    # tenant until we've looked up the merchant. Every row this function
    # creates from here on auto-stamps to the merchant's own tenant.
    db.set_tenant(merchant.tenant_id)

    now = dt.datetime.now(dt.timezone.utc).replace(tzinfo=None)
    incident_id = f"INC_CHAOS_{uuid.uuid4().hex[:6].upper()}"
    audit_trail: list[str] = []
    payout_ids: list[str] = []

    if scenario == "new_beneficiary_burst":
        contact = _new_contact_and_fund_account(db, merchant_id, "Crestline Vendor Co", now - dt.timedelta(minutes=5))
        p1 = _make_payout(db, merchant_id, contact, 8_50_000, now - dt.timedelta(minutes=5))
        p2 = _make_payout(db, merchant_id, contact, 8_50_000, now - dt.timedelta(minutes=2))
        p3 = _make_payout(db, merchant_id, contact, 8_50_000, now)
        payout_ids = [p1.id, p2.id, p3.id]
        artifact = _ensure_artifact(db, merchant_id, incident_id, "whatsapp_export.txt",
                                     "Urgent: release pending vendor dues to Crestline Vendor Co today, "
                                     "Rs 8,50,000 per invoice, don't call finance to confirm.")
        _add_communication(db, artifact.id, incident_id, "Unknown (claimed: Finance Head)",
                            artifact.raw_text, 8_50_000, "Crestline Vendor Co", now - dt.timedelta(minutes=6),
                            f"FEV_PYO_{p1.id}", contact.id, "CORROBORATED")
        audit_trail = ["FINANCIAL_EVENT_CREATED", "BASELINE_DEVIATION", "INCIDENT_DETECTED",
                       "GRAPH_UPDATED", "EVIDENCE_CORRELATED", "HUMAN_CONTEXT_REQUIRED"]

    elif scenario == "executive_impersonation":
        contact = _new_contact_and_fund_account(db, merchant_id, "Meridian Consulting LLP", now - dt.timedelta(minutes=3))
        p1 = _make_payout(db, merchant_id, contact, 22_00_000, now)
        payout_ids = [p1.id]
        artifact = _ensure_artifact(db, merchant_id, incident_id, "whatsapp_ceo_impersonation.txt",
                                     "This is urgent and confidential -- I need you to process a payment to "
                                     "Meridian Consulting LLP immediately, Rs 22,00,000, I'm in a board meeting "
                                     "and can't take calls right now.")
        _add_communication(db, artifact.id, incident_id, "Unknown (claimed: CEO)", artifact.raw_text,
                            22_00_000, "Meridian Consulting LLP", now - dt.timedelta(minutes=4),
                            f"FEV_PYO_{p1.id}", contact.id, "CORROBORATED")
        audit_trail = ["FINANCIAL_EVENT_CREATED", "BASELINE_DEVIATION", "INCIDENT_DETECTED",
                       "GRAPH_UPDATED", "EVIDENCE_CORRELATED", "HUMAN_CONTEXT_REQUIRED"]

    elif scenario == "dormant_vendor_activation":
        old_contact = (
            db.query(m.Contact)
            .filter(m.Contact.merchant_id == merchant_id, m.Contact.type == "vendor")
            .order_by(m.Contact.created_at.asc()).first()
        )
        if old_contact is None:
            old_contact = _new_contact_and_fund_account(db, merchant_id, "Silverline Traders",
                                                          now - dt.timedelta(days=280))
        p1 = _make_payout(db, merchant_id, old_contact, 6_40_000, now)
        payout_ids = [p1.id]
        artifact = _ensure_artifact(db, merchant_id, incident_id, "bank_sms_export.txt",
                                     f"Reactivating dormant vendor account for {old_contact.name} after a long "
                                     "gap -- please process the pending settlement today.")
        _add_communication(db, artifact.id, incident_id, "Unknown", artifact.raw_text, 6_40_000,
                            old_contact.name, now - dt.timedelta(minutes=2), f"FEV_PYO_{p1.id}",
                            old_contact.id, "POSSIBLE")
        audit_trail = ["FINANCIAL_EVENT_CREATED", "BASELINE_DEVIATION", "INCIDENT_DETECTED",
                       "GRAPH_UPDATED", "EVIDENCE_CORRELATED", "HUMAN_CONTEXT_REQUIRED"]

    elif scenario == "duplicate_payout":
        recent_contact = (
            db.query(m.Contact).filter(m.Contact.merchant_id == merchant_id)
            .order_by(m.Contact.created_at.desc()).first()
        )
        if recent_contact is None:
            recent_contact = _new_contact_and_fund_account(db, merchant_id, "Oakridge Supplies", now)
        shared_ref = uuid.uuid4().hex[:10]
        p1 = _make_payout(db, merchant_id, recent_contact, 3_10_000, now - dt.timedelta(minutes=1),
                           reference_id=shared_ref)
        p2 = _make_payout(db, merchant_id, recent_contact, 3_10_000, now, reference_id=shared_ref)
        payout_ids = [p1.id, p2.id]
        artifact = _ensure_artifact(db, merchant_id, incident_id, "payout_batch_note.txt",
                                     "Same invoice reference submitted twice in the payout batch -- possible "
                                     "duplicate settlement.")
        audit_trail = ["FINANCIAL_EVENT_CREATED", "BASELINE_DEVIATION", "INCIDENT_DETECTED",
                       "GRAPH_UPDATED", "HUMAN_CONTEXT_REQUIRED"]
    else:
        raise ValueError(f"Unknown scenario: {scenario}")

    incident = create_incident_from_payouts(
        db, incident_id=incident_id, merchant_id=merchant_id, payout_ids=payout_ids,
        scenario=scenario,
    )

    return {
        "incident_id": incident.id,
        "scenario": scenario,
        "incident_evidence_score": incident.incident_evidence_score,
        "score_components": incident.score_components,
        "payout_ids": payout_ids,
        "audit_trail": audit_trail,
    }
