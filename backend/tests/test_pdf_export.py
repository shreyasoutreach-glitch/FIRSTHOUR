from app.services.recovery.pdf import render_recovery_packet_pdf

def test_recovery_packet_pdf_is_real_pdf():
    payload = {
        "case_id": "INC_TEST",
        "merchant_name": "Synthetic Test Co",
        "transaction_table": [{
            "payout_id": "CSV_PAY_001",
            "timestamp": "2026-09-30T10:00:00",
            "beneficiary": "Synthetic Vendor",
            "amount": "125000.00",
            "status": "processed",
            "source_reference": "FEV_TEST",
        }],
        "outstanding_questions": ["authorization_status"],
        "evidence_index": [{"filename": "invoice.pdf", "sha256": "abc123", "extraction_status": "extracted"}],
    }
    data = render_recovery_packet_pdf(payload)
    assert data.startswith(b"%PDF-")
    assert len(data) > 1000
