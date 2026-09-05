"""
Production-shaped data model for FIRST HOUR.

This is deliberately built around Razorpay's actual financial primitives
(Payments, RazorpayX Payouts, Contacts, Fund Accounts, Transfers, Settlements,
Events) rather than one generic "transaction" table, per the architecture doc.

Every table that can be pointed at from a claim, a graph edge, or a recovery
packet line has a stable string ID (not just an autoincrement PK) so that
evidence, audit events, and the frontend can all refer to "PYO_..." /
"FA_..." the way a real integration would.
"""
from __future__ import annotations

import datetime as dt

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def utcnow() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc).replace(tzinfo=None)


# ---------------------------------------------------------------------------
# Core Razorpay-shaped financial primitives
# ---------------------------------------------------------------------------


class Merchant(Base):
    __tablename__ = "merchants"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    category: Mapped[str] = mapped_column(String(80), default="general")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=utcnow)

    is_flagship: Mapped[bool] = mapped_column(Boolean, default=False)


class Employee(Base):
    """An employee/communication-account holder at a merchant. This is the
    node that a compromised-account incident actually happens to."""

    __tablename__ = "employees"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    merchant_id: Mapped[str] = mapped_column(ForeignKey("merchants.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    role: Mapped[str] = mapped_column(String(80), default="finance_ops")
    comm_handle: Mapped[str] = mapped_column(String(120))  # e.g. WhatsApp/phone identity
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=utcnow)


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    merchant_id: Mapped[str] = mapped_column(ForeignKey("merchants.id"), index=True)
    amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(8), default="INR")
    status: Mapped[str] = mapped_column(String(24), default="paid")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=utcnow, index=True)


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id"), index=True)
    merchant_id: Mapped[str] = mapped_column(ForeignKey("merchants.id"), index=True)
    customer_id: Mapped[str] = mapped_column(String(32), index=True)
    amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(8), default="INR")
    status: Mapped[str] = mapped_column(String(24), default="captured")
    method: Mapped[str] = mapped_column(String(24), default="upi")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=utcnow, index=True)


class Contact(Base):
    """A RazorpayX Contact -- the human/entity a payout is made to."""

    __tablename__ = "contacts"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    merchant_id: Mapped[str] = mapped_column(ForeignKey("merchants.id"), index=True)
    name: Mapped[str] = mapped_column(String(160))
    type: Mapped[str] = mapped_column(String(24), default="vendor")  # vendor/employee/customer
    phone: Mapped[str] = mapped_column(String(24), default="")
    email: Mapped[str] = mapped_column(String(160), default="")
    upi_id: Mapped[str] = mapped_column(String(80), default="")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=utcnow, index=True)


class FundAccount(Base):
    __tablename__ = "fund_accounts"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    contact_id: Mapped[str] = mapped_column(ForeignKey("contacts.id"), index=True)
    account_type: Mapped[str] = mapped_column(String(16), default="bank_account")  # or vpa
    masked_bank_account: Mapped[str] = mapped_column(String(40), default="")
    masked_ifsc: Mapped[str] = mapped_column(String(20), default="")
    vpa: Mapped[str] = mapped_column(String(80), default="")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=utcnow, index=True)


class Payout(Base):
    __tablename__ = "payouts"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    merchant_id: Mapped[str] = mapped_column(ForeignKey("merchants.id"), index=True)
    contact_id: Mapped[str] = mapped_column(ForeignKey("contacts.id"), index=True)
    fund_account_id: Mapped[str] = mapped_column(ForeignKey("fund_accounts.id"), index=True)
    amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(8), default="INR")
    purpose: Mapped[str] = mapped_column(String(40), default="vendor_bill")
    mode: Mapped[str] = mapped_column(String(16), default="IMPS")
    narration: Mapped[str] = mapped_column(String(200), default="")
    reference_id: Mapped[str] = mapped_column(String(64), default="")
    status: Mapped[str] = mapped_column(String(24), default="processed", index=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=utcnow, index=True)

    is_injected: Mapped[bool] = mapped_column(Boolean, default=False)


class Transfer(Base):
    """Route/linked-account transfer."""

    __tablename__ = "transfers"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    merchant_id: Mapped[str] = mapped_column(ForeignKey("merchants.id"), index=True)
    source_payment_id: Mapped[str] = mapped_column(String(32), default="")
    destination_account_id: Mapped[str] = mapped_column(String(32), default="")
    amount: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(24), default="processed")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=utcnow, index=True)


class Settlement(Base):
    __tablename__ = "settlements"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    merchant_id: Mapped[str] = mapped_column(ForeignKey("merchants.id"), index=True)
    amount: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(24), default="processed")
    settlement_window_start: Mapped[dt.datetime] = mapped_column(DateTime)
    settlement_window_end: Mapped[dt.datetime] = mapped_column(DateTime)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=utcnow, index=True)


class FinancialEvent(Base):
    """The canonical event model from the architecture doc -- every payment,
    payout, transfer and settlement also gets normalized into one of these so
    the incident engine, graph and audit trail all read from one place."""

    __tablename__ = "financial_events"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    event_type: Mapped[str] = mapped_column(String(32), index=True)  # payment/payout/transfer/settlement
    source_system: Mapped[str] = mapped_column(String(32), default="razorpay")
    source_record_id: Mapped[str] = mapped_column(String(32), index=True)
    merchant_id: Mapped[str] = mapped_column(ForeignKey("merchants.id"), index=True)
    actor_id: Mapped[str] = mapped_column(String(32), default="")  # employee/system actor
    account_id: Mapped[str] = mapped_column(String(32), default="")
    counterparty_id: Mapped[str] = mapped_column(String(32), default="", index=True)  # contact id
    timestamp: Mapped[dt.datetime] = mapped_column(DateTime, index=True)
    amount: Mapped[float] = mapped_column(Float, default=0.0)
    currency: Mapped[str] = mapped_column(String(8), default="INR")
    attributes: Mapped[dict] = mapped_column(JSON, default=dict)
    evidence_refs: Mapped[list] = mapped_column(JSON, default=list)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    extraction_method: Mapped[str] = mapped_column(String(32), default="system_of_record")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=utcnow)


class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    event_type: Mapped[str] = mapped_column(String(64))
    source_object_type: Mapped[str] = mapped_column(String(32))
    source_object_id: Mapped[str] = mapped_column(String(32), index=True)
    merchant_id: Mapped[str] = mapped_column(ForeignKey("merchants.id"), index=True)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=utcnow, index=True)


# ---------------------------------------------------------------------------
# Evidence + extraction
# ---------------------------------------------------------------------------


class EvidenceArtifact(Base):
    __tablename__ = "evidence_artifacts"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    incident_id: Mapped[str] = mapped_column(String(32), index=True, default="")
    merchant_id: Mapped[str] = mapped_column(ForeignKey("merchants.id"), index=True)
    filename: Mapped[str] = mapped_column(String(200))
    mime_type: Mapped[str] = mapped_column(String(80))
    sha256: Mapped[str] = mapped_column(String(64), index=True)
    source_label: Mapped[str] = mapped_column(String(40), default="upload")  # whatsapp/sms/bank/email
    raw_text: Mapped[str] = mapped_column(Text, default="")
    extraction_status: Mapped[str] = mapped_column(String(24), default="pending", index=True)
    uploaded_at: Mapped[dt.datetime] = mapped_column(DateTime, default=utcnow, index=True)


class ExtractedClaim(Base):
    __tablename__ = "extracted_claims"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    source_artifact_id: Mapped[str] = mapped_column(ForeignKey("evidence_artifacts.id"), index=True)
    source_location: Mapped[str] = mapped_column(String(120), default="")
    extraction_method: Mapped[str] = mapped_column(String(40), default="rule_based_extractor")
    claim_type: Mapped[str] = mapped_column(String(40))  # instruction/amount/beneficiary/timestamp
    claim_value: Mapped[dict] = mapped_column(JSON, default=dict)
    verification_status: Mapped[str] = mapped_column(String(24), default="UNVERIFIED", index=True)
    matched_financial_event_id: Mapped[str] = mapped_column(String(40), default="")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=utcnow)


class CommunicationEvent(Base):
    __tablename__ = "communication_events"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    source_artifact_id: Mapped[str] = mapped_column(ForeignKey("evidence_artifacts.id"), index=True)
    incident_id: Mapped[str] = mapped_column(String(32), index=True, default="")
    sender_label: Mapped[str] = mapped_column(String(120))
    channel: Mapped[str] = mapped_column(String(24), default="whatsapp")
    body_text: Mapped[str] = mapped_column(Text)
    mentioned_amount: Mapped[float] = mapped_column(Float, default=0.0)
    mentioned_beneficiary_text: Mapped[str] = mapped_column(String(160), default="")
    resolved_contact_id: Mapped[str] = mapped_column(String(32), default="")
    timestamp: Mapped[dt.datetime] = mapped_column(DateTime, index=True)
    correlation_status: Mapped[str] = mapped_column(String(24), default="UNCORRELATED")  # CORROBORATED/POSSIBLE
    correlated_financial_event_id: Mapped[str] = mapped_column(String(40), default="")


class EntityLink(Base):
    """Result of entity resolution between two records (e.g. a communication
    mention and a Contact, or two Contacts suspected to be the same entity)."""

    __tablename__ = "entity_links"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    left_type: Mapped[str] = mapped_column(String(32))
    left_id: Mapped[str] = mapped_column(String(64), index=True)
    right_type: Mapped[str] = mapped_column(String(32))
    right_id: Mapped[str] = mapped_column(String(64), index=True)
    signal: Mapped[str] = mapped_column(String(40))  # exact_transaction_id / normalized_name / ...
    weight: Mapped[float] = mapped_column(Float)
    decision: Mapped[str] = mapped_column(String(16))  # AUTO_LINK / REVIEW / KEEP_SEPARATE
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=utcnow)


# ---------------------------------------------------------------------------
# Incident, human context, audit
# ---------------------------------------------------------------------------


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    merchant_id: Mapped[str] = mapped_column(ForeignKey("merchants.id"), index=True)
    state: Mapped[str] = mapped_column(String(32), default="INGESTING", index=True)
    scenario: Mapped[str] = mapped_column(String(48), default="")
    incident_evidence_score: Mapped[float] = mapped_column(Float, default=0.0)
    score_components: Mapped[dict] = mapped_column(JSON, default=dict)
    window_start: Mapped[dt.datetime | None] = mapped_column(DateTime, nullable=True)
    window_end: Mapped[dt.datetime | None] = mapped_column(DateTime, nullable=True)
    dataset_version: Mapped[str] = mapped_column(String(24), default="v1")
    config_version: Mapped[str] = mapped_column(String(24), default="v1")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=utcnow, index=True)
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime, default=utcnow)


class IncidentEvent(Base):
    """A financial_event that has been pulled into a specific incident's case
    file (the payouts on the incident spine)."""

    __tablename__ = "incident_events"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    incident_id: Mapped[str] = mapped_column(ForeignKey("incidents.id"), index=True)
    financial_event_id: Mapped[str] = mapped_column(ForeignKey("financial_events.id"), index=True)
    role: Mapped[str] = mapped_column(String(32), default="suspicious_payout")
    sequence: Mapped[int] = mapped_column(Integer, default=0)


class HumanAttestation(Base):
    __tablename__ = "human_attestations"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    incident_id: Mapped[str] = mapped_column(ForeignKey("incidents.id"), index=True)
    question_id: Mapped[str] = mapped_column(String(64))
    question_text: Mapped[str] = mapped_column(String(300))
    answer: Mapped[str] = mapped_column(String(16))  # YES/NO/NOT_SURE
    note: Mapped[str] = mapped_column(String(500), default="")
    actor: Mapped[str] = mapped_column(String(80), default="merchant_user")
    affected_predicate: Mapped[str] = mapped_column(String(120), default="")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=utcnow, index=True)


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    incident_id: Mapped[str] = mapped_column(String(32), index=True, default="")
    actor: Mapped[str] = mapped_column(String(16), default="SYSTEM")  # SYSTEM / HUMAN
    event_type: Mapped[str] = mapped_column(String(48), index=True)
    summary: Mapped[str] = mapped_column(String(300), default="")
    sources: Mapped[list] = mapped_column(JSON, default=list)
    detail: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=utcnow, index=True)


Index("ix_payout_merchant_created", Payout.merchant_id, Payout.created_at)
Index("ix_fevent_merchant_ts", FinancialEvent.merchant_id, FinancialEvent.timestamp)
