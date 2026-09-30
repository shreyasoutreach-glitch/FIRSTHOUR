# PRIMHORA Verification Scorecard

This scorecard records verification status rather than product claims.

## Current status
- Render backend: LIVE, deployed from the merged main commit.
- Render frontend: LIVE, deployed from the merged main commit.
- OIDC JWT validation code path: present; production activation requires an IdP configuration.
- Tenant-scoped session: implemented and covered by API/DB isolation tests.
- RBAC: implemented and covered by recovery-command tests.
- Evidence hashing/MIME validation: implemented.
- Deterministic evidence verification: implemented.
- Recovery packet computation: implemented.
- Generic payout CSV ingestion: implemented as a read-only import path.
- PDF evidence-packet export: implemented.
- GitHub Actions CI: passing.
- DB-backed API regression suite: 60 visible labeled cases passing in the latest verified CI run.

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
| Backend tests in CI | PASS, 146 tests |
| Frontend lint/build in CI | PASS |
| Synthetic precision/recall benchmark | PASS, synthetic-only |
| DB-backed API evaluation | PASS, 60 visible regression cases |
| Broader hidden 50-100+ case evaluation | NOT YET COMPLETE |
| Fresh deployed-browser verification of Phase 5 flows | NOT YET COMPLETE |

## Interpretation

The current repository has a verified CI path and live Render deployments, but it should not be represented as fully production-ready for external customer data until identity-provider activation, customer provisioning/operations, broader provider coverage and deployed-browser verification are completed.
