# FIRST HOUR: DATA HANDOFF GUIDE

To execute the Customer Zero Replay, we must map your internal telemetry fields to FIRST HOUR's normalized schema. 

## FIELD MAPPING TEMPLATE

| YOUR FIELD (Example) | FIRST HOUR SCHEMA | STATUS | DESCRIPTION |
| :--- | :--- | :--- | :--- |
| `customer_id` | `account_id` | **REQUIRED** | Unique transacting entity. (May be hashed). |
| `created_at` | `event_time` | **REQUIRED** | ISO-8601 Timestamp. |
| `event_name` | `event_type` | **REQUIRED** | e.g., login, transfer. |
| `value` | `amount` | **REQUIRED** | Float. (0.0 for auth events). |
| `currency` | `currency` | **REQUIRED** | 3-letter ISO code. |
| `txn_id` | `transaction_id` | **REQUIRED** | Unique trace ID. |
| `beneficiary` | `beneficiary_id` | **REQUIRED** | Destination account/VPA. (May be hashed). |
| `device` | `device_id` | RECOMMENDED | Hardware identifier. |
| `session` | `session_id` | RECOMMENDED | Web/App session ID. |
| `ip` | `IP_address` | RECOMMENDED | Network routing IP. |
| `mfa_passed` | `is_strongly_authenticated` | RECOMMENDED | Boolean. |
| `existing_fraud_flag` | `existing_fraud_flag` | OPTIONAL | Boolean. Used for ROI comparison. |
| `existing_block_timestamp`| `existing_block_timestamp`| OPTIONAL | ISO-8601. Used for lead-time comparison. |

## PRIVACY & IDENTIFIERS
FIRST HOUR does not require Personally Identifiable Information (PII) such as Names, SSNs, or Plaintext Emails to detect fraud. 

To build graph structures and behavioral baselines, we only require **stable uniqueness**. You are strongly encouraged to hash (e.g., HMAC-SHA256) fields like `account_id`, `beneficiary_id`, and `device_id` prior to handoff.

## FORMATS
We support secure ingestion via CSV, JSON, or JSONL.
