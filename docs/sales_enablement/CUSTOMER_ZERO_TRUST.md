# FIRST HOUR: TRUST & SECURITY

Customer Zero is designed to prove value with zero operational risk.

## DATA MINIMIZATION & HASHING
FIRST HOUR does not require plaintext PII. Customers are encouraged to provide pseudonymized or hashed identifiers (e.g., HMAC account IDs, hashed IP addresses). We detect fraud via behavioral metadata and graph structure, not raw identity fields.

## SHADOW MODE ONLY
Customer Zero operates exclusively in historical shadow mode. FIRST HOUR is mechanically decoupled from your production environment. It cannot alter credentials, move money, block transactions, or interact with your customers.

## STRICT TENANT ISOLATION
All behavioral baselines, network graphs, and risk policies are strictly partitioned by `tenant_id`. Graph traversals cannot bridge across distinct institutional datasets.

## AI / DETERMINISTIC BOUNDARY
FIRST HOUR uses Generative AI strictly for reading messy telemetry and generating human-readable incident timelines. The core financial policies, thresholds, and blocking recommendations are entirely deterministic, hard-coded ledger math. AI cannot authorize financial action.

## DATA RETENTION & DELETION
Customer Zero supports deletion of ingested historical data after evaluation, subject to the agreed retention configuration.
