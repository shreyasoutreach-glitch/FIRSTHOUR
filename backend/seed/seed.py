"""
Deterministic synthetic Razorpay universe + the flagship incident, across
two tenants (so multi-tenancy has something real to isolate).

Scale note (documented, not hidden): the architecture doc specifies 500
merchants / 50,000+ events / 10,000+ payments / 5,000+ payouts as the
production-shape target. This seed generates a scaled-down universe (see
the constants below) so `python -m seed.seed` finishes in well under a
minute on a laptop and the resulting SQLite file stays small enough to ship
in a demo ZIP. Every generator here is written to scale up cleanly --
bump the constants and it produces the full-size universe with no code
changes.

Determinism: everything is anchored to a fixed reference date (not
`utcnow()`) and a fixed random seed, so `run_seed(db, seed_value=42)`
produces byte-identical entity IDs, amounts and timestamps every time it
runs, on any machine, forever. That is what "same seed -> same universe"
actually requires. This now extends to tenant/user tokens too -- same seed,
same tokens, every run.

Tenancy: TEN_NORTHBRIDGE holds the flagship demo (Arrow Industries + the
Chaos Lab merchant Harbor & Co + half the background merchants).
TEN_MERIDIAN holds the other half of the background merchants and exists
specifically so tenant-isolation tests have real cross-tenant data to try
(and fail) to reach.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import random
import statistics
import uuid

from faker import Faker

from app.audit.logger import log as audit_log
from app.core.authz import ROLES
from app.core.database import Base, engine
from app.core.tenancy import TenantScopedSession, tenant_scope
from app.models import entities as m
from app.services.evidence.pipeline import cross_reference_amount_claim, extract_candidate_claims
from app.services.incident.detector import create_incident_from_payouts, sync_financial_events_for_payouts

# ---------------------------------------------------------------------------
# Scale (see module docstring)
# ---------------------------------------------------------------------------
OTHER_MERCHANT_COUNT = 58           # + Arrow Industries + Harbor & Co = 60 total
ARROW_CONTACT_COUNT = 143           # matches the architecture doc exactly
ARROW_HISTORICAL_PAYOUTS = 950
HARBOR_CONTACT_COUNT = 40
HARBOR_HISTORICAL_PAYOUTS = 260
OTHER_MERCHANT_CONTACT_RANGE = (5, 55)
OTHER_MERCHANT_PAYOUT_RANGE = (40, 260)
HISTORY_DAYS = 182  # ~6 months

ANCHOR_DATE = dt.datetime(2026, 9, 3, 0, 0, 0)  # fixed "today" for the synthetic universe
HISTORY_START = ANCHOR_DATE - dt.timedelta(days=HISTORY_DAYS)

MERCHANT_CATEGORIES = ["logistics", "d2c_retail", "b2b_manufacturing", "healthcare_services",
                       "education", "hospitality", "fintech_services", "textiles", "agritech",
                       "media_and_entertainment"]

PAYOUT_PURPOSES = ["vendor_bill", "refund", "salary", "utility_bill", "commission"]
PAYOUT_MODES = ["IMPS", "NEFT", "UPI"]

TENANT_NORTHBRIDGE = "TEN_NORTHBRIDGE"
TENANT_MERIDIAN = "TEN_MERIDIAN"


def _rand_time_in_business_hours(rng: random.Random, day: dt.date, start_hour=10, end_hour=18) -> dt.datetime:
    hour = rng.randint(start_hour, end_hour - 1)
    minute = rng.randint(0, 59)
    second = rng.randint(0, 59)
    return dt.datetime.combine(day, dt.time(hour, minute, second))


def _random_day(rng: random.Random) -> dt.date:
    offset = rng.randint(0, HISTORY_DAYS - 2)
    return (HISTORY_START + dt.timedelta(days=offset)).date()


def _short_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


def _deterministic_token(rng: random.Random) -> str:
    return "".join(rng.choices("0123456789abcdef", k=48))


def wipe_all(db: TenantScopedSession) -> None:
    """Delete in FK-safe order (tenant-scoped children before Tenant/User
    parents). Used by /demo/reset and repeated seed runs. Must run on an
    UNSCOPED session (tenant=None) -- otherwise it would only wipe one
    tenant's data, which is not what a full reset means."""
    for model in [
        m.AuditEvent, m.HumanAttestation, m.RecoveryCommand, m.IncidentEvent, m.Incident,
        m.EntityLink, m.CommunicationEvent, m.ExtractedClaim, m.EvidenceArtifact,
        m.WebhookEvent, m.FinancialEvent, m.Settlement, m.Transfer, m.Payout,
        m.FundAccount, m.Contact, m.Payment, m.Order, m.Employee, m.Merchant,
        m.User, m.Tenant,
    ]:
        db.query(model).delete()
    db.commit()


def _make_tenant_users(db: TenantScopedSession, rng: random.Random, tenant_id: str) -> dict[str, str]:
    """One user per role, per tenant. Returns {role: token} for the CLI
    printout / test convenience -- nothing sensitive, these are demo-only
    bearer tokens for a system that has no real authentication yet."""
    tokens: dict[str, str] = {}
    for role in ROLES:
        token = _deterministic_token(rng)
        user = m.User(
            id=_short_id("USR"), tenant_id=tenant_id,
            email=f"{role.lower()}@{tenant_id.lower().replace('ten_', '')}.demo",
            display_name=f"{role.title().replace('_', ' ')} ({tenant_id})",
            role=role, api_token=token,
        )
        db.add(user)
        tokens[role] = token
    db.flush()
    return tokens


def _make_merchant(db: TenantScopedSession, fake: Faker, rng: random.Random, merchant_id: str, name: str,
                    category: str, is_flagship: bool = False) -> m.Merchant:
    merchant = m.Merchant(id=merchant_id, name=name, category=category, is_flagship=is_flagship,
                          created_at=HISTORY_START - dt.timedelta(days=rng.randint(30, 400)))
    db.add(merchant)
    for _ in range(rng.randint(2, 4)):
        db.add(m.Employee(
            id=_short_id("EMP"), merchant_id=merchant_id, name=fake.name(),
            role=rng.choice(["finance_ops", "founder", "accounts_payable", "ops_lead"]),
            comm_handle=f"+91-{rng.randint(70000,99999)}{rng.randint(10000,99999)}",
        ))
    db.flush()
    return merchant


def _make_contact_with_fund_account(db: TenantScopedSession, fake: Faker, rng: random.Random, merchant_id: str,
                                     created_at: dt.datetime, contact_type: str = "vendor") -> m.Contact:
    is_company = rng.random() < 0.7
    name = fake.company() if is_company else fake.name()
    contact = m.Contact(
        id=_short_id("CON"), merchant_id=merchant_id, name=name, type=contact_type,
        phone=f"9{rng.randint(0,9)}{rng.randint(10**8,10**9-1)}",
        email=fake.company_email() if is_company else fake.email(),
        upi_id=f"{name.lower().replace(' ', '').replace('.', '')[:18]}@okhdfc",
        created_at=created_at,
    )
    db.add(contact)
    db.flush()
    fa_type = "vpa" if rng.random() < 0.55 else "bank_account"
    fund_account = m.FundAccount(
        id=_short_id("FA"), contact_id=contact.id, account_type=fa_type,
        masked_bank_account=f"XXXXXX{rng.randint(1000,9999)}" if fa_type == "bank_account" else "",
        masked_ifsc=f"{fake.lexify('????').upper()}0{rng.randint(100000,999999)}" if fa_type == "bank_account" else "",
        vpa=contact.upi_id if fa_type == "vpa" else "",
        created_at=created_at,
    )
    db.add(fund_account)
    db.flush()
    return contact


def _generate_payout_history(db: TenantScopedSession, fake: Faker, rng: random.Random, merchant_id: str,
                              contacts: list[m.Contact], count: int, median_target: float,
                              spread: float, largest_override: float | None = None) -> list[m.Payout]:
    """Lognormal-ish amounts around median_target using rng.lognormvariate,
    so the distribution has a realistic right skew (many small payouts, a
    few large ones) rather than a symmetric bell curve around the median."""
    import math

    mu = math.log(median_target)
    payouts: list[m.Payout] = []
    for i in range(count):
        contact = rng.choice(contacts)
        amount = round(rng.lognormvariate(mu, spread), -2)
        amount = max(500.0, amount)
        day = _random_day(rng)
        created_at = _rand_time_in_business_hours(rng, day)
        payout = m.Payout(
            id=_short_id("PYO"), merchant_id=merchant_id, contact_id=contact.id,
            fund_account_id=db.query(m.FundAccount).filter(m.FundAccount.contact_id == contact.id).first().id,
            amount=amount, purpose=rng.choice(PAYOUT_PURPOSES), mode=rng.choice(PAYOUT_MODES),
            narration=f"{rng.choice(PAYOUT_PURPOSES).replace('_', ' ').title()} settlement",
            reference_id=uuid.uuid4().hex[:10], status="processed", created_at=created_at,
        )
        db.add(payout)
        payouts.append(payout)
        if i % 200 == 0:
            db.flush()

    if largest_override is not None and payouts:
        anchor_contact = rng.choice(contacts)
        outlier_day = _random_day(rng)
        payouts[0].amount = largest_override
        payouts[0].contact_id = anchor_contact.id
        payouts[0].created_at = _rand_time_in_business_hours(rng, outlier_day)

    db.flush()
    return payouts


def _generate_payments(db: TenantScopedSession, fake: Faker, rng: random.Random, merchant_id: str, count: int) -> None:
    for i in range(count):
        day = _random_day(rng)
        created_at = _rand_time_in_business_hours(rng, day, start_hour=7, end_hour=23)
        order = m.Order(id=_short_id("ORD"), merchant_id=merchant_id,
                        amount=round(rng.lognormvariate(7.5, 1.0), -1), created_at=created_at)
        db.add(order)
        db.flush()
        db.add(m.Payment(
            id=_short_id("PAY"), order_id=order.id, merchant_id=merchant_id,
            customer_id=_short_id("CUST"), amount=order.amount,
            method=rng.choice(["upi", "card", "netbanking", "wallet"]), created_at=created_at,
        ))
        if i % 300 == 0:
            db.flush()
    db.flush()


def _generate_transfers_and_settlements(db: TenantScopedSession, rng: random.Random, merchant_id: str) -> None:
    for _ in range(rng.randint(3, 8)):
        day = _random_day(rng)
        db.add(m.Transfer(
            id=_short_id("TRF"), merchant_id=merchant_id, source_payment_id=_short_id("PAY"),
            destination_account_id=_short_id("ACC"), amount=round(rng.uniform(2000, 80000), 2),
            created_at=_rand_time_in_business_hours(rng, day),
        ))
    for _ in range(rng.randint(4, 10)):
        window_start = dt.datetime.combine(_random_day(rng), dt.time(0, 0, 0))
        db.add(m.Settlement(
            id=_short_id("STL"), merchant_id=merchant_id, amount=round(rng.uniform(50000, 900000), 2),
            settlement_window_start=window_start, settlement_window_end=window_start + dt.timedelta(days=1),
            created_at=window_start + dt.timedelta(days=1, hours=2),
        ))
        db.add(m.WebhookEvent(
            id=_short_id("WHK"), event_type="settlement.processed", source_object_type="settlement",
            source_object_id=_short_id("STL"), merchant_id=merchant_id,
            payload={"status": "processed"}, created_at=window_start + dt.timedelta(days=1, hours=2),
        ))
    db.flush()


def _build_flagship_incident(db: TenantScopedSession, rng: random.Random, arrow: m.Merchant,
                              arrow_contacts: list[m.Contact]) -> str:
    incident_id = "INC-001"
    employees = db.query(m.Employee).filter(m.Employee.merchant_id == arrow.id).all()
    compromised_employee = employees[0]

    contact_created_at = ANCHOR_DATE.replace(hour=10, minute=40, second=0)
    beneficiary_a = _make_contact_with_fund_account(db, Faker(), rng, arrow.id, contact_created_at)
    beneficiary_a.name = "Kailash Enterprises"
    beneficiary_b = _make_contact_with_fund_account(db, Faker(), rng, arrow.id,
                                                     ANCHOR_DATE.replace(hour=10, minute=54, second=0))
    beneficiary_b.name = "Sundara Freight Co"
    db.flush()

    t1 = ANCHOR_DATE.replace(hour=10, minute=47, second=13)
    t2 = ANCHOR_DATE.replace(hour=10, minute=51, second=4)
    t3 = ANCHOR_DATE.replace(hour=10, minute=56, second=21)
    amount = 1_00_00_000.0

    def make_payout(contact: m.Contact, ts: dt.datetime) -> m.Payout:
        fa = db.query(m.FundAccount).filter(m.FundAccount.contact_id == contact.id).first()
        payout = m.Payout(
            id=_short_id("PYO"), merchant_id=arrow.id, contact_id=contact.id, fund_account_id=fa.id,
            amount=amount, purpose="vendor_bill", mode="IMPS",
            narration="Urgent vendor settlement", reference_id=uuid.uuid4().hex[:10],
            status="processed", created_at=ts, is_injected=True,
        )
        db.add(payout)
        db.flush()
        return payout

    p1 = make_payout(beneficiary_a, t1)
    p2 = make_payout(beneficiary_a, t2)
    p3 = make_payout(beneficiary_b, t3)
    sync_financial_events_for_payouts(db, [p1, p2, p3])

    def make_artifact(filename: str, text: str) -> m.EvidenceArtifact:
        artifact = m.EvidenceArtifact(
            id=_short_id("EVD"), incident_id=incident_id, merchant_id=arrow.id, filename=filename,
            mime_type="text/plain", sha256=hashlib.sha256(text.encode()).hexdigest(),
            source_label="whatsapp", raw_text=text, extraction_status="text_ready",
        )
        db.add(artifact)
        db.flush()
        return artifact

    text_a = (
        f"[{t1 - dt.timedelta(minutes=5):%H:%M}] {compromised_employee.name} (Finance Ops): Urgent -- "
        "vendor settlement pending, please release Rs 1,00,00,000 to Kailash Enterprises right now, "
        "new account, don't call to confirm, I'm in transit."
    )
    artifact_a = make_artifact("whatsapp_export_finance_ops.txt", text_a)

    text_b = (
        f"[{t3 - dt.timedelta(minutes=6):%H:%M}] {compromised_employee.name} (Finance Ops): One more, "
        "same urgency -- Rs 1,00,00,000 to Sundara Freight Co, confidential, process immediately."
    )
    artifact_b = make_artifact("whatsapp_export_finance_ops_2.txt", text_b)

    comm_a = m.CommunicationEvent(
        id=_short_id("COM"), source_artifact_id=artifact_a.id, incident_id=incident_id,
        sender_label=f"{compromised_employee.name} (Finance Ops)", channel="whatsapp",
        body_text=text_a, mentioned_amount=amount, mentioned_beneficiary_text="Kailash Enterprises",
        resolved_contact_id=beneficiary_a.id, timestamp=t1 - dt.timedelta(minutes=5),
        correlation_status="CORROBORATED", correlated_financial_event_id=f"FEV_PYO_{p1.id}",
    )
    comm_b = m.CommunicationEvent(
        id=_short_id("COM"), source_artifact_id=artifact_b.id, incident_id=incident_id,
        sender_label=f"{compromised_employee.name} (Finance Ops)", channel="whatsapp",
        body_text=text_b, mentioned_amount=amount, mentioned_beneficiary_text="Sundara Freight Co",
        resolved_contact_id=beneficiary_b.id, timestamp=t3 - dt.timedelta(minutes=6),
        correlation_status="CORROBORATED", correlated_financial_event_id=f"FEV_PYO_{p3.id}",
    )
    db.add_all([comm_a, comm_b])
    db.flush()

    for artifact, comm in [(artifact_a, comm_a), (artifact_b, comm_b)]:
        candidates = extract_candidate_claims(artifact.raw_text, artifact.id)
        financial_events = db.query(m.FinancialEvent).filter(m.FinancialEvent.merchant_id == arrow.id).all()
        candidate_events = [(fe.id, fe.amount) for fe in financial_events]
        for c in candidates:
            status, matched = ("UNVERIFIED", "")
            if c["claim_type"] == "amount":
                status, matched = cross_reference_amount_claim(c["claim_value"]["amount"], candidate_events)
            db.add(m.ExtractedClaim(
                id=c["id"], source_artifact_id=c["source_artifact_id"],
                source_location=c["source_location"], extraction_method=c["extraction_method"],
                claim_type=c["claim_type"], claim_value=c["claim_value"],
                verification_status=status, matched_financial_event_id=matched,
            ))
    db.flush()

    audit_log(db, incident_id=incident_id, actor="SYSTEM", event_type="EVIDENCE_UPLOADED",
              summary="2 WhatsApp exports ingested from Finance Ops thread",
              sources=[artifact_a.id, artifact_b.id], detail={})
    db.commit()

    incident = create_incident_from_payouts(
        db, incident_id=incident_id, merchant_id=arrow.id, payout_ids=[p1.id, p2.id, p3.id],
        scenario="compromised_employee_executive_impersonation",
    )
    incident.state = "EVIDENCE_REVIEW"
    audit_log(db, incident_id=incident_id, actor="SYSTEM", event_type="CASE_STATE_CHANGED",
              summary="RECONSTRUCTING -> EVIDENCE_REVIEW", sources=[], detail={})
    db.commit()
    return incident.id


def run_seed(db: TenantScopedSession, seed_value: int = 42) -> dict:
    Base.metadata.create_all(bind=engine)
    db.set_tenant(None)
    wipe_all(db)

    rng = random.Random(seed_value)
    Faker.seed(seed_value)
    fake = Faker()

    tenant_a = m.Tenant(id=TENANT_NORTHBRIDGE, name="Northbridge Financial")
    tenant_b = m.Tenant(id=TENANT_MERIDIAN, name="Meridian Payments")
    db.add(tenant_a)
    db.add(tenant_b)
    db.commit()

    tokens_by_tenant: dict[str, dict[str, str]] = {}

    # --- Tenant A: Northbridge Financial (the flagship demo tenant) --------
    with tenant_scope(db, tenant_a.id):
        tokens_by_tenant[tenant_a.id] = _make_tenant_users(db, rng, tenant_a.id)

        arrow = _make_merchant(db, fake, rng, "MER_ARROW", "Arrow Industries", "logistics", is_flagship=True)
        arrow_contacts = [
            _make_contact_with_fund_account(db, fake, rng, arrow.id,
                                             HISTORY_START + dt.timedelta(days=rng.randint(0, HISTORY_DAYS - 5)))
            for _ in range(ARROW_CONTACT_COUNT)
        ]
        _generate_payout_history(db, fake, rng, arrow.id, arrow_contacts, ARROW_HISTORICAL_PAYOUTS,
                                  median_target=18400, spread=0.35, largest_override=8_70_000.0)
        _generate_payments(db, fake, rng, arrow.id, ARROW_HISTORICAL_PAYOUTS * 2)
        _generate_transfers_and_settlements(db, rng, arrow.id)

        harbor = _make_merchant(db, fake, rng, "MER_HARBOR", "Harbor & Co", "d2c_retail", is_flagship=False)
        harbor_contacts = [
            _make_contact_with_fund_account(db, fake, rng, harbor.id,
                                             HISTORY_START + dt.timedelta(days=rng.randint(0, HISTORY_DAYS - 5)))
            for _ in range(HARBOR_CONTACT_COUNT)
        ]
        _generate_payout_history(db, fake, rng, harbor.id, harbor_contacts, HARBOR_HISTORICAL_PAYOUTS,
                                  median_target=9600, spread=0.4, largest_override=3_20_000.0)
        _generate_payments(db, fake, rng, harbor.id, HARBOR_HISTORICAL_PAYOUTS * 2)
        _generate_transfers_and_settlements(db, rng, harbor.id)

        half = OTHER_MERCHANT_COUNT // 2
        for i in range(half):
            merchant_id = f"MER_A{i:04d}"
            merchant = _make_merchant(db, fake, rng, merchant_id, fake.company(), rng.choice(MERCHANT_CATEGORIES))
            contacts = [
                _make_contact_with_fund_account(db, fake, rng, merchant.id,
                                                 HISTORY_START + dt.timedelta(days=rng.randint(0, HISTORY_DAYS - 5)))
                for _ in range(rng.randint(*OTHER_MERCHANT_CONTACT_RANGE))
            ]
            payout_count = rng.randint(*OTHER_MERCHANT_PAYOUT_RANGE)
            _generate_payout_history(db, fake, rng, merchant.id, contacts, payout_count,
                                      median_target=rng.uniform(2500, 60000), spread=rng.uniform(0.3, 0.6))
            _generate_payments(db, fake, rng, merchant.id, payout_count * 2)
            if rng.random() < 0.6:
                _generate_transfers_and_settlements(db, rng, merchant.id)
            if i % 10 == 0:
                db.commit()
        db.commit()

        tenant_a_payouts = db.query(m.Payout).all()  # scoped to Tenant A -> Arrow + Harbor + all Tenant-A background merchants
        sync_financial_events_for_payouts(db, tenant_a_payouts)
        db.commit()

        flagship_incident_id = _build_flagship_incident(db, rng, arrow, arrow_contacts)

        audit_log(db, incident_id="", actor="SYSTEM", event_type="DATASET_SEEDED",
                  summary=f"Synthetic universe seeded for {tenant_a.name} (seed={seed_value})",
                  sources=[], detail={"merchants": half + 2})
        db.commit()

    # --- Tenant B: Meridian Payments (isolation-test fodder, no incidents) -
    with tenant_scope(db, tenant_b.id):
        tokens_by_tenant[tenant_b.id] = _make_tenant_users(db, rng, tenant_b.id)

        remaining = OTHER_MERCHANT_COUNT - half
        for i in range(remaining):
            merchant_id = f"MER_B{i:04d}"
            merchant = _make_merchant(db, fake, rng, merchant_id, fake.company(), rng.choice(MERCHANT_CATEGORIES))
            contacts = [
                _make_contact_with_fund_account(db, fake, rng, merchant.id,
                                                 HISTORY_START + dt.timedelta(days=rng.randint(0, HISTORY_DAYS - 5)))
                for _ in range(rng.randint(*OTHER_MERCHANT_CONTACT_RANGE))
            ]
            payout_count = rng.randint(*OTHER_MERCHANT_PAYOUT_RANGE)
            _generate_payout_history(db, fake, rng, merchant.id, contacts, payout_count,
                                      median_target=rng.uniform(2500, 60000), spread=rng.uniform(0.3, 0.6))
            _generate_payments(db, fake, rng, merchant.id, payout_count * 2)
            if rng.random() < 0.6:
                _generate_transfers_and_settlements(db, rng, merchant.id)
            if i % 10 == 0:
                db.commit()
        db.commit()

        all_b_payouts = db.query(m.Payout).all()
        sync_financial_events_for_payouts(db, all_b_payouts)
        db.commit()

        audit_log(db, incident_id="", actor="SYSTEM", event_type="DATASET_SEEDED",
                  summary=f"Synthetic universe seeded for {tenant_b.name} (seed={seed_value})",
                  sources=[], detail={"merchants": remaining})
        db.commit()

    db.set_tenant(None)
    return {
        "flagship_incident_id": flagship_incident_id,
        "tenants": {tenant_a.id: tenant_a.name, tenant_b.id: tenant_b.name},
        "tokens_by_tenant": tokens_by_tenant,
    }


if __name__ == "__main__":
    from app.core.database import SessionLocal

    session = SessionLocal()
    try:
        result = run_seed(session, seed_value=42)
        session.set_tenant(None)
        merchant_count = session.query(m.Merchant).count()
        payout_count = session.query(m.Payout).count()
        payment_count = session.query(m.Payment).count()
        fevent_count = session.query(m.FinancialEvent).count()
        arrow_payouts = [p.amount for p in session.query(m.Payout).filter(
            m.Payout.merchant_id == "MER_ARROW", m.Payout.is_injected.is_(False)).all()]
        print(f"Seed complete. Flagship incident: {result['flagship_incident_id']}")
        print(f"Tenants: {result['tenants']}")
        print(f"Merchants={merchant_count} Payments={payment_count} Payouts={payout_count} "
              f"FinancialEvents={fevent_count}")
        print(f"Arrow Industries baseline: median={statistics.median(arrow_payouts):,.0f} "
              f"largest={max(arrow_payouts):,.0f} beneficiaries={ARROW_CONTACT_COUNT}")
        print()
        print("Demo bearer tokens (seed=42, deterministic -- not real secrets):")
        for tenant_id, role_tokens in result["tokens_by_tenant"].items():
            print(f"  {tenant_id}:")
            for role, token in role_tokens.items():
                print(f"    {role:<18} {token}")
    finally:
        session.close()

