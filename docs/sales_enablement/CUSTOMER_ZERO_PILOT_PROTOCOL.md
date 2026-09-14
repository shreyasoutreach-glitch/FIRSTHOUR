# FIRST HOUR: CUSTOMER ZERO PILOT PROTOCOL

This document defines the formal workflow for executing a Shadow-Mode Customer Zero evaluation.

## 1. DATA INGESTION
The customer securely transfers historical event data via CSV, JSON, or JSONL.

## 2. SCHEMA DISCOVERY & MAPPING
The FIRST HOUR `CustomerDataAdapter` is configured to map customer-specific nomenclature into the 39 canonical RiskEvent schemas (e.g., mapping `wire_out` to `TRANSFER_COMPLETED`).

## 3. DATA QUALITY GATE
Before replay, the system generates a Data Quality Report grading the integrity of the payload (Green/Yellow/Red). Missing fields (e.g., device telemetry, exact timestamps) are explicitly flagged as limiting factors. The system gracefully continues but notes the degraded capability.

## 4. POINT-IN-TIME REPLAY
The dataset is replayed strictly chronologically. The system reconstructs `AccountTrustState`, calculates temporal velocity, and builds the network graph dynamically. **No future-data leakage is permitted.**

## 5. INCIDENT RECONSTRUCTION
As anomalies trigger, FIRST HOUR reconstructs the incident timeline, capturing the exact moment of First Divergence (Identity, Behavior, Graph, or Sequence).

## 6. EXISTING-CONTROL COMPARISON
If the dataset includes existing customer labels (`existing_fraud_flag`, `existing_block_timestamp`), FIRST HOUR calculates the Incremental Lead Time: how much earlier FIRST HOUR flagged the divergence compared to the legacy control.

## 7. FINANCIAL EXPOSURE CALCULATION
The system calculates Gross Fraud Exposure, Potential Prevented Exposure (capital that would have been saved), and the Operational Friction Cost (false positive review overhead).

## 8. EXECUTIVE REPORT DELIVERY
A formalized report detailing the exact economic findings, timelines, and network exposure maps is generated and presented to the customer.
