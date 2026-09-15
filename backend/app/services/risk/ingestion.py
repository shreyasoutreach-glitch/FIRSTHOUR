from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import uuid
from app.services.risk.events import RiskEvent, EventType

class CustomerSchemaMapping:
    def __init__(self, mapping: Dict[str, str]):
        """
        mapping example:
        {
            "event_time": "transaction_timestamp",
            "entity_id": "customer_account_id",
            "amount": "transaction_amount",
            "beneficiary_id": "destination_account",
            "event_type": "type_code"
        }
        """
        self.mapping = mapping

class CustomerDataAdapter:
    def __init__(self, tenant_id: str, schema: CustomerSchemaMapping):
        self.tenant_id = tenant_id
        self.schema = schema.mapping

    def normalize_event(self, raw_payload: Dict[str, Any]) -> RiskEvent:
        # Extract mapped fields safely
        try:
            entity_id = raw_payload[self.schema.get("entity_id", "entity_id")]
            raw_time = raw_payload[self.schema.get("event_time", "event_time")]
            if isinstance(raw_time, str):
                event_time = datetime.fromisoformat(raw_time.replace('Z', '+00:00'))
                if event_time.tzinfo is None: event_time = event_time.replace(tzinfo=timezone.utc)
            else:
                event_time = raw_time
                
            raw_type = raw_payload[self.schema.get("event_type", "event_type")]
        except KeyError as e:
            raise ValueError(f"Missing required mapped field: {e}")

        # Map event types to canonical FIRST HOUR ontology
        event_type = self._map_event_type(raw_type)

        # Construct canonical payload
        payload = {}
        if "amount" in self.schema and self.schema["amount"] in raw_payload:
            payload["amount"] = float(raw_payload[self.schema["amount"]])
        if "beneficiary_id" in self.schema and self.schema["beneficiary_id"] in raw_payload:
            payload["beneficiary_id"] = str(raw_payload[self.schema["beneficiary_id"]])
        if "ip" in self.schema and self.schema["ip"] in raw_payload:
            payload["ip"] = str(raw_payload[self.schema["ip"]])
        if "device_id" in self.schema and self.schema["device_id"] in raw_payload:
            payload["device_id"] = str(raw_payload[self.schema["device_id"]])

        return RiskEvent(
            event_id=f"EVT_{uuid.uuid4().hex[:8]}",
            tenant_id=self.tenant_id,
            entity_id=entity_id,
            event_type=event_type,
            event_time=event_time,
            source="customer_import",
            source_event_id=raw_payload.get("transaction_id", uuid.uuid4().hex),
            payload=payload
        )

    def _map_event_type(self, raw_type: str) -> EventType:
        raw = str(raw_type).upper()
        if "LOGIN" in raw: return "LOGIN_SUCCESS"
        if "TRANSFER" in raw or "PAYMENT" in raw: return "TRANSFER_COMPLETED"
        if "DEVICE" in raw: return "DEVICE_REGISTERED"
        if "PIN" in raw or "PASSWORD" in raw: return "PIN_RESET"
        if "BENEFICIARY" in raw or "PAYEE" in raw: return "BENEFICIARY_CREATED"
        # Fallback to a safe standard event
        return "CUSTOMER_REPORTED"
