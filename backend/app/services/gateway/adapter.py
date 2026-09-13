import os
from typing import Protocol, List, Dict, Any, Optional
from pydantic import BaseModel

class NormalizedPayment(BaseModel):
    id: str
    tenant_id: str
    amount: float
    currency: str
    status: str
    gateway_reference: str
    created_at: str

class NormalizedPayout(BaseModel):
    id: str
    tenant_id: str
    amount: float
    currency: str
    status: str
    beneficiary_name: str
    gateway_reference: str
    created_at: str

class GatewayAdapter(Protocol):
    def sync_payments(self, tenant_id: str, since: Optional[str] = None) -> List[NormalizedPayment]:
        ...
        
    def sync_payouts(self, tenant_id: str, since: Optional[str] = None) -> List[NormalizedPayout]:
        ...
        
    def simulate_freeze(self, target_id: str) -> Dict[str, Any]:
        ...
        
    def simulate_reversal(self, target_id: str) -> Dict[str, Any]:
        ...
