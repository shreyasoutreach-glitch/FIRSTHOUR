from app.services.entity.resolution import normalize_name, resolve


def test_exact_transaction_id_auto_links():
    result = resolve(candidate_transaction_id="TXN1", known_transaction_id="TXN1")
    assert result.decision == "AUTO_LINK"


def test_exact_upi_case_insensitive_auto_links():
    result = resolve(candidate_upi_id="Vendor@upi", known_upi_id="vendor@UPI")
    assert result.decision == "AUTO_LINK"


def test_similar_name_alone_never_auto_links():
    result = resolve(candidate_name="Arrow Traders Pvt Ltd", known_name="Arrow Traders")
    assert result.decision != "AUTO_LINK"


def test_different_names_and_no_strong_signal_keeps_separate():
    result = resolve(candidate_name="Zenith Corp", known_name="Meridian Corp")
    assert result.decision == "KEEP_SEPARATE"


def test_phone_digits_normalized_before_comparison():
    # exact_phone weight is 0.85 -- inside the REVIEW band (0.70-0.89), not
    # strong enough alone for AUTO_LINK per the architecture's decision bands.
    result = resolve(candidate_phone="+91 98765-43210", known_phone="9876543210")
    assert result.signal == "exact_phone"
    assert result.decision == "REVIEW"


def test_normalize_name_strips_suffix_and_punctuation():
    assert normalize_name("Arrow Industries Pvt. Ltd.") == "arrow industries"
