import random
import uuid
from datetime import datetime, timedelta
from typing import List, Tuple
from app.services.risk.events import RiskEvent
from app.services.risk.engines import RiskFusionEngine, AccountTrustState

class RiskDatasetGenerator:
    def __init__(self, tenant_id: str = "tenant_global"):
        self.tenant_id = tenant_id

    def generate_normal_account_history(self, entity_id: str, count: int, start_time: datetime) -> Tuple[AccountTrustState, List[RiskEvent]]:
        state = AccountTrustState(tenant_id=self.tenant_id, entity_id=entity_id)
        events = []
        current_time = start_time
        
        # Initial setup
        dev_id = f"dev_{uuid.uuid4().hex[:8]}"
        ip = f"192.168.1.{random.randint(1, 255)}"
        
        e1 = RiskEvent(
            event_id=f"EVT_{uuid.uuid4().hex[:8]}", tenant_id=self.tenant_id, entity_id=entity_id,
            event_type="DEVICE_REGISTERED", event_time=current_time, source="auth", source_event_id=uuid.uuid4().hex[:8],
            payload={"device_id": dev_id}
        )
        events.append(e1)
        state.apply_event(e1)
        
        for i in range(count):
            current_time += timedelta(hours=random.randint(2, 48))
            amount = random.uniform(10.0, 500.0)
            
            # Login
            e_log = RiskEvent(
                event_id=f"EVT_{uuid.uuid4().hex[:8]}", tenant_id=self.tenant_id, entity_id=entity_id,
                event_type="LOGIN_SUCCESS", event_time=current_time, source="auth", source_event_id=uuid.uuid4().hex[:8],
                payload={"device_id": dev_id, "ip": ip}
            )
            events.append(e_log)
            state.apply_event(e_log)
            
            current_time += timedelta(minutes=random.randint(1, 10))
            
            e_pay = RiskEvent(
                event_id=f"EVT_{uuid.uuid4().hex[:8]}", tenant_id=self.tenant_id, entity_id=entity_id,
                event_type="PAYMENT_COMPLETED", event_time=current_time, source="gateway", source_event_id=uuid.uuid4().hex[:8],
                payload={"amount": amount}
            )
            events.append(e_pay)
            state.apply_event(e_pay)
            
        # Update robust stats
        amounts = [e.payload["amount"] for e in events if e.event_type == "PAYMENT_COMPLETED"]
        if amounts:
            amounts.sort()
            state.median_amount = amounts[len(amounts)//2]
            mad_amounts = sorted([abs(a - state.median_amount) for a in amounts])
            state.mad_amount = mad_amounts[len(mad_amounts)//2] or 1.0
            
        return state, events

    def generate_attack_scenario(self, state: AccountTrustState, history: List[RiskEvent], current_time: datetime) -> List[RiskEvent]:
        # Phase 25: Generate synthetic attack (SIM takeover / Device takeover -> Drain)
        events = []
        
        e1 = RiskEvent(
            event_id=f"EVT_{uuid.uuid4().hex[:8]}", tenant_id=self.tenant_id, entity_id=state.entity_id,
            event_type="DEVICE_REGISTERED", event_time=current_time, source="auth", source_event_id=uuid.uuid4().hex[:8],
            payload={"device_id": f"dev_hacker_{uuid.uuid4().hex[:4]}"}
        )
        events.append(e1)
        
        current_time += timedelta(minutes=2)
        e2 = RiskEvent(
            event_id=f"EVT_{uuid.uuid4().hex[:8]}", tenant_id=self.tenant_id, entity_id=state.entity_id,
            event_type="PIN_RESET", event_time=current_time, source="auth", source_event_id=uuid.uuid4().hex[:8],
            payload={}
        )
        events.append(e2)
        
        current_time += timedelta(minutes=5)
        e3 = RiskEvent(
            event_id=f"EVT_{uuid.uuid4().hex[:8]}", tenant_id=self.tenant_id, entity_id=state.entity_id,
            event_type="BENEFICIARY_CREATED", event_time=current_time, source="core", source_event_id=uuid.uuid4().hex[:8],
            payload={"beneficiary_id": "bene_mule_1"}
        )
        events.append(e3)
        
        current_time += timedelta(minutes=1)
        e4 = RiskEvent(
            event_id=f"EVT_{uuid.uuid4().hex[:8]}", tenant_id=self.tenant_id, entity_id=state.entity_id,
            event_type="TRANSFER_COMPLETED", event_time=current_time, source="core", source_event_id=uuid.uuid4().hex[:8],
            payload={"amount": state.median_amount * 20, "graph_fan_out": 25}
        )
        events.append(e4)
        return events

def run_benchmark():
    gen = RiskDatasetGenerator()
    fusion = RiskFusionEngine()
    
    print("Generating Benchmark Dataset...")
    state, history = gen.generate_normal_account_history("user_test", 50, datetime.utcnow() - timedelta(days=30))
    attack_events = gen.generate_attack_scenario(state, history, datetime.utcnow())
    
    print(f"Normal History Events: {len(history)}")
    print(f"Attack Events: {len(attack_events)}")
    
    print("\n--- ATTACK EVALUATION ---")
    sim_state = state.model_copy(deep=True)
    sim_history = history.copy()
    for e in attack_events:
        res = fusion.evaluate_risk(e, sim_state, sim_history)
        sim_state.apply_event(e)
        sim_history.append(e)
        print(f"[{e.event_time.strftime('%H:%M:%S')}] {e.event_type:22} -> RISK: {res.risk_probability:.2f} ({res.risk_band}) | ACTION: {res.recommended_action}")

if __name__ == "__main__":
    run_benchmark()
