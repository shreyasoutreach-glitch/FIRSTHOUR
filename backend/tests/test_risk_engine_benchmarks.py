import pytest
from datetime import datetime, timedelta, timezone
import uuid

from app.services.risk.events import RiskEvent, AccountTrustState
from app.services.risk.engines import RiskFusionEngine

def create_event(event_type: str, time_offset_sec: int, payload: dict) -> RiskEvent:
    return RiskEvent(
        event_id=f"EVT_{uuid.uuid4().hex[:8]}",
        tenant_id="tenant_test",
        entity_id="user_123",
        event_type=event_type,
        event_time=datetime(2026, 9, 13, 10, 42, 11, tzinfo=timezone.utc) + timedelta(seconds=time_offset_sec),
        source="system",
        source_event_id=uuid.uuid4().hex[:8],
        payload=payload
    )

def test_flagship_attack_scenario():
    """Phase 28: Flagship Attack Scenario"""
    fusion = RiskFusionEngine()
    state = AccountTrustState(tenant_id="tenant_test", entity_id="user_123")
    
    # Pre-warm state with normal behavior
    state.median_amount = 500.0
    state.mad_amount = 100.0
    state.known_devices = {"device_alpha"}
    
    events = []
    
    # 10:43:08 NEW DEVICE
    e1 = create_event("DEVICE_REGISTERED", 57, {"device_id": "device_hacker"})
    events.append(e1)
    state.apply_event(e1)
    
    # 10:43:14 AUTH RE-REGISTRATION (SIMULATED AS PIN RESET FOR NOW)
    e2 = create_event("PIN_RESET", 63, {})
    events.append(e2)
    state.apply_event(e2)
    
    # 10:45:01 NEW BENEFICIARY
    e3 = create_event("BENEFICIARY_CREATED", 170, {"beneficiary_id": "bene_mule"})
    events.append(e3)
    state.apply_event(e3)
    
    # 10:47:13 ₹1,00,00,000 TRANSFER
    e4 = create_event("TRANSFER_COMPLETED", 302, {"amount": 10000000.0, "graph_fan_out": 20})
    events.append(e4)
    state.apply_event(e4)
    
    # Evaluate at the end
    result = fusion.evaluate_risk(e4, state, events[:-1])
    
    assert result.risk_band in ("HIGH", "CRITICAL")
    assert result.recommended_action in ("HOLD_AND_REVIEW", "BLOCK_RECOMMENDED")
    assert "SUSPICIOUS_EVENT_SEQUENCE" in result.reason_codes
    assert "ANOMALOUS_BEHAVIOR" in result.reason_codes

def test_legitimate_control_scenario():
    """Phase 29: Legitimate Control Scenario"""
    fusion = RiskFusionEngine()
    state = AccountTrustState(tenant_id="tenant_test", entity_id="user_123")
    
    # Pre-warm state with normal behavior
    state.median_amount = 500.0
    state.mad_amount = 100.0
    state.known_devices = {"device_alpha"}
    
    events = []
    
    # 10:43 NEW PHONE
    e1 = create_event("DEVICE_REGISTERED", 60, {"device_id": "device_new_iphone"})
    events.append(e1)
    state.apply_event(e1)
    
    # 10:44 TRAVEL LOCATION
    e2 = create_event("IP_CHANGE", 120, {"ip": "travel_ip"})
    events.append(e2)
    state.apply_event(e2)
    
    # 10:45 KNOWN AUTHENTICATION (NO PIN RESET)
    e3 = create_event("LOGIN_SUCCESS", 180, {"device_id": "device_new_iphone"})
    events.append(e3)
    state.apply_event(e3)
    
    # 10:47 LARGE LEGITIMATE TRANSACTION (but no mule graph)
    e4 = create_event("TRANSFER_COMPLETED", 300, {"amount": 1500.0, "graph_fan_in": 1, "graph_fan_out": 1})
    events.append(e4)
    state.apply_event(e4)
    
    # 10:48 KNOWN BENEFICIARY
    e5 = create_event("PAYOUT_COMPLETED", 360, {"amount": 500.0})
    events.append(e5)
    state.apply_event(e5)
    
    # Evaluate at the transfer
    result = fusion.evaluate_risk(e4, state, events[:3])
    
    # Must NOT produce the same result as the takeover scenario.
    assert result.risk_band in ("LOW", "MEDIUM")
    assert result.recommended_action in ("ALLOW", "STEP_UP")

def test_baseline_leakage_protection():
    """Phase 5: Baseline Leakage Protection"""
    state = AccountTrustState(tenant_id="tenant_test", entity_id="user_123")
    state.median_amount = 500.0
    state.mad_amount = 100.0
    
    # Simulate an active incident
    state.active_incident_id = "INC_999"
    
    e1 = create_event("LOGIN_SUCCESS", 10, {"device_id": "hacker_device"})
    state.apply_event(e1)
    
    # The device should NOT be trusted because of the active incident
    assert "hacker_device" not in state.known_devices
    
def test_tamper_evident_hash_chain():
    """Phase 3: Hash Chain Integrity"""
    state = AccountTrustState(tenant_id="tenant_test", entity_id="user_123")
    
    e1 = create_event("LOGIN_SUCCESS", 10, {"device_id": "device_1"})
    state.apply_event(e1)
    assert e1.verify_integrity() is True
    
    e2 = create_event("PIN_RESET", 20, {})
    state.apply_event(e2)
    assert e2.previous_event_hash == e1.payload_hash
    assert e2.verify_integrity() is True
    
    # Tamper with e1 payload
    e1.payload.__dict__["device_id"] = "hacker_device"
    assert e1.verify_integrity() is False
