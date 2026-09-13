import os
import uuid
import razorpay
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from .adapter import GatewayAdapter, NormalizedPayment, NormalizedPayout

class RazorpayTestAdapter(GatewayAdapter):
    def __init__(self, key_id: str | None = None, key_secret: str | None = None):
        self.key_id = key_id or os.environ.get("RAZORPAY_KEY_ID")
        self.key_secret = key_secret or os.environ.get("RAZORPAY_KEY_SECRET")
        self.is_test_mode = os.environ.get("RAZORPAY_MODE", "test").lower() == "test"
        
        if not self.key_id or not self.key_secret:
            logging.warning("Razorpay keys missing. RazorpayAdapter will operate in degraded/mock mode.")
            self.client = None
        else:
            self.client = razorpay.Client(auth=(self.key_id, self.key_secret))

    def _generate_mock_payments(self, tenant_id: str) -> List[NormalizedPayment]:
        return [
            NormalizedPayment(
                id=f"pay_{uuid.uuid4().hex[:10]}",
                tenant_id=tenant_id,
                amount=50000.0,
                currency="INR",
                status="captured",
                gateway_reference="rzp_mock_pay",
                created_at=datetime.utcnow().isoformat()
            )
        ]
        
    def _generate_mock_payouts(self, tenant_id: str) -> List[NormalizedPayout]:
        return [
            NormalizedPayout(
                id=f"pout_{uuid.uuid4().hex[:10]}",
                tenant_id=tenant_id,
                amount=15000.0,
                currency="INR",
                status="processed",
                beneficiary_name="Acme Corp",
                gateway_reference="rzp_mock_pout",
                created_at=datetime.utcnow().isoformat()
            )
        ]

    def sync_payments(self, tenant_id: str, since: Optional[str] = None) -> List[NormalizedPayment]:
        if not self.client:
            return self._generate_mock_payments(tenant_id)
            
        try:
            # Bounded fetch to prevent huge payloads
            rzp_payments = self.client.payment.all({'count': 10})
            results = []
            for p in rzp_payments.get('items', []):
                # Razorpay amounts are in paise
                amount = float(p.get('amount', 0)) / 100.0
                results.append(NormalizedPayment(
                    id=f"FIRST_PAY_{p['id']}",
                    tenant_id=tenant_id,
                    amount=amount,
                    currency=p.get('currency', 'INR'),
                    status=p.get('status', 'unknown'),
                    gateway_reference=p['id'],
                    created_at=datetime.fromtimestamp(p.get('created_at', 0)).isoformat()
                ))
            return results
        except Exception as e:
            logging.error(f"Failed to sync Razorpay payments: {e}")
            raise
            
    def sync_payouts(self, tenant_id: str, since: Optional[str] = None) -> List[NormalizedPayout]:
        # Razorpay Payouts API requires RazorpayX, which uses different auth, but we abstract it here
        if not self.client:
            return self._generate_mock_payouts(tenant_id)
            
        try:
            rzp_payouts = self.client.payout.all({'count': 10})
            results = []
            for p in rzp_payouts.get('items', []):
                amount = float(p.get('amount', 0)) / 100.0
                # In a real app we'd fetch the fund account to get the beneficiary name
                results.append(NormalizedPayout(
                    id=f"FIRST_POUT_{p['id']}",
                    tenant_id=tenant_id,
                    amount=amount,
                    currency=p.get('currency', 'INR'),
                    status=p.get('status', 'unknown'),
                    beneficiary_name="Unknown (Requires FundAccount fetch)",
                    gateway_reference=p['id'],
                    created_at=datetime.fromtimestamp(p.get('created_at', 0)).isoformat()
                ))
            return results
        except Exception as e:
            logging.error(f"Failed to sync Razorpay payouts: {e}")
            # Some sandbox accounts don't have RazorpayX enabled, fallback cleanly
            return []

    def simulate_freeze(self, target_id: str) -> Dict[str, Any]:
        """
        Simulates freezing a payout. In Razorpay this would map to cancelling a queued payout.
        Since we NEVER execute real money movement in this phase, we only return the simulation payload.
        """
        return {
            "intended_action": "FREEZE_PAYOUT",
            "target": target_id,
            "gateway": "RAZORPAY",
            "payload": {"payout_id": target_id.replace("FIRST_POUT_", "")},
            "expected_outcome": "Payout marked as CANCELLED before processing",
            "simulated_result": "SUCCESS",
            "audit_event": "Simulated Razorpay Payout Freeze"
        }
        
    def simulate_reversal(self, target_id: str) -> Dict[str, Any]:
        """
        Simulates reversing a payment (Refund).
        """
        return {
            "intended_action": "REVERSE_PAYMENT",
            "target": target_id,
            "gateway": "RAZORPAY",
            "payload": {"payment_id": target_id.replace("FIRST_PAY_", ""), "amount": "full"},
            "expected_outcome": "Payment refunded to source",
            "simulated_result": "SUCCESS",
            "audit_event": "Simulated Razorpay Payment Reversal"
        }
