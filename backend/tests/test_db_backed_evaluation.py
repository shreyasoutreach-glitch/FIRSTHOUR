import json
import pytest
from fastapi.testclient import TestClient
from app.core.database import get_db
from app.main import app
from app.models import entities as m

@pytest.fixture()
def api_eval_client(db_session):
    token = "eval_investigator_token"
    db_session.add(m.User(id="USR_EVAL", email="eval@test.demo", display_name="Evaluator", role="INVESTIGATOR", api_token=token))
    merchant = m.Merchant(id="MER_EVAL", name="Evaluation Merchant", category="industrial")
    db_session.add(merchant)
    contact = m.Contact(id="CON_EVAL", merchant_id=merchant.id, name="New Vendor", type="vendor", created_at=__import__("datetime").datetime(2026, 1, 1))
    db_session.add(contact)
    fund = m.FundAccount(id="FA_EVAL", contact_id=contact.id, masked_bank_account="XXXX1234", masked_ifsc="ABCD0001234")
    db_session.add(fund)
    for i in range(30):
        db_session.add(m.Payout(id=f"PYO_EVAL_H_{i}", merchant_id=merchant.id, contact_id=contact.id, fund_account_id=fund.id, amount=15000 + i * 100, status="processed", created_at=__import__("datetime").datetime(2026, 1, 1) + __import__("datetime").timedelta(days=i)))
    db_session.commit()
    def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield {"client": client, "token": token}
    app.dependency_overrides.clear()

def _post_csv(client, token, source_id, amount, beneficiary):
    csv = (
        "transaction_id,timestamp,amount,currency,status,beneficiary_name,account_number,ifsc\n"
        f"{source_id},2026-09-30T10:00:00+00:00,{amount},INR,processed,{beneficiary},XXXX1234,ABCD0001234\n"
    ).encode()
    return client.post("/api/import/payouts-csv", files={"file": ("case.csv", csv, "text/csv")}, data={"merchant_id": "MER_EVAL", "source_system": "db_eval"}, headers={"Authorization": f"Bearer {token}"})

def test_db_backed_api_evaluation_60_cases(api_eval_client, capsys):
    client, token = api_eval_client["client"], api_eval_client["token"]
    results = []
    for i in range(30):
        resp = _post_csv(client, token, f"EVAL-CLEAN-{i:03d}", 15000 + (i % 5) * 100, "New Vendor")
        assert resp.status_code == 200, resp.text
        results.append({"case": f"clean-{i}", "expected": 0, "observed": resp.json()["incident_count"]})
    for i in range(30):
        resp = _post_csv(client, token, f"EVAL-SUSPICIOUS-{i:03d}", 5_000_000 + i * 1000, f"Unseen Vendor {i}" )
        assert resp.status_code == 200, resp.text
        results.append({"case": f"suspicious-{i}", "expected": 1, "observed": resp.json()["incident_count"]})
    tp = sum(r["expected"] == 1 and r["observed"] >= 1 for r in results)
    fn = sum(r["expected"] == 1 and r["observed"] == 0 for r in results)
    tn = sum(r["expected"] == 0 and r["observed"] == 0 for r in results)
    fp = sum(r["expected"] == 0 and r["observed"] >= 1 for r in results)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    print(json.dumps({"dataset":"primhora-db-api-eval-v1","population":60,"tp":tp,"fp":fp,"tn":tn,"fn":fn,"precision":round(precision,3),"recall":round(recall,3),"failures":[r for r in results if (r["expected"] == 1 and r["observed"] == 0) or (r["expected"] == 0 and r["observed"] >= 1)]}, indent=2))
    assert fn == 0
    assert fp == 0

def test_db_backed_api_evaluation_rejects_malformed_and_replays(api_eval_client):
    client, token = api_eval_client["client"], api_eval_client["token"]
    malformed = client.post("/api/import/payouts-csv", files={"file": ("bad.csv", b"transaction_id,amount\nBAD,10\n", "text/csv")}, data={"merchant_id":"MER_EVAL"}, headers={"Authorization":f"Bearer {token}"})
    assert malformed.status_code == 422
    first = _post_csv(client, token, "EVAL-REPLAY-001", 15000, "New Vendor")
    assert first.status_code == 200
    replay = _post_csv(client, token, "EVAL-REPLAY-001", 15000, "New Vendor")
    assert replay.status_code == 200
    assert replay.json()["skipped_rows"] == 1
    assert replay.json()["imported_rows"] == 0