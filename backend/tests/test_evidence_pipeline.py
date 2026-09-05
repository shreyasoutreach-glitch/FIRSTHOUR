from app.services.evidence.pipeline import (
    cross_reference_amount_claim,
    extract_candidate_claims,
    sha256_bytes,
    validate_mime,
)


def test_sha256_is_deterministic():
    assert sha256_bytes(b"hello") == sha256_bytes(b"hello")
    assert sha256_bytes(b"hello") != sha256_bytes(b"world")


def test_validate_mime_accepts_expected_types():
    assert validate_mime("image/png")
    assert validate_mime("application/pdf")
    assert validate_mime("text/plain")


def test_validate_mime_rejects_executable():
    assert not validate_mime("application/x-msdownload")


def test_extract_amount_claim_crore():
    claims = extract_candidate_claims("please send Rs 1,00,00,000 today", "EVD_1")
    amount_claims = [c for c in claims if c["claim_type"] == "amount"]
    assert amount_claims
    assert amount_claims[0]["claim_value"]["amount"] == 1_00_00_000


def test_extract_beneficiary_claim():
    claims = extract_candidate_claims("please transfer to Kailash Enterprises now", "EVD_1")
    beneficiary_claims = [c for c in claims if c["claim_type"] == "beneficiary"]
    assert beneficiary_claims
    assert "Kailash" in beneficiary_claims[0]["claim_value"]["name"]


def test_extract_instruction_signal():
    claims = extract_candidate_claims("this is urgent and confidential", "EVD_1")
    signals = [c for c in claims if c["claim_type"] == "instruction_signal"]
    assert signals
    assert "urgent" in signals[0]["claim_value"]["keywords"]


def test_cross_reference_verified_within_tolerance():
    status, matched = cross_reference_amount_claim(1_00_00_000, [("FEV_1", 1_00_00_000)])
    assert status == "VERIFIED"
    assert matched == "FEV_1"


def test_cross_reference_conflicting_when_no_match_but_events_exist():
    status, _ = cross_reference_amount_claim(50_000, [("FEV_1", 1_00_00_000)])
    assert status == "CONFLICTING"


def test_cross_reference_unverified_when_no_events():
    status, _ = cross_reference_amount_claim(50_000, [])
    assert status == "UNVERIFIED"
