# LIMITATIONS

This document records what is deliberately not claimed as production-ready.

## Authentication
There is no active customer identity provider in the checked-in environment. In demo mode, users are seeded and authenticated with demo tokens. Production mode validates OIDC/JWT tokens but requires a configured provider domain/audience and pre-provisioned tenant membership.

## Multi-tenancy
Tenant scoping is structural and covered by API and DB isolation tests. The current user model carries one tenant assignment; durable production organization membership/invitation lifecycle is still required. Raw SQL and future SQLAlchemy relationship loading remain review-sensitive surfaces. Demo reset/injection operations are demo-only.

## Workspace provisioning
The first-run workspace flow now persists a Tenant and an administrator User in demo mode and stores the returned workspace token in browser session state. This is not production identity provisioning. Production self-service organization creation remains blocked until the real IdP and membership model are activated.

## Recovery commands
Recovery commands are simulations and evidence/packet preparation only. There is no external payment processor, bank, or UPI execution integration. Authoritative payout rows are never mutated by the recovery command path.

## Evidence extraction
Text extraction is deterministic in the current no-key path. Gemini multimodal extraction is available behind an explicit credential and its output remains candidate evidence until deterministic verification.

## Evidence storage
Uploaded evidence currently lives on the application filesystem. A production deployment needs durable object storage or a verified persistent disk plus retention, backup and restore procedures.

## Integrations
Generic payout CSV ingestion is implemented and read-only. RazorpayX live sync remains credential-dependent. Additional bank, ERP, ledger and payment-provider adapters are not yet implemented.

## Operational readiness
Application-level security headers, protected metrics/evaluation endpoints, and evidence ownership checks are implemented. Production observability, distributed rate limiting, secrets rotation, incident response, backup/restore drills, API versioning, deployment runbooks and durable evidence storage remain to be completed before handling sensitive customer financial data.

## Evaluation
The current 300-case fixture benchmark is synthetic and intentionally separable. A visible 60-case DB-backed API regression suite now covers clean/suspicious CSV imports, malformed input and replay behavior. A larger hidden 50-100+ case suite covering normal, anomalous, malformed, conflicting, replayed and cross-tenant cases is still required.

## Not yet claimed
PRIMHORA does not claim live bank connectivity, autonomous fraud decisions, recovered funds, customer savings, fraud-detection accuracy in the wild, durable customer-data storage, or product-market fit.
