# FIRST HOUR: CUSTOMER ZERO SECURITY OVERVIEW

## SHADOW MODE ENFORCEMENT
During the Customer Zero pilot, FIRST HOUR operates strictly in **Shadow Mode**. The system is mechanically isolated from production ledgers. It cannot move money, freeze real accounts, reverse transactions, or block customers. It exclusively reconstructs historical data and outputs read-only intelligence.

## AI BOUNDARY LIMITATIONS
FIRST HOUR utilizes AI exclusively for complex evidence extraction and incident timeline summarization. 
*   **Deterministic Authority:** AI output cannot directly authorize financial action. Deterministic systems establish financial truth based on hard ledger math.
*   **Prompt Injection Safety:** Messy/malicious data injected into payloads cannot manipulate financial thresholds or risk policies.

## DATA PRIVACY & TENANCY
*   **Tenant Isolation:** Graph traversals, behavioral baselines, and risk scores are strictly partitioned by `tenant_id`. 
*   **Anonymization:** Customers are encouraged to provide pseudonymized or hashed identifiers (e.g., hashed device IDs, hashed account numbers). FIRST HOUR requires uniqueness to build graphs, not raw PII.
*   **Data Destruction:** Following the completion of the Customer Zero replay and report generation, historical payloads can be purged upon request.

## DEPLOYMENT ARCHITECTURE
FIRST HOUR is deployed via GCP Cloud Run (stateless, non-root containers) backed by Cloud SQL PostgreSQL. All inter-service communication requires TLS, and secrets are strictly managed via Secret Manager. No production credentials or customer data exist in the application source code.
