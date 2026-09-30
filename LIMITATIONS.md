# LIMITATIONS

This document records what is deliberately not claimed as production-ready.

## Authentication
There is no active customer identity provider in the checked-in environment. In demo mode, users are seeded and authenticated with demo tokens. Production mode validates OIDC/JWT tokens but requires a configured provider domain/audience and pre-provisioned tenant membership.

## Multi-tenancy
Tenant scoping is structural and covered by API and DB isolation tests. Raw SQL and future SQLAlchemy relationship loading remain review-sensitive surfaces. Demo reset/injection operations are demo-only.

## Recovery commands
Recovery commands are simulations and evidence/packet preparation only. There is no external payment processor, bank, or UPI execution integration. Authoritative payout rows are never mutated by the recovery command path.

## Evidence extraction
Text extraction is deterministic in the current no-key path. Gemini multimodal extraction is available behind an explicit credential and its output remains candidate evidence until deterministic verification.

## Integrations
Generic payout CSV ingestion is implemented and read-only. RazorpayX live sync remains credential-dependent. Additional bank, ERP, ledger and payment-provider adapters are not yet implemented.

## Operational readiness
CI verifies backend tests, frontend lint/build, Docker Compose health and the synthetic evaluation. Production observability, rate limiting, secrets rotation, incident response, backup/restore drills, API versioning and deployment runbooks remain to be completed before handling sensitive customer financial data.

## Evaluation
The current 300-case fixture benchmark is synthetic and intentionally separable. A larger 50-100+ DB-backed API-path suite covering normal, anomalous, malformed, conflicting, replayed and cross-tenant cases is still required.

## Not yet claimed
PRIMHORA does not claim live bank connectivity, autonomous fraud decisions, recovered funds, customer savings, fraud-detection accuracy in the wild, or product-market fit.