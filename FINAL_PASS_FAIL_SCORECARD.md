# PRIMHORA Verification Scorecard

This scorecard records verification status rather than product claims.

## Current status
- Render backend: LIVE, verified from deployment state and startup logs.
- Render frontend: LIVE, verified from deployment state.
- OIDC JWT validation code path: present; deployment not active.
- Tenant-scoped session: present; fresh execution UNVERIFIED.
- RBAC: present; fresh execution UNVERIFIED.
- Evidence hashing/MIME validation: implemented.
- Deterministic evidence verification: implemented.
- Recovery packet computation: implemented.

## Blockers
| Requirement | Status |
|---|---|
| Customer CSV ingestion | NOT IMPLEMENTED |
| Persistent customer organization/membership | PARTIAL |
| Read-only enforcement for every recovery endpoint | BLOCKED |
| Generic multi-source adapter | PARTIAL |
| PDF packet export | NOT IMPLEMENTED |
| Docker Compose execution | UNVERIFIED |
| GitHub Actions CI | NOT IMPLEMENTED |
| Fresh backend tests | UNVERIFIED |
| Fresh frontend type-check | UNVERIFIED locally |
| Fresh frontend Render build | VERIFIED |
| Precision/recall benchmark | UNVERIFIED |

## Phase 4 pass gate
A requirement is complete only after the command actually runs and output is recorded. Required evidence: backend pytest, frontend type-check/build, Docker health, CI result, CSV fixture, evidence fixture, PDF generation, and an explicit test proving no recovery endpoint can invoke an external money-moving API.

No green checkbox is allowed for an unexecuted test.


## Latest CI verification

Run 36671174979, 2026-09-30: PASS.

Backend tests: PASS.
Frontend TypeScript/build: PASS.
Docker Compose health verification: PASS.
Synthetic evaluation report: PASS.

Synthetic evaluation numbers are recorded in docs/EVALUATION.md and README.md. They are not real-world performance claims.
