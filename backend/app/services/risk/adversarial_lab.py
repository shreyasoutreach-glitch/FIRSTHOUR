import time
import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from app.services.risk.events import RiskEvent, AccountTrustState
from app.services.risk.engines import RiskFusionEngine

class AdversarialLab:
    def __init__(self):
        self.fusion = RiskFusionEngine()
        self.nightmare_set = []
        self.money_extracted = 0.0

    def evaluate_sequence(self, events: List[RiskEvent], state: AccountTrustState) -> Tuple[float, str, float]:
        hist = []
        max_risk = 0.0
        final_action = "ALLOW"
        extracted = 0.0
        
        sim_state = state.model_copy(deep=True)
        
        for e in events:
            res = self.fusion.evaluate_risk(e, sim_state, hist)
            max_risk = max(max_risk, res.risk_probability)
            
            # Simple simulation of policy application
            if res.recommended_action in ("BLOCK_RECOMMENDED", "HOLD_AND_REVIEW"):
                final_action = res.recommended_action
                break # Attack halted
                
            if e.event_type == "TRANSFER_COMPLETED":
                extracted += e.payload.get("amount", 0.0)
                
            sim_state.apply_event(e)
            hist.append(e)
            
        return max_risk, final_action, extracted

    def generate_low_and_slow(self, base_state: AccountTrustState, target_amount: float) -> List[RiskEvent]:
        # Attacker probes threshold. Z-score threshold for risk is ~3.0. 
        # Safe amount is median + 2.5 * MAD.
        safe_amount = base_state.median_amount + (2.5 * max(base_state.mad_amount, 1.0))
        
        events = []
        t = datetime.utcnow()
        
        # Initial stealth takeover
        events.append(RiskEvent(
            event_id=f"EVT_{uuid.uuid4().hex[:8]}", tenant_id="t1", entity_id=base_state.entity_id,
            event_type="LOGIN_SUCCESS", event_time=t, source="auth", source_event_id="s1",
            payload={"ip": "trusted_vpn", "device_id": list(base_state.known_devices)[0] if base_state.known_devices else "dev1"}
        ))
        
        extracted = 0.0
        while extracted < target_amount:
            t += timedelta(hours=12) # Wait to avoid sequence velocity
            chunk = min(safe_amount, target_amount - extracted)
            events.append(RiskEvent(
                event_id=f"EVT_{uuid.uuid4().hex[:8]}", tenant_id="t1", entity_id=base_state.entity_id,
                event_type="TRANSFER_COMPLETED", event_time=t, source="core", source_event_id=uuid.uuid4().hex[:8],
                payload={"amount": chunk, "beneficiary_id": "stealth_bene_1"}
            ))
            extracted += chunk
            
        return events

    def generate_sleepy_takeover(self, base_state: AccountTrustState, target_amount: float) -> List[RiskEvent]:
        events = []
        t = datetime.utcnow() - timedelta(days=40)
        
        # New device registered long ago
        events.append(RiskEvent(
            event_id=f"EVT_{uuid.uuid4().hex[:8]}", tenant_id="t1", entity_id=base_state.entity_id,
            event_type="DEVICE_REGISTERED", event_time=t, source="auth", source_event_id="s2",
            payload={"device_id": "sleepy_dev"}
        ))
        
        # Dormant for 40 days
        t += timedelta(days=40)
        events.append(RiskEvent(
            event_id=f"EVT_{uuid.uuid4().hex[:8]}", tenant_id="t1", entity_id=base_state.entity_id,
            event_type="TRANSFER_COMPLETED", event_time=t, source="core", source_event_id="s3",
            payload={"amount": target_amount, "beneficiary_id": "sleepy_bene"}
        ))
        return events
        
    def run_lab(self):
        print("========================================")
        print("ADVERSARIAL REALITY LAB - SPRINT 3")
        print("========================================")
        
        base_state = AccountTrustState(tenant_id="t1", entity_id="victim_1")
        base_state.median_amount = 500.0
        base_state.mad_amount = 100.0
        base_state.known_devices = {"legit_dev_1"}
        base_state.total_transactions = 100
        
        print("\n[ATTACK 1: LOW AND SLOW THRESHOLD PROBING]")
        target = 10000.0
        events = self.generate_low_and_slow(base_state, target)
        risk, action, extracted = self.evaluate_sequence(events, base_state)
        print(f"Objective: Extract {target}")
        print(f"Risk Reached: {risk:.2f}")
        print(f"Action Triggered: {action}")
        print(f"Money Extracted: {extracted}")
        if extracted >= target and action == "ALLOW":
            print(">>> EVASION SUCCESSFUL. Adding to Nightmare Set.")
            self.nightmare_set.append(("LOW_AND_SLOW", events))
            
        print("\n[ATTACK 2: SLEEPY TAKEOVER (TIME DECAY EVASION)]")
        target = 5000.0
        events = self.generate_sleepy_takeover(base_state, target)
        risk, action, extracted = self.evaluate_sequence(events, base_state)
        print(f"Objective: Extract {target} via time-decay evasion")
        print(f"Risk Reached: {risk:.2f}")
        print(f"Action Triggered: {action}")
        print(f"Money Extracted: {extracted}")
        if extracted >= target and action == "ALLOW":
            print(">>> EVASION SUCCESSFUL. Adding to Nightmare Set.")
            self.nightmare_set.append(("SLEEPY_TAKEOVER", events))
            
if __name__ == "__main__":
    lab = AdversarialLab()
    lab.run_lab()
