# PRIMHORA Verification Scorecard

This scorecard records verification status rather than product claims.

## Current status
- Render backend: LIVE, deployed from the merged main commit.
- Render frontend: LIVE, deployed from the merged main commit.
- Render frontend API origin: configured to the Render backend URL.
- Workspace creation: backend-persisted in the demo environment; browser storage only retains the returned workspace session token.
- OIDC JWT validation code path: present; production activation requires an IdP configuration.
- Tenant-scoped session: implemented and covered by API/DB isolation tests.
- RBAC: implemented and covered by recovery-command tests.
- Evidence hashing/MIME validation: implemented.
- Evidence upload merchant/incident ownership validation: implemented.
- Deterministic evidence verification: implemented.
- Application security headers: implemented.
- Metrics/evaluation access control: implemented.
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
| Durable production evidence storage | NOT YET COMPLETE |
| Distributed rate limiting / abuse controls | NOT YET COMPLETE |
| Production observability and incident runbook | NOT YET COMPLETE |
| Docker Compose execution in CI | PASS |
| GitHub Actions CI | PASS |
| Backend tests in CI | PASS |
| Frontend lint/build in CI | PASS |
| Synthetic precision/recall benchmark | PASS, synthetic-only |
| DB-backed API evaluation | PASS, 60 visible regression cases |
| Broader hidden 50-100+ case evaluation | NOT YET COMPLETE |
| Fresh deployed-browser verification of Phase 5 flows | NOT YET COMPLETE |
| Canonical frontend service selection | NOT YET COMPLETE |

## Production verification

The latest Render deployment from the merged hardening commit completed application startup and received a successful platform health request (HEAD / -> 200). The frontend build completed successfully and Render reported the site live.

Browser-level verification of the complete first-run workflow is still pending because the available web fetch path cannot directly exercise the deployed SPA interactively.

## Interpretation

The current repository has a verified CI path, a live deployed stack and a substantially hardened application boundary, but it should not be represented as fully production-ready for external customer data until identity-provider activation, customer provisioning/operations, durable evidence storage, broader provider coverage, operational controls and deployed-browser verification are completed.
