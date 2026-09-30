from decimal import Decimal
from pathlib import Path

from app.models import entities as m
from app.services.imports.csv_payouts import normalize_payout_rows

def test_csv_normalizer_accepts_generic_payout_headers():
    rows = [{
        "transaction_id": "PAY-001",
        "timestamp": "2026-09-30T10:00:00+05:30",
        "amount": "125000.00",
        "currency": "INR",
        "status": "processed",
        "beneficiary_name": "Acme Supplies",
        "account_number": "XXXX1234",
        "ifsc": "ABCD0001234",
    }]
    parsed = normalize_payout_rows(rows)
    assert parsed[0]["source_id"] == "PAY-001"
    assert parsed[0]["amount"] == Decimal("125000.00")
    assert parsed[0]["beneficiary"] == "Acme Supplies"

def test_csv_normalizer_rejects_missing_required_fields():
    rows = [{"transaction_id": "PAY-001", "amount": "10"}]
    try:
        normalize_payout_rows(rows)
        assert False, "expected validation error"
    except ValueError as exc:
        assert "timestamp" in str(exc)
