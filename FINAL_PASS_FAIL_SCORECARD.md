# PRIMHORA Verification Scorecard

This scorecard records verification status rather than product claims.

## Current status
- Render backend: LIVE, verified from deployment state and startup logs.
- Render frontend: LIVE, verified from deployment state.
- OIDC JWT validation code path: present; production activation requires an IdP configuration.
- Tenant-scoped session: implemented and covered by API/DB isolation tests.
- RBAC: implemented and covered by recovery-command tests.
- Evidence hashing/MIME validation: implemented.
- Deterministic evidence verification: implemented.
- Recovery packet computation: implemented.
- Generic payout CSV ingestion: implemented as a read-only import path.
- PDF evidence-packet export: implemented.
- GitHub Actions CI: passing on the current rebuild branch.

## Remaining gates
| Requirement | Status |
|---|---|
| Customer payout CSV ingestion | IMPLEMENTED |
| Persistent customer organization/membership | PARTIAL |
| Production identity-provider activation | CREDENTIAL-DEPENDENT |
| Read-only financial execution boundary | IMPLEMENTED, TESTED |
| Generic multi-source adapter | PARTIAL |
| PDF packet export | IMPLEMENTED |
| Docker Compose execution in CI | PASS |
| GitHub Actions CI | PASS |
| Backend tests in CI | PASS |
| Frontend lint/build in CI | PASS |
| Synthetic precision/recall benchmark | PASS, synthetic-only |
| DB-backed API evaluation, 50-100 cases | NOT YET COMPLETE |
| Fresh deployed-browser verification of Phase 5 flows | NOT YET COMPLETE |
