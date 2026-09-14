# FIRST HOUR: DATA REQUIREMENTS

To perform a valid Customer Zero point-in-time replay, FIRST HOUR requires a chronological ledger of events. 

## MINIMUM REQUIRED FIELDS
These fields are strictly necessary to calculate financial exposure and construct behavioral baselines.
*   `account_id`: Unique identifier for the transacting entity.
*   `event_time`: ISO-8601 timestamp (must include accurate timezone offsets).
*   `event_type`: The nature of the event (login, transfer, password reset).
*   `transaction_id`: Unique trace ID for the event.
*   `amount`: Numeric financial value (0.0 for non-financial events).
*   `currency`: 3-letter currency code (e.g., USD, EUR).
*   `beneficiary_id` / `VPA`: The destination account/routing identifier.

## HIGHLY RECOMMENDED TELEMETRY
Absence of these fields degrades detection accuracy (particularly for Account Takeovers) and increases the False Positive rate.
*   `device_id` or `device_hash`: Hardware identifier used for the session.
*   `IP_address` or `network_identifier`.
*   `session_id`: Correlates pre-auth events with post-auth financial actions.
*   `is_strongly_authenticated` (Boolean): Indicates if multi-factor authentication was explicitly verified for the event.

## EXISTING CONTROL LABELS (FOR ROI COMPARISON)
To prove incremental value, we request historical outcomes:
*   `existing_fraud_flag`: Boolean (was this event ultimately classified as fraud?)
*   `existing_block_timestamp`: When did your current systems stop the actor?
*   `chargeback_received`: Boolean.

*Note: Missing telemetry will be documented in the Data Quality Gate. FIRST HOUR will not silently infer missing data.*
