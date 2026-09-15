import csv
from datetime import datetime
from collections import defaultdict
import json
from decimal import Decimal

def _get(p, key, default=None):
    if isinstance(p, dict):
        return p.get(key, default)
    return getattr(p, key, default)

def _set(p, key, val):
    if isinstance(p, dict):
        p[key] = val
    else:
        setattr(p, key, val)

from app.services.risk.events import RiskEvent, AccountTrustState
from app.services.risk.engines import RiskFusionEngine
from app.services.risk.ingestion import CustomerDataAdapter, CustomerSchemaMapping

def run_replay(csv_file):
    print("--- CUSTOMER ZERO REPLAY INITIATED ---")
    fusion = RiskFusionEngine()
    schema = CustomerSchemaMapping({
        "event_time": "timestamp",
        "entity_id": "account_id",
        "amount": "amount",
        "beneficiary_id": "beneficiary_id",
        "event_type": "event_type",
        "device_id": "device_id",
        "ip": "ip_address",
    })
    adapter = CustomerDataAdapter("t_customer_zero", schema)
    
    events_raw = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            events_raw.append(row)
            
    # Sort chronologically to enforce point-in-time
    events_raw.sort(key=lambda x: x["timestamp"])
    
    state_store = {}
    history_store = defaultdict(list)
    beneficiary_senders = defaultdict(set)
    sender_beneficiaries = defaultdict(set)
    
    metrics = {
        "total_events": 0,
        "accounts": set(),
        "total_exposure": 0.0,
        "prevented_exposure": 0.0,
        "true_positives": 0,
        "false_positives": 0,
        "false_negatives": 0,
        "true_negatives": 0,
        "incidents_detected": set(),
        "missed_fraud": 0.0,
        "friction_cost": 0.0,
        "fp_details": [],
        "fn_details": []
    }
    
    fraud_accounts = set()
    detected_accounts = set()

    for row in events_raw:
        metrics["total_events"] += 1
        account_id = row["account_id"]
        metrics["accounts"].add(account_id)
        
        ground_truth = row["ground_truth"]
        if ground_truth == "FRAUD":
            fraud_accounts.add(account_id)
            metrics["total_exposure"] += float(row.get("amount", 0.0))
            
        # 1. Normalize
        event = adapter.normalize_event(row)
        
        # 2. State setup
        if account_id not in state_store:
            state_store[account_id] = AccountTrustState(tenant_id="t_customer_zero", entity_id=account_id)
        
        state = state_store[account_id]
        hist = history_store[account_id]
        
        # 3. Graph Mocking Point-in-Time
        b_id = _get(event.payload, "beneficiary_id")
        if event.event_type == "TRANSFER_COMPLETED" and b_id:
            beneficiary_senders[b_id].add(account_id)
            sender_beneficiaries[account_id].add(b_id)
            _set(event.payload, "graph_fan_in", len(beneficiary_senders[b_id]))
            _set(event.payload, "graph_fan_out", len(sender_beneficiaries[account_id]))
            
        # 4. Evaluate
        res = fusion.evaluate_risk(event, state, hist)
        action = res.recommended_action
        
        # 5. Measure & React
        is_fraud = (ground_truth == "FRAUD")
        triggered = (action in ["BLOCK_RECOMMENDED", "HOLD_AND_REVIEW"])
        
        amt = Decimal(str(_get(event.payload, "amount", "0")))

        if not is_fraud and triggered and metrics["false_positives"] < 5:
            pass # print(f"DEBUG FP: amt={amt} state_med={state.median_amount} state_mad={state.mad_amount} action={action} score={res.risk_probability:.2f}")
            
        if is_fraud and not triggered and metrics["false_negatives"] < 10:
            print(f"DEBUG FN: amt={amt} state_med={state.median_amount} state_mad={state.mad_amount} "
                  f"action={action} score={res.risk_probability:.2f}")
                  
        if triggered:
            metrics["incidents_detected"].add(account_id)
            detected_accounts.add(account_id)
        if not is_fraud and triggered:
            metrics["false_positives"] += 1
            metrics["friction_cost"] += 10.0
            metrics["fp_details"].append({
                "account": account_id, "amount": float(amt), "median": float(state.median_amount), 
                "score": res.risk_probability, "action": action
            })
        elif is_fraud and not triggered:
            metrics["false_negatives"] += 1
            metrics["missed_fraud"] += float(amt)
            metrics["fn_details"].append({
                "account": account_id, "amount": float(amt), "median": float(state.median_amount),
                "score": res.risk_probability, "action": action
            })
        elif is_fraud and triggered:
            metrics["true_positives"] += 1
            metrics["prevented_exposure"] += float(amt)
        else:
            metrics["true_negatives"] += 1
                
        # 6. Apply state changes
        state.apply_event(event)
        hist.append(event)
        
        # Manually update rolling baseline for this simulation
        if event.event_type == "TRANSFER_COMPLETED" and amt > 0:
            past_amts = [Decimal(str(_get(e.payload, "amount", "0"))) for e in hist if e.event_type == "TRANSFER_COMPLETED" and Decimal(str(_get(e.payload, "amount", "0"))) > 0]
            if past_amts:
                past_amts.sort()
                mid = len(past_amts) // 2
                med = (Decimal(str(past_amts[mid])) + Decimal(str(past_amts[~mid]))) / Decimal("2.0")
                state.median_amount = med
                
                mads = sorted([abs(x - med) for x in past_amts])
                mad = (mads[len(mads)//2] + mads[~len(mads)//2]) / Decimal("2.0")
                state.mad_amount = mad if mad > 0 else (med * Decimal("0.1") + Decimal("1.0"))
        
    print(f"Events Analyzed: {metrics['total_events']}")
    print(f"Accounts Analyzed: {len(metrics['accounts'])}")
    print(f"Total Fraud Exposure: ${metrics['total_exposure']:,.2f}")
    print(f"Prevented Exposure: ${metrics['prevented_exposure']:,.2f}")
    print(f"Missed Fraud Loss: ${metrics['missed_fraud']:,.2f}")
    print(f"False Positives: {metrics['false_positives']}")
    print(f"True Positives: {metrics['true_positives']}")
    
    # Account level stats
    print(f"\nTotal Compromised Accounts: {len(fraud_accounts)}")
    print(f"Compromised Accounts Detected: {len(fraud_accounts.intersection(detected_accounts))}")
    print(f"Legitimate Accounts Flagged (FP): {len(detected_accounts - fraud_accounts)}")

    with open("customer_zero_forensics.json", "w") as f:
        json.dump({"fp": metrics["fp_details"], "fn": metrics["fn_details"]}, f, indent=2)

if __name__ == "__main__":
    run_replay(r"C:\Users\FIRSTHOUR\first_hour_customer_zero_realistic_fraud_replay.csv")
