import pytest
from decimal import Decimal
from datetime import datetime, timezone
import enum
from app.core.serialization import to_json_safe, canonical_json_bytes
import json
import hashlib

class TestEnum(enum.Enum):
    STATUS_OK = "ok"

def test_canonical_serialization_roundtrip_nested():
    aware_dt = datetime(2026, 9, 13, 10, 42, 11, tzinfo=timezone.utc)
    domain_obj = {
        "amount": Decimal("1234.567890"),
        "risk_probability": 0.9342,
        "timestamp": aware_dt,
        "status": TestEnum.STATUS_OK,
        "nested": {
            "amount": Decimal("0.000001")
        }
    }
    
    # JSON-safe
    safe = to_json_safe(domain_obj)
    
    # Canonical Bytes
    b = canonical_json_bytes(domain_obj)
    s = b.decode("utf-8")
    assert s == '{"amount":"1234.567890","nested":{"amount":"0.000001"},"risk_probability":0.9342,"status":"ok","timestamp":"2026-09-13T10:42:11+00:00"}'
    
    # Hash stability
    h1 = hashlib.sha256(b).hexdigest()
    h2 = hashlib.sha256(canonical_json_bytes(domain_obj)).hexdigest()
    assert h1 == h2
