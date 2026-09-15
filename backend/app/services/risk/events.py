import hashlib
from decimal import Decimal
from datetime import datetime
from typing import Any, Dict, Optional, Literal, Union
from pydantic import BaseModel, Field
from app.core.serialization import canonical_json_bytes

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
    # ACCOUNTING EXTENSIONS
    "REFUND", "REVERSAL", "CHARGEBACK",
    # BENEFICIARY
    "BENEFICIARY_CREATED", "BENEFICIARY_CHANGED", "BENEFICIARY_REMOVED",
    # TELECOM
    "SIM_CHANGED", "SIM_REPLACED", "NUMBER_PORTED",
    # INCIDENT
    "CUSTOMER_REPORTED", "FRAUD_CONFIRMED", "FRAUD_DISMISSED", "ACCOUNT_LOCKED", "ACCOUNT_UNLOCKED"
]

class RiskEventPayload(BaseModel):
    amount: Optional[Decimal] = None
    velocity_amount: Optional[Decimal] = None
    exposure: Optional[Decimal] = None
    risk_score: Optional[float] = None
    z_score: Optional[float] = None
    transaction_id: Optional[str] = None
    device_id: Optional[str] = None
    ip: Optional[str] = None
    beneficiary_id: Optional[str] = None
    status: Optional[str] = None
    # For generic unstructured fields
    class Config:
        extra = "allow"

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
    payload: RiskEventPayload
    payload_hash: str = ""
    previous_event_hash: str = ""
    
    def compute_hash(self) -> str:
        data = {
            "event_id": self.event_id,
            "tenant_id": self.tenant_id,
            "entity_id": self.entity_id,
            "event_type": self.event_type,
            "event_time": self.event_time,
            "payload": self.payload,
            "previous_event_hash": self.previous_event_hash
        }
        encoded = canonical_json_bytes(data)
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
    median_amount: Decimal = Decimal(0)
    mad_amount: Decimal = Decimal(0)
    total_transactions: int = 0
    active_incident_id: Optional[str] = None
    current_risk_score: float = 0.0
    first_divergence_at: datetime | None = None
    last_event_hash: str = ""
    
    def apply_event(self, event: RiskEvent):
        if self.first_seen is None:
            self.first_seen = event.event_time
        self.last_seen = event.event_time
        
        event.previous_event_hash = self.last_event_hash
        event.payload_hash = event.compute_hash()
        self.last_event_hash = event.payload_hash
        
        if self.active_incident_id is not None:
            return
            
        if event.event_type in ("LOGIN_SUCCESS", "SESSION_START"):
            if event.payload.device_id:
                self.known_devices.add(event.payload.device_id)
            if event.payload.ip:
                self.known_ips.add(event.payload.ip)
        elif event.event_type == "BENEFICIARY_CREATED":
            if event.payload.beneficiary_id:
                self.known_beneficiaries.add(event.payload.beneficiary_id)
