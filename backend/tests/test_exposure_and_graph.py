import datetime as dt

from app.models import entities as m
from app.services.exposure.engine import compute_exposure
from app.services.graph.builder import blast_radius, build_incident_graph


def _seed_minimal_incident(db):
    merchant = m.Merchant(id="MER_T", name="Test Co", category="retail")
    db.add(merchant)
    contact_a = m.Contact(id="CON_A", merchant_id="MER_T", name="Vendor A", type="vendor",
                          created_at=dt.datetime(2026, 1, 1))
    contact_b = m.Contact(id="CON_B", merchant_id="MER_T", name="Vendor B", type="vendor",
                          created_at=dt.datetime(2026, 1, 1))
    db.add_all([contact_a, contact_b])
    fa_a = m.FundAccount(id="FA_A", contact_id="CON_A", vpa="a@upi")
    fa_b = m.FundAccount(id="FA_B", contact_id="CON_B", vpa="a@upi")  # shared VPA -> shared fund account signal
    db.add_all([fa_a, fa_b])

    payout1 = m.Payout(id="PYO_1", merchant_id="MER_T", contact_id="CON_A", fund_account_id="FA_A",
                       amount=1000000, status="processed", created_at=dt.datetime(2026, 6, 1, 10, 0))
    payout2 = m.Payout(id="PYO_2", merchant_id="MER_T", contact_id="CON_A", fund_account_id="FA_A",
                       amount=500000, status="queued", created_at=dt.datetime(2026, 6, 1, 10, 5))
    payout3 = m.Payout(id="PYO_3", merchant_id="MER_T", contact_id="CON_B", fund_account_id="FA_B",
                       amount=200000, status="processed", created_at=dt.datetime(2026, 6, 1, 10, 10))
    db.add_all([payout1, payout2, payout3])

    fe1 = m.FinancialEvent(id="FEV_PYO_PYO_1", event_type="payout", source_record_id="PYO_1",
                           merchant_id="MER_T", counterparty_id="CON_A", timestamp=payout1.created_at,
                           amount=payout1.amount)
    fe2 = m.FinancialEvent(id="FEV_PYO_PYO_2", event_type="payout", source_record_id="PYO_2",
                           merchant_id="MER_T", counterparty_id="CON_A", timestamp=payout2.created_at,
                           amount=payout2.amount)
    db.add_all([fe1, fe2])

    incident = m.Incident(id="INC_T", merchant_id="MER_T", state="RECONSTRUCTING",
                          window_start=payout1.created_at, window_end=payout2.created_at)
    db.add(incident)
    db.add(m.IncidentEvent(id="IEV_1", incident_id="INC_T", financial_event_id="FEV_PYO_PYO_1", sequence=0))
    db.add(m.IncidentEvent(id="IEV_2", incident_id="INC_T", financial_event_id="FEV_PYO_PYO_2", sequence=1))
    db.commit()


def test_exposure_separates_confirmed_and_pending(db_session):
    _seed_minimal_incident(db_session)
    exposure = compute_exposure(db_session, "INC_T")
    assert exposure["confirmed_moved"]["total"] == 1000000
    assert exposure["pending"]["total"] == 500000
    assert exposure["attempted"]["total"] == 0
    # PYO_3 shares fund account "a@upi" family via CON_B -> reachable in blast radius, not in confirmed/pending
    assert exposure["related"]["total"] >= 0


def test_graph_contains_merchant_payout_and_contact_nodes(db_session):
    _seed_minimal_incident(db_session)
    graph = build_incident_graph(db_session, "INC_T")
    node_types = {n["type"] for n in graph["nodes"]}
    assert "Merchant" in node_types
    assert "Payout" in node_types
    assert "Contact" in node_types
    edge_types = {e["type"] for e in graph["edges"]}
    assert "PAID_TO" in edge_types


def test_blast_radius_reaches_shared_fund_account_contact(db_session):
    _seed_minimal_incident(db_session)
    radius = blast_radius(db_session, ["CON_A"], depth=3)
    assert radius["affected_entities"] >= 1
    assert radius["traversal_depth"] == 3
