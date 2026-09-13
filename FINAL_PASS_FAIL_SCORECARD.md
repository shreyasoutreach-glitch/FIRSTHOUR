# FINAL_PASS_FAIL_SCORECARD — Enterprise Upgrade Pass

Every line reflects a command actually run in this session. Raw output
quoted where useful. This supersedes the prior scorecard's numbers (which
covered only the earlier security-fix pass); prior results are still
accurate for what they tested, just smaller in scope than this one.

## Backend tests

```
$ .venv/bin/python -m pytest -q
...............................................................................
..... [ 60%]
...............................................                          [100%]
119 passed in 44.97s
```

Breakdown: 82 from the prior passes (algorithms, evidence pipeline, state
machine, human questions, exposure/graph, API integration, path-traversal
security) + 11 tenant isolation + 8 RBAC permission matrix + 12 recovery
command lifecycle + 6 convergence checking.

**BACKEND TESTS: 119/119 PASS**

## Frontend

```
$ npx tsc --noEmit    -> exit 0, no output
$ npm run build
✓ 1878 modules transformed.
dist/assets/index-DrHNW5Fx.js   335.16 kB
✓ built in 5.62s
```

**TSC: PASS** &nbsp;&nbsp; **FRONTEND BUILD: PASS**

## Live HTTP verification (real seeded database, real running uvicorn)

| Check | Result |
|---|---|
| Unauthenticated request to a tenant-scoped route | 401, as expected |
| Full Recovery Command lifecycle against the real Arrow Industries incident (₹1Cr payout): propose (Investigator) → blocked approve-without-review (403, wrong permission... actually correctly a permission check) → blocked execute-before-approval (409, wrong state) → review → blocked self-approval → approve (real Approver) → execute (real Administrator) → verify → convergence | **PASS**, every step's status code matched what the state machine and RBAC matrix predict |
| Frontend's actual bundled demo tokens (Investigator/Approver/Administrator) against a freshly reseeded server | **PASS** — proposed a real command via the exact token the built frontend ships with |
| Tenant isolation via HTTP: Tenant A's token against Tenant B's incident ID | 404, not data, not a 403-that-confirms-existence |

## Two real bugs caught by testing during this pass (not by inspection)

1. **Tenant sync gap**: the initial tenant-restructuring of `seed.py` only
   synced Arrow Industries' own payouts into `financial_events`, silently
   dropping ~4,700 events for Harbor & Co and the 29 background merchants
   in the same tenant. Caught by comparing `Payouts` count to
   `FinancialEvents` count after seeding — they should always be equal and
   weren't.
2. **Silent JSON query failure**: `AuditEvent.sources.contains([id])` was
   used to look up a recovery command's audit trail for convergence
   checking. Verified empirically against SQLite before trusting it, and
   found it returns **zero rows even for a genuine match** — no error, no
   warning, just silently wrong. Replaced with a filter on the indexed
   `incident_id` column plus a Python-side membership check. This is
   exactly the kind of bug that would have shipped a convergence check
   that always looked broken (permanently reporting missing audit trail)
   without ever raising an exception to reveal why.

## Docker

Unchanged from the prior pass: `docker-compose.yml` is YAML-valid and
internally consistent with the app's config, but **actual `docker compose
up` execution has still not been tested** — no Docker daemon in this build
environment (`docker: not found`).

## Scorecard summary

```
BACKEND TESTS: 119/119
FRONTEND BUILD: PASS
TSC: PASS
LIVE RECOVERY COMMAND LIFECYCLE (real HTTP, real seeded incident): PASS
TENANT ISOLATION (API + DB level): PASS
RBAC ENFORCEMENT (live + unit): PASS
CONVERGENCE CHECK (both CONVERGED and STILL_DIVERGENT paths proven): PASS
DOCKER RUNTIME: NOT TESTED - daemon unavailable
```
