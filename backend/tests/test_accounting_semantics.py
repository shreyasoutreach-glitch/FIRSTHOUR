import pytest
from decimal import Decimal
from app.services.exposure.engine import compute_exposure
from app.models.entities import FinancialEvent

def build_fe(id, amount, event_type="payout", orig_id=None):
    return FinancialEvent(
        id=id,
        amount=Decimal(str(amount)),
        event_type=event_type,
        attributes={"original_event_id": orig_id} if orig_id else {}
    )

def test_confirmed_transaction():
    events = [build_fe("1", 1000)]
    res = compute_exposure(None, fevents=events)
    assert res["confirmed_moved"]["total"] == Decimal(1000)

def test_full_reversal():
    events = [
        build_fe("1", 1000),
        build_fe("2", 1000, "reversal", orig_id="1")
    ]
    res = compute_exposure(None, fevents=events)
    assert res["confirmed_moved"]["total"] == Decimal(0)
    assert res["attempted"]["total"] == Decimal(1000)

def test_duplicate_reversal():
    events = [
        build_fe("1", 1000),
        build_fe("2", 1000, "reversal", orig_id="1"),
        build_fe("3", 1000, "reversal", orig_id="1")
    ]
    res = compute_exposure(None, fevents=events)
    assert res["confirmed_moved"]["total"] == Decimal(0)
    assert res["attempted"]["total"] == Decimal(1000)

def test_partial_refund():
    events = [
        build_fe("1", 1000),
        build_fe("2", 300, "refund", orig_id="1")
    ]
    res = compute_exposure(None, fevents=events)
    assert res["confirmed_moved"]["total"] == Decimal(700)

def test_duplicate_partial_refund():
    # Same refund ID simulates a duplicate event in the stream
    events = [
        build_fe("1", 1000),
        build_fe("2", 300, "refund", orig_id="1"),
        build_fe("2", 300, "refund", orig_id="1")
    ]
    res = compute_exposure(None, fevents=events)
    assert res["confirmed_moved"]["total"] == Decimal(700)

def test_multiple_legitimate_partial_refunds():
    events = [
        build_fe("1", 1000),
        build_fe("2", 300, "refund", orig_id="1"),
        build_fe("3", 200, "refund", orig_id="1")
    ]
    res = compute_exposure(None, fevents=events)
    assert res["confirmed_moved"]["total"] == Decimal(500)

def test_failed_original_transaction():
    orig = build_fe("1", 1000)
    orig.attributes["_legacy_status"] = "failed"
    events = [orig]
    res = compute_exposure(None, fevents=events)
    assert res["confirmed_moved"]["total"] == Decimal(0)
    assert res["attempted"]["total"] == Decimal(1000)

def test_reversal_of_nonexistent_transaction():
    events = [build_fe("2", 1000, "reversal", orig_id="999")]
    res = compute_exposure(None, fevents=events)
    assert res["confirmed_moved"]["total"] == Decimal(0)

def test_reversal_referencing_another_tenant():
    # Because compute_exposure receives scoped events, cross-tenant leaks are
    # prevented upstream, but if it DID get passed, it would just orphan.
    events = [build_fe("2", 1000, "reversal", orig_id="OTHER_TENANT_ID")]
    res = compute_exposure(None, fevents=events)
    assert res["confirmed_moved"]["total"] == Decimal(0)

def test_out_of_order_reversal_arrival():
    events = [
        build_fe("2", 1000, "reversal", orig_id="1"),
        build_fe("1", 1000)
    ]
    res = compute_exposure(None, fevents=events)
    assert res["confirmed_moved"]["total"] == Decimal(0)
    assert res["attempted"]["total"] == Decimal(1000)

def test_reconciliation_after_all_events_arrive():
    events = [
        build_fe("1", 1000),
        build_fe("2", 100, "refund", orig_id="1"),
        build_fe("3", 200, "refund", orig_id="1"),
        build_fe("4", 1000, "reversal", orig_id="1"), # Overrides refunds
    ]
    res = compute_exposure(None, fevents=events)
    assert res["confirmed_moved"]["total"] == Decimal(0)
    assert res["attempted"]["total"] == Decimal(1000)

