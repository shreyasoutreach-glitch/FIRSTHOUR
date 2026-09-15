from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from .events import RiskEvent, AccountTrustState

class RiskEvaluation(BaseModel):
    decision_id: str
    risk_probability: float
    risk_band: str # LOW, MEDIUM, HIGH, CRITICAL
    recommended_action: str
    reason_codes: List[str]
    supporting_event_ids: List[str]
    model_version: str = "1.0.0"
    calibration_version: str = "1.0.0"
    feature_version: str = "1.0.0"
    policy_version: str = "1.0.0"
    evaluated_at: datetime
    competing_hypotheses: Dict[str, float]

class IdentityEngine:
    def evaluate(self, event: RiskEvent, state: AccountTrustState, recent_history: List[RiskEvent]) -> float:
        risk = 0.0
        # Check current event
        if event.event_type == "PIN_RESET": risk += 0.4
        elif event.event_type == "DEVICE_REGISTERED": risk += 0.3
        
        # Check recent history (Phase 13: continuous risk accumulation)
        # Apply Temporal Decay: events older than 7 days contribute no active identity risk
        recent_types = []
        for e in recent_history:
            if (event.event_time - e.event_time).days <= 7:
                recent_types.append(e.event_type)
                
        if "PIN_RESET" in recent_types: risk += 0.4
        if "DEVICE_REGISTERED" in recent_types: risk += 0.3
        
        return min(risk, 1.0)

class BehavioralEngine:
    def evaluate(self, event: RiskEvent, state: AccountTrustState, recent_history: List[RiskEvent]) -> float:
        if event.event_type not in ("TRANSFER_COMPLETED", "PAYOUT_COMPLETED", "PAYMENT_COMPLETED"):
            return 0.0
            
        raw_amount = float(dict(event.payload).get('amount', 0.0))
        if raw_amount < 0:
            raise ValueError(f'Negative amounts are semantically invalid for {event.event_type}')
        amount = raw_amount
        
        # Calculate recent velocity
        recent_transfers = [e for e in recent_history if e.event_type == "TRANSFER_COMPLETED" and (event.event_time - e.event_time).days <= 1]
        cumulative_24h = sum(dict(e.payload).get("amount", 0.0) for e in recent_transfers) + amount
        
        # Velocity check: if 24h volume > median * 10, that's a velocity spike even if individual txns are small
        velocity_risk = 0.0
        if state.median_amount > 0:
            if cumulative_24h > state.median_amount * 15:
                velocity_risk = 0.8
            elif cumulative_24h > state.median_amount * 8:
                velocity_risk = 0.4
            
        # Robust z-score check
        z_risk = 0.0
        if state.mad_amount > 0:
            epsilon = 1e-6
            z = 0.6745 * (amount - state.median_amount) / (state.mad_amount + epsilon)
            if z > 10: z_risk = 0.8
            elif z > 5: z_risk = 0.5
            elif z > 3: z_risk = 0.2
            
        return max(z_risk, velocity_risk)

class GraphEngine:
    def evaluate(self, event: RiskEvent, state: AccountTrustState, recent_history: List[RiskEvent]) -> float:
        # Phase 14: Network Intelligence (Fan-In / Fan-Out)
        # Catching the Sprint 3 Low-and-Slow Attack via Graph Mule detection
        fan_in = dict(event.payload).get("graph_fan_in", 1)
        fan_out = dict(event.payload).get("graph_fan_out", 1)
        cross_tenant_velocity = dict(event.payload).get("network_velocity", 0.0)
        
        # Check history for large fan outs
        for e in recent_history:
            fan_in = max(fan_in, dict(e.payload).get("graph_fan_in", 1))
            fan_out = max(fan_out, dict(e.payload).get("graph_fan_out", 1))
            
        risk = 0.0
        # If multiple victims are transferring to the same beneficiary (Mule Fan-In)
        if fan_in > 3: 
            risk = max(risk, 0.7)
        if fan_in > 10: 
            risk = max(risk, 0.9)
            
        # Large fan out (Distribution Mule)
        if fan_out > 10: 
            risk = max(risk, 0.8)
            
        return risk

class SequenceEngine:
    def evaluate(self, recent_events: List[RiskEvent], state: AccountTrustState) -> float:
        types = [e.event_type for e in recent_events[-5:]]
        
        score = 0.0
        if "DEVICE_REGISTERED" in types and "PIN_RESET" in types:
            score += 0.6
            if "BENEFICIARY_CREATED" in types:
                score += 0.2
                if "TRANSFER_COMPLETED" in types:
                    score += 0.2
        
        return min(score, 1.0)

class RiskFusionEngine:
    def __init__(self):
        self.identity = IdentityEngine()
        self.behavioral = BehavioralEngine()
        self.graph = GraphEngine()
        self.sequence = SequenceEngine()
        
    def evaluate_risk(self, event: RiskEvent, state: AccountTrustState, recent_history: List[RiskEvent]) -> RiskEvaluation:
        # Phase 10: Risk Fusion (transparent calibrated model)
        id_risk = self.identity.evaluate(event, state, recent_history)
        beh_risk = self.behavioral.evaluate(event, state, recent_history)
        graph_risk = self.graph.evaluate(event, state, recent_history)
        seq_risk = self.sequence.evaluate(recent_history + [event], state)
        
        # Logistic regression abstraction (weights calibrated offline)
        raw_score = (id_risk * 0.3) + (beh_risk * 0.2) + (graph_risk * 0.2) + (seq_risk * 0.3)
        
        # Phase 22 & 44: Non-linear activation for Stealth Attacks
        # Check if recently strongly authenticated
        is_strongly_authenticated = any(
            e.event_type == "LOGIN_SUCCESS" and dict(e.payload).get("mfa_verified", False) 
            for e in recent_history if (event.event_time - e.event_time).days == 0
        )
        
        # If behavior is extreme, only suppress if strongly authenticated.
        if beh_risk >= 0.8 and not is_strongly_authenticated:
            # Huge uncharacteristic drain without explicit same-day MFA -> HIGH RISK
            raw_score = max(raw_score, 0.75) 
            
        # Phase 14: Network Mule Override
        # If multiple victims fan-in to this beneficiary, bypass all linear weights.
        # This explicitly defeats isolated behavioral Low-and-Slow evasions.
        if graph_risk >= 0.7:
            raw_score = max(raw_score, 0.85) # CRITICAL

        prob = min(max(raw_score, 0.0), 1.0)
        
        # Competing Hypotheses (Phase 8)
        hypotheses = {
            "H0_legitimate_normal": 1.0 - prob if prob < 0.3 else 0.1,
            "H1_legitimate_unusual": prob if 0.3 <= prob < 0.6 else 0.1,
            "H2_account_takeover": prob if prob >= 0.6 else 0.05,
            "H3_device_compromise": id_risk,
        }
        
        band = "LOW"
        action = "ALLOW"
        if prob >= 0.85:
            band = "CRITICAL"
            action = "BLOCK_RECOMMENDED"
        elif prob >= 0.60:
            band = "HIGH"
            action = "HOLD_AND_REVIEW"
        elif prob >= 0.35:
            band = "MEDIUM"
            action = "STEP_UP"
            
        reasons = []
        if id_risk > 0.4: reasons.append("HIGH_IDENTITY_RISK")
        if beh_risk > 0.4: reasons.append("ANOMALOUS_BEHAVIOR")
        if graph_risk > 0.4: reasons.append("SUSPICIOUS_GRAPH_TOPOLOGY")
        if seq_risk > 0.4: reasons.append("SUSPICIOUS_EVENT_SEQUENCE")
        if not reasons: reasons.append("NORMAL_ACTIVITY")
        
        from datetime import datetime, timezone
        return RiskEvaluation(
            decision_id=f"DEC_{event.event_id}",
            risk_probability=prob,
            risk_band=band,
            recommended_action=action,
            reason_codes=reasons,
            supporting_event_ids=[e.event_id for e in recent_history[-3:]] + [event.event_id],
            evaluated_at=datetime.now(timezone.utc),
            competing_hypotheses=hypotheses
        )






