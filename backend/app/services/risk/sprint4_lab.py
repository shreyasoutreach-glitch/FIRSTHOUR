import random
import uuid
from datetime import datetime, timedelta
from app.services.risk.events import RiskEvent, AccountTrustState
from app.services.risk.engines import RiskFusionEngine

class ROI_Calculator:
    def __init__(self, baseline_loss: float, review_cost: float, fpr_cost: float):
        self.baseline_loss = baseline_loss
        self.review_cost = review_cost
        self.fpr_cost = fpr_cost
        self.loss_prevented = 0.0
        self.review_expense = 0.0
        
    def calculate(self):
        roi = self.loss_prevented - self.review_expense
        return {
            "Baseline Fraud": self.baseline_loss,
            "Loss Prevented": self.loss_prevented,
            "Review / Friction Expense": self.review_expense,
            "Net ROI": roi
        }

class CustomerZeroSimulator:
    def __init__(self):
        self.fusion = RiskFusionEngine()
        self.roi = ROI_Calculator(100000.0, 10.0, 50.0) # $10 per review, $50 per block friction
        self.global_beneficiary_counts = {}

    def ingest_and_evaluate(self, events, state, label=""):
        hist = []
        max_risk = 0.0
        action = "ALLOW"
        extracted = 0.0
        
        sim_state = state.model_copy(deep=True)
        
        for e in events:
            # Phase 14: Network Simulation (Fan-In calculation dynamically populated before eval)
            b_id = e.payload.get("beneficiary_id")
            if e.event_type == "TRANSFER_COMPLETED" and b_id:
                if b_id not in self.global_beneficiary_counts:
                    self.global_beneficiary_counts[b_id] = set()
                self.global_beneficiary_counts[b_id].add(e.entity_id)
                
                # Mock graph payload dynamically via shadow network lookup
                e.payload["graph_fan_in"] = len(self.global_beneficiary_counts[b_id])
            
            res = self.fusion.evaluate_risk(e, sim_state, hist)
            max_risk = max(max_risk, res.risk_probability)
            
            if res.recommended_action == "BLOCK_RECOMMENDED":
                action = "BLOCK"
                if label == "fraud": self.roi.loss_prevented += e.payload.get("amount", 0.0)
                if label == "legit": self.roi.review_expense += self.roi.fpr_cost
                break
            elif res.recommended_action == "HOLD_AND_REVIEW":
                action = "REVIEW"
                self.roi.review_expense += self.roi.review_cost
                if label == "fraud": self.roi.loss_prevented += e.payload.get("amount", 0.0)
                break
                
            if e.event_type == "TRANSFER_COMPLETED":
                extracted += e.payload.get("amount", 0.0)
                
            sim_state.apply_event(e)
            hist.append(e)
            
        return max_risk, action, extracted

    def generate_low_and_slow_mule_attack(self):
        # 10 compromised accounts all funneling 750 (under threshold) to 1 mule
        extracted_total = 0.0
        for victim_idx in range(10):
            state = AccountTrustState(tenant_id="t1", entity_id=f"victim_{victim_idx}")
            state.median_amount = 500.0
            state.mad_amount = 100.0
            
            events = []
            t = datetime.utcnow()
            for _ in range(5): # 5 transfers per victim
                t += timedelta(hours=12)
                events.append(RiskEvent(
                    event_id=f"EVT_{uuid.uuid4().hex[:8]}", tenant_id="t1", entity_id=state.entity_id,
                    event_type="TRANSFER_COMPLETED", event_time=t, source="core", source_event_id="s",
                    payload={"amount": 750.0, "beneficiary_id": "mule_wallet_x"}
                ))
            
            r, a, ext = self.ingest_and_evaluate(events, state, label="fraud")
            extracted_total += ext
            
        return extracted_total
        
    def generate_legitimate_payroll(self):
        # 1 business account transferring to 50 employees
        state = AccountTrustState(tenant_id="t1", entity_id="business_1")
        state.median_amount = 2000.0
        state.mad_amount = 500.0
        
        events = []
        t = datetime.utcnow()
        for i in range(50):
            t += timedelta(minutes=1)
            events.append(RiskEvent(
                event_id=f"EVT_{uuid.uuid4().hex[:8]}", tenant_id="t1", entity_id=state.entity_id,
                event_type="TRANSFER_COMPLETED", event_time=t, source="core", source_event_id="s",
                payload={"amount": 2500.0, "beneficiary_id": f"employee_{i}"}
            ))
            
        return self.ingest_and_evaluate(events, state, label="legit")

    def run(self):
        print("--- PHASE 49: CUSTOMER ZERO SIMULATION ---")
        extracted_mule = self.generate_low_and_slow_mule_attack()
        print(f"[ATTACK] Low-and-Slow Mule Fan-In -> Extracted: {extracted_mule} (Expected 37500 without Graph, <3000 with Graph)")
        
        r, a, ext_pay = self.generate_legitimate_payroll()
        print(f"[LEGIT] Payroll Fan-Out -> Risk: {r}, Action: {a}")
        
        print("\n--- PHASE 40: ECONOMIC ROI ---")
        roi = self.roi.calculate()
        for k,v in roi.items():
            print(f"{k}: ${v:.2f}")

if __name__ == "__main__":
    sim = CustomerZeroSimulator()
    sim.run()
