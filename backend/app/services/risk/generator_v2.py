import time
from datetime import datetime, timedelta
import random
import uuid
from typing import List
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, Base, engine
from app.models.risk import RiskEventModel, AccountTrustStateModel, GraphRelationshipModel
from app.services.risk.engines import RiskFusionEngine
from app.services.risk.events import RiskEvent, AccountTrustState
from app.services.risk.sprint2 import PointInTimeEventSourcing, ShadowModeLogger

def generate_stealth_attack(gen_time: datetime, entity_id: str) -> List[RiskEvent]:
    # Phase 22: Stealth Attacks (Long dwell time, familiar IPs)
    events = []
    # Attacker uses familiar IP (compromised router/VPN)
    ip = "192.168.1.100" # pretend it's familiar
    dev = "dev_stealth_1"
    
    events.append(RiskEvent(
        event_id=f"EVT_{uuid.uuid4().hex[:8]}", tenant_id="t1", entity_id=entity_id,
        event_type="LOGIN_SUCCESS", event_time=gen_time, source="auth", source_event_id=uuid.uuid4().hex[:8],
        payload={"ip": ip, "device_id": dev}
    ))
    
    # Wait hours (stealth)
    gen_time += timedelta(hours=14)
    events.append(RiskEvent(
        event_id=f"EVT_{uuid.uuid4().hex[:8]}", tenant_id="t1", entity_id=entity_id,
        event_type="BENEFICIARY_CREATED", event_time=gen_time, source="core", source_event_id=uuid.uuid4().hex[:8],
        payload={"beneficiary_id": "stealth_bene_1"}
    ))
    
    # Test transaction (small)
    gen_time += timedelta(hours=2)
    events.append(RiskEvent(
        event_id=f"EVT_{uuid.uuid4().hex[:8]}", tenant_id="t1", entity_id=entity_id,
        event_type="TRANSFER_COMPLETED", event_time=gen_time, source="core", source_event_id=uuid.uuid4().hex[:8],
        payload={"amount": 15.0, "beneficiary_id": "stealth_bene_1"}
    ))
    
    # Actual drain
    gen_time += timedelta(hours=24)
    events.append(RiskEvent(
        event_id=f"EVT_{uuid.uuid4().hex[:8]}", tenant_id="t1", entity_id=entity_id,
        event_type="TRANSFER_COMPLETED", event_time=gen_time, source="core", source_event_id=uuid.uuid4().hex[:8],
        payload={"amount": 49000.0, "beneficiary_id": "stealth_bene_1"} # just under typical 50k limit
    ))
    return events

def generate_legitimate_camouflage(gen_time: datetime, entity_id: str) -> List[RiskEvent]:
    # Phase 23: Legitimate Camouflage (Looks like ATO but is legitimate)
    events = []
    # New phone + new city + large purchase (but trusted auth & no rapid drain)
    dev = "dev_new_iphone_15"
    events.append(RiskEvent(
        event_id=f"EVT_{uuid.uuid4().hex[:8]}", tenant_id="t1", entity_id=entity_id,
        event_type="DEVICE_REGISTERED", event_time=gen_time, source="auth", source_event_id=uuid.uuid4().hex[:8],
        payload={"device_id": dev}
    ))
    gen_time += timedelta(minutes=5)
    events.append(RiskEvent(
        event_id=f"EVT_{uuid.uuid4().hex[:8]}", tenant_id="t1", entity_id=entity_id,
        event_type="LOGIN_SUCCESS", event_time=gen_time, source="auth", source_event_id=uuid.uuid4().hex[:8],
        payload={"ip": "travel_ip", "device_id": dev, "mfa_verified": True}
    ))
    gen_time += timedelta(hours=1)
    events.append(RiskEvent(
        event_id=f"EVT_{uuid.uuid4().hex[:8]}", tenant_id="t1", entity_id=entity_id,
        event_type="BENEFICIARY_CREATED", event_time=gen_time, source="core", source_event_id=uuid.uuid4().hex[:8],
        payload={"beneficiary_id": "supplier_x"}
    ))
    gen_time += timedelta(minutes=10)
    events.append(RiskEvent(
        event_id=f"EVT_{uuid.uuid4().hex[:8]}", tenant_id="t1", entity_id=entity_id,
        event_type="TRANSFER_COMPLETED", event_time=gen_time, source="core", source_event_id=uuid.uuid4().hex[:8],
        payload={"amount": 100000.0, "beneficiary_id": "supplier_x", "purpose": "business_expansion"}
    ))
    return events

def generate_bulk_dataset(accounts: int, normal_per_acct: int):
    print("Generating massive dataset in memory...")
    events = []
    attacks = []
    camouflages = []
    start_time = datetime.utcnow() - timedelta(days=90)
    
    for i in range(accounts):
        acct = f"acct_{i}"
        cur_time = start_time + timedelta(days=random.randint(0, 30))
        for j in range(normal_per_acct):
            cur_time += timedelta(hours=random.randint(12, 72))
            events.append(RiskEvent(
                event_id=f"EVT_{uuid.uuid4().hex[:8]}", tenant_id="t1", entity_id=acct,
                event_type="LOGIN_SUCCESS", event_time=cur_time, source="auth", source_event_id=uuid.uuid4().hex[:8],
                payload={"ip": "1.1.1.1", "device_id": f"dev_{i}"}
            ))
            events.append(RiskEvent(
                event_id=f"EVT_{uuid.uuid4().hex[:8]}", tenant_id="t1", entity_id=acct,
                event_type="TRANSFER_COMPLETED", event_time=cur_time+timedelta(minutes=5), source="core", source_event_id=uuid.uuid4().hex[:8],
                payload={"amount": random.uniform(50, 500), "beneficiary_id": f"bene_{i}"}
            ))
            
        # Add varied scenarios
        r = random.random()
        if r < 0.05:
            attacks.extend(generate_stealth_attack(cur_time + timedelta(days=2), acct))
        elif r < 0.10:
            camouflages.extend(generate_legitimate_camouflage(cur_time + timedelta(days=2), acct))
            
    return events, attacks, camouflages

def run_e2e_benchmark():
    # 10,000 accounts * 10 events = 100,000 events.
    # To keep script within realistic CI timeout for this demonstration, I'll generate 2,000 accounts = 20,000 events + attacks
    # If the environment handles it, I'll scale it to 10k.
    t0 = time.time()
    events, attacks, camouflages = generate_bulk_dataset(5000, 10) 
    print(f"Generated {len(events)} normal, {len(attacks)} attacks, {len(camouflages)} camouflage events in {time.time()-t0:.2f}s")
    
    # We will simulate the evaluate_risk performance
    fusion = RiskFusionEngine()
    
    t1 = time.time()
    # E2E Benchmark on the attacks
    print("\nEvaluating Stealth Attacks...")
    detected = 0
    state = AccountTrustState(tenant_id="t1", entity_id="test")
    state.median_amount = 200
    state.mad_amount = 50
    state.known_devices = {"dev_stealth_1"} # Familiar device!
    
    # Let's run fusion on stealth events
    hist = []
    for e in generate_stealth_attack(datetime.utcnow(), "test"):
        res = fusion.evaluate_risk(e, state, hist)
        hist.append(e)
        if res.risk_probability > 0.6:
            detected += 1
            
    print(f"Stealth Attack Detection Rate: {detected}/4 events crossed HIGH threshold.")
    
    print("\nEvaluating Legitimate Camouflage...")
    false_positives = 0
    hist = []
    for e in generate_legitimate_camouflage(datetime.utcnow(), "test"):
        res = fusion.evaluate_risk(e, state, hist)
        hist.append(e)
        if res.risk_probability > 0.6:
            false_positives += 1
            
    print(f"Legitimate Camouflage False Positive Events: {false_positives}/4")
    
if __name__ == "__main__":
    run_e2e_benchmark()
