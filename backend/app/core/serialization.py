import json
from decimal import Decimal
from datetime import datetime, timezone
from enum import Enum
from typing import Any

def to_json_safe(value: Any) -> Any:
    """
    Recursively converts domain types (Decimal, datetime, Enum) into
    canonical JSON-safe primitives (str, float, int, bool, None).
    """
    if value is None:
        return None
    if isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, Decimal):
        # Canonical decimal string format
        return str(value)
    if isinstance(value, datetime):
        # Canonical ISO-8601 UTC string
        if value.tzinfo is None:
            raise ValueError("Naive datetime objects are not allowed in canonical serialization.")
        return value.astimezone(timezone.utc).isoformat()
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {str(k): to_json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [to_json_safe(x) for x in value]
    
    # Check for Pydantic v2
    if hasattr(value, "model_dump"):
        return to_json_safe(value.model_dump(mode="json"))
    # Check for Pydantic v1
    if hasattr(value, "dict"):
        return to_json_safe(value.dict())
        
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")

def canonical_json_bytes(value: Any) -> bytes:
    """
    Produces deterministic byte representation for hashing.
    Keys are sorted, separators are deterministic.
    """
    safe_dict = to_json_safe(value)
    return json.dumps(safe_dict, sort_keys=True, separators=(',', ':')).encode('utf-8')
