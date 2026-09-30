# PRIMHORA Honest Audit

Audit date: 2026-09-30
Working branch: primhora-production-rebuild
Working branch: primhora-production-rebuild

## Executive status

Primhora is a working synthetic financial-investigation product, not yet a production customer-data product.

Render backend and frontend are live. The repository contains deterministic incident/reconstruction logic, tenant-scoped sessions, OIDC JWT validation code, RBAC, evidence providers, recovery-command state transitions, convergence checking, audit logging, and a RazorpayX adapter.

The biggest remaining product gap is the boundary between customer-owned data and synthetic/demo data. Generic customer CSV ingestion, persistent customer organizations/membership, production identity provisioning, and production-grade data-source onboarding remain incomplete.

## Verification ledger

| Check | Evidence | Result |
|---|---|---|
| Backend deployment | Render deploy dep-datvq80u01pc73frsi8g | VERIFIED: LIVE |
| Frontend deployment | Render deploy dep-datvq88u01pc73frsig0 | VERIFIED: LIVE |
| Backend startup | Render logs: alembic upgrade, Application startup complete, Uvicorn running, Your service is live | VERIFIED |
| Backend root | Render logs show GET / 200 | VERIFIED |
| Local HTTP smoke test | urllib request to Render URL | UNVERIFIED: audit container DNS cannot resolve external host |
| Local clone/build | attempted during engineering pass | UNVERIFIED: container DNS cannot resolve github.com |
| Backend pytest | CI run 36677872645 | VERIFIED: PASS |
| Frontend tsc/build | Render build succeeded; local execution unavailable | UNVERIFIED locally; Render build VERIFIED |
| Docker Compose | CI run 36677872645 | VERIFIED: PASS |
| GitHub Actions | CI run 36677872645 | VERIFIED: PASS |

No test result is described as passing unless it was actually executed.

## Feature / screen audit

| Area | Status | Evidence |
|---|---|---|
| Landing / Welcome | FUNCTIONAL | Demo/workspace split and synthetic-data disclosure |
| Demo setup | FUNCTIONAL | Synthetic setup and routing |
| Demo connect | FUNCTIONAL / SYNTHETIC | Explicitly no live provider |
| Incident detail | FUNCTIONAL | Backend incident endpoint |
| Timeline | FUNCTIONAL | Deterministic chronological spine |
| Evidence upload | FUNCTIONAL | Upload, hashing, MIME/security handling |
| Text evidence extraction | FUNCTIONAL / LIMITED | Gemini provider plus deterministic fallback |
| Image/PDF extraction | FUNCTIONAL WHEN GEMINI CONFIGURED | Multimodal Gemini provider |
| Evidence verification | FUNCTIONAL | VERIFIED / CONFLICTING / UNVERIFIED states |
| Reconstruction | FUNCTIONAL | Financial events + communications + evidence |
| Entity graph | FUNCTIONAL | Graph builder/endpoint |
| Exposure | FUNCTIONAL | Deterministic exposure computation |
| Human witness | FUNCTIONAL | Prioritized questions + attestations |
| Recovery packet | FUNCTIONAL | Computed packet data |
| Recovery proposal/review/approval/reject | FUNCTIONAL CODE PATH | Structured RecoveryCommand endpoints exist |
| Recovery dry-run | FUNCTIONAL CODE PATH | Endpoint/service exist |
| Recovery execution | BLOCKED BY DESIGN | Endpoint returns 409 and does not call a provider |
| Recovery verification/convergence | PARTIAL | Exists but requires read-only semantic hardening and benchmark verification |
| Audit log | FUNCTIONAL CODE PATH | Audit service and endpoint |
| Workspace overview | PARTIAL | UI exists, organization is browser-session state |
| Workspace incidents | PARTIAL | Correctly empty; no customer ingestion |
| Workspace data sources | PARTIAL | CSV inspection only, not ingestion |
| Workspace team | PARTIAL | Invitation draft only |
| Production OIDC | CODE PATH FUNCTIONAL / DEPLOYMENT UNCONFIGURED | JWT/JWKS validation exists; deployment remains DEMO_MODE |
| Tenant isolation | CODE PATH FUNCTIONAL / TEST UNVERIFIED | TenantScopedSession exists |
| RBAC | CODE PATH FUNCTIONAL / TEST UNVERIFIED | Roles/permissions exist |
| RazorpayX | FUNCTIONAL ADAPTER / NOT CONNECTED | Adapter exists; credentials absent |
| Generic CSV ingestion | FUNCTIONAL CODE PATH | Authenticated generic payout CSV normalizer/import |
| Multi-source ingestion | PARTIAL | RazorpayX adapter only |
| PDF export | FUNCTIONAL CODE PATH / TESTING | ReportLab service + endpoint + UI; dedicated test added |
| Docker Compose | PRESENT / UNVERIFIED | Not executed with a Docker daemon |
| CI | FUNCTIONAL | GitHub Actions backend/frontend/Docker lanes |
| Evaluation harness | PRESENT / UNVERIFIED | Tests/benchmarks exist; fresh run unavailable |
| Production monitoring | ABSENT | No recurring customer-source monitoring |

## Backend endpoint audit

Incident/investigation routes exist for incident list/detail, timeline, graph, exposure, evidence, next human question, attestation, recovery packet and audit.

Recovery routes exist for proposal, listing, retrieval, dry-run, review, approval, rejection, execution, verification and convergence.

Merchant/data-source routes exist for connection status, Razorpay sync and deterministic baseline.

Demo routes exist and are DEMO_MODE-gated.

## Where the old demo cheats

1. Synthetic financial data remains the demo incident source.
2. Demo bank/account details are fictional and never connect to a bank.
3. Razorpay is not a live collaborator/integration. The adapter exists, credentials are absent.
4. Workspace organization creation is browser/session state, not persistent customer tenancy.
5. Workspace CSV selection is inspection, not ingestion.
6. Team invitations are drafts, not actual invitations.
7. Seeded demo incidents must never appear in the real workspace.
8. Deterministic evidence extraction is not an LLM.
9. Recovery execution currently contains a provider execution path. This violates the new read-only contract and is a Phase 4 blocker.
10. PDF export is not implemented/verified.
11. Docker Compose has not been executed with Docker during this audit.
12. No GitHub Actions CI workflow exists.
13. Production OIDC code exists, but the deployed environment remains DEMO_MODE.
14. No fresh local test run was possible in the current tool environment. This is a limitation, not a passing result.

## Deterministic-truth rule audit

The architecture separates deterministic financial truth from evidence interpretation and human context.

Model extraction can produce candidate amount/beneficiary claims, but these are untrusted evidence claims and must never become financial truth without deterministic verification against source records.

Phase 4 must enforce this boundary in schemas, provenance, tests and UI wording.

## Remaining blockers

1. Make organization/membership persistence and production identity real.
2. Complete dedicated HTTP-level customer CSV import tests.
3. Complete stronger tenant/resource ownership tests.
4. Expand executable precision/recall evaluation to customer-import scenarios.
5. Keep broader provider integrations adapter-only until credentials/authorization exist.


## Phase 4-6 verification update

GitHub Actions run 36677872645 on 2026-09-30 completed successfully.

- Backend: pytest passed.
- Frontend: npm ci, TypeScript lint, and production build passed.
- Docker: compose build/start/healthcheck/teardown passed.
- Synthetic evaluation step passed and emitted metrics.
- Code search for "buildathon", "hackathon", and "judge" returned zero indexed matches at audit time.

Synthetic evaluation result:
- event detection precision 1.000, recall 1.000, F1 1.000 on 200 clean + 100 suspicious synthetic cases;
- entity-link precision 1.000, recall 1.000, F1 1.000 on 6 labeled entity cases;
- entity exact-decision accuracy 0.833 on 6 cases;
- timeline ordering accuracy 1.000 on the fixture;
- replay consistency 1.000 across five repeated runs.

These are fixture metrics, not production accuracy.
