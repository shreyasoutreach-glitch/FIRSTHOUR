import datetime as dt

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.main import app
from app.models import entities as m


@pytest.fixture()
def client(tmp_path):
    db_path = tmp_path / "api_test.db"
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    db = TestingSessionLocal()
    merchant = m.Merchant(id="MER_API", name="API Test Co", category="retail")
    db.add(merchant)
    contact = m.Contact(id="CON_API", merchant_id="MER_API", name="New Vendor", type="vendor",
                        created_at=dt.datetime(2026, 6, 1, 10, 40))
    db.add(contact)
    fa = m.FundAccount(id="FA_API", contact_id="CON_API", vpa="newvendor@upi")
    db.add(fa)
    for i in range(30):
        db.add(m.Payout(id=f"PYO_HIST_{i}", merchant_id="MER_API", contact_id="CON_API",
                        fund_account_id="FA_API", amount=15000 + i * 100, status="processed",
                        created_at=dt.datetime(2026, 1, 1) + dt.timedelta(days=i)))
    db.commit()

    from app.services.incident.detector import create_incident_from_payouts
    payout = m.Payout(id="PYO_API_1", merchant_id="MER_API", contact_id="CON_API", fund_account_id="FA_API",
                      amount=5_000_000, status="processed", created_at=dt.datetime(2026, 6, 1, 11, 0),
                      is_injected=True)
    db.add(payout)
    db.commit()
    create_incident_from_payouts(db, incident_id="INC_API_TEST", merchant_id="MER_API",
                                  payout_ids=["PYO_API_1"], scenario="test_scenario")
    db.close()

    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_get_incident_returns_headline(client):
    resp = client.get("/incident/INC_API_TEST")
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == "INC_API_TEST"
    assert body["headline"]["payout_count"] == 1
    assert body["incident_evidence_score"] > 0


def test_get_incident_404_for_unknown(client):
    resp = client.get("/incident/NOPE")
    assert resp.status_code == 404


def test_timeline_endpoint_sorted_chronologically(client):
    resp = client.get("/incident/INC_API_TEST/timeline")
    assert resp.status_code == 200
    events = resp.json()
    timestamps = [e["timestamp"] for e in events]
    assert timestamps == sorted(timestamps)


def test_exposure_endpoint(client):
    resp = client.get("/incident/INC_API_TEST/exposure")
    assert resp.status_code == 200
    body = resp.json()
    assert body["confirmed_moved"]["total"] == 5_000_000


def test_graph_endpoint(client):
    resp = client.get("/incident/INC_API_TEST/graph")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["nodes"]) > 0


def test_next_question_then_attestation_changes_state(client):
    resp = client.get("/incident/INC_API_TEST/questions/next")
    assert resp.status_code == 200
    question = resp.json()
    assert question["question_id"] == "q_authorized_payouts"

    resp2 = client.post("/incident/INC_API_TEST/attestation",
                        json={"question_id": "q_authorized_payouts", "answer": "NO", "note": "not me"})
    assert resp2.status_code == 200
    body = resp2.json()
    assert body["new_state"] == "INCIDENT_CONFIRMED"
    assert "does not rewrite" in body["message"]


def test_attestation_rejects_unknown_question(client):
    resp = client.post("/incident/INC_API_TEST/attestation",
                       json={"question_id": "q_not_real", "answer": "YES"})
    assert resp.status_code == 400


def test_recovery_packet_has_source_references(client):
    resp = client.get("/incident/INC_API_TEST/recovery-packet")
    assert resp.status_code == 200
    packet = resp.json()
    assert packet["case_id"] == "INC_API_TEST"
    assert packet["transaction_table"][0]["source_reference"]


def test_demo_reset_reseeds_flagship_incident(client):
    resp = client.post("/demo/reset")
    assert resp.status_code == 200
    body = resp.json()
    assert body["flagship_incident_id"] == "INC-001"

    resp2 = client.get("/incident/INC-001")
    assert resp2.status_code == 200
    assert resp2.json()["headline"]["payout_count"] == 3


def test_demo_inject_incident_scenario(client):
    # MER_HARBOR (the dedicated Chaos Lab merchant) only exists after a seed/reset.
    client.post("/demo/reset")
    resp = client.post("/demo/inject-incident", json={"scenario": "new_beneficiary_burst",
                                                        "merchant_id": "MER_HARBOR"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["incident_evidence_score"] > 0
    assert len(body["payout_ids"]) == 3
