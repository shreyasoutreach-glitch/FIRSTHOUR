import hashlib
import json
from datetime import datetime
from typing import Any, Dict, Optional, Literal
from pydantic import BaseModel, Field

EventType = Literal[
    # IDENTITY
    "ACCOUNT_CREATED", "ACCOUNT_PROFILE_CHANGED", "PHONE_CHANGED", "EMAIL_CHANGED",
    # DEVICE
    "DEVICE_REGISTERED", "DEVICE_CHANGED", "DEVICE_REMOVED", "DEVICE_TRUSTED", "DEVICE_UNTRUSTED",
    # NETWORK
    "IP_CHANGE", "ASN_CHANGE", "GEOLOCATION_CHANGE", "SESSION_START", "SESSION_END", "IMPOSSIBLE_TRAVEL",
    # AUTHENTICATION
    "LOGIN_SUCCESS", "LOGIN_FAILURE", "MFA_ENABLED", "MFA_DISABLED", "AUTH_METHOD_CHANGED",
    "PIN_CHANGED", "PIN_RESET", "PASSWORD_CHANGED", "PASSWORD_RESET", "ACCOUNT_RECOVERY", "SESSION_REAUTHENTICATED",
    # PAYMENT
    "PAYMENT_INITIATED", "PAYMENT_COMPLETED", "PAYMENT_FAILED", "PAYOUT_INITIATED", "PAYOUT_COMPLETED",
    "TRANSFER_INITIATED", "TRANSFER_COMPLETED",
    # BENEFICIARY
    "BENEFICIARY_CREATED", "BENEFICIARY_CHANGED", "BENEFICIARY_REMOVED",
    # TELECOM
    "SIM_CHANGED", "SIM_REPLACED", "NUMBER_PORTED",
    # INCIDENT
    "CUSTOMER_REPORTED", "FRAUD_CONFIRMED", "FRAUD_DISMISSED", "ACCOUNT_LOCKED", "ACCOUNT_UNLOCKED"
]

class RiskEvent(BaseModel):
    event_id: str
    tenant_id: str
    entity_id: str
    event_type: EventType
    event_time: datetime
    ingested_at: datetime = Field(default_factory=datetime.utcnow)
    source: str
    source_event_id: str
    schema_version: str = "1.0"
    payload: Dict[str, Any]
    payload_hash: str = ""
    previous_event_hash: str = ""
    
    def compute_hash(self) -> str:
        # Tamper-evident hash chain implementation (Phase 3)
        data = {
            "event_id": self.event_id,
            "tenant_id": self.tenant_id,
            "entity_id": self.entity_id,
            "event_type": self.event_type,
            "event_time": self.event_time.isoformat(),
            "payload": self.payload,
            "previous_event_hash": self.previous_event_hash
        }
        encoded = json.dumps(data, sort_keys=True).encode('utf-8')
        return hashlib.sha256(encoded).hexdigest()

    def verify_integrity(self) -> bool:
        return self.payload_hash == self.compute_hash()

class AccountTrustState(BaseModel):
    tenant_id: str
    entity_id: str
    known_devices: set[str] = Field(default_factory=set)
    known_ips: set[str] = Field(default_factory=set)
    known_beneficiaries: set[str] = Field(default_factory=set)
    first_seen: datetime | None = None
    last_seen: datetime | None = None
    median_amount: float = 0.0
    mad_amount: float = 0.0
    total_transactions: int = 0
    active_incident_id: Optional[str] = None
    current_risk_score: float = 0.0
    first_divergence_at: datetime | None = None
    last_event_hash: str = ""
    
    def apply_event(self, event: RiskEvent):
        # Apply event cleanly without contaminating baseline if an incident is active
        if self.first_seen is None:
            self.first_seen = event.event_time
        self.last_seen = event.event_time
        
        # Link hash chain
        event.previous_event_hash = self.last_event_hash
        event.payload_hash = event.compute_hash()
        self.last_event_hash = event.payload_hash
        
        if self.active_incident_id is not None:
            # Phase 5: Events associated with an active suspected/confirmed incident 
            # must NOT automatically contaminate the trusted baseline.
            return
            
        # Update baseline safely
        if event.event_type in ("LOGIN_SUCCESS", "SESSION_START"):
            if "device_id" in event.payload:
                self.known_devices.add(event.payload["device_id"])
            if "ip" in event.payload:
                self.known_ips.add(event.payload["ip"])
        elif event.event_type == "BENEFICIARY_CREATED":
            if "beneficiary_id" in event.payload:
                self.known_beneficiaries.add(event.payload["beneficiary_id"])

