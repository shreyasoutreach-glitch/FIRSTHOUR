# FILE_CHANGE_MANIFEST — Enterprise Upgrade Pass

Scope: the enterprise-readiness upgrade following AUDIT.md's P0 findings —
multi-tenancy, RBAC, and the Recovery Command state machine with
convergence checking. No UI redesign, no unrelated refactors.

## New

- `AUDIT.md` — full repository audit (A-J categories, P0-P3 ranked findings)
  produced before any code changed, per the brief's own sequencing.
- `LIMITATIONS.md` — the honest, single-source list of what's real vs.
  simulated vs. not-built, referenced from code comments throughout.
- `backend/app/core/tenancy.py` — `TenantScopedSession`, a `Session`
  subclass overriding `get()`/`query()`/`add()` for structural tenant
  isolation. Chosen after empirically verifying that `with_loader_criteria`
  (the more "standard" SQLAlchemy multi-tenancy pattern) does not reliably
  cover `Session.get()` — see the throwaway verification scripts in the
  conversation history.
- `backend/app/core/authz.py` — RBAC: 5 roles, 5 permissions, bearer-token
  auth, `get_tenant_db`/`get_system_db` dependencies.
- `backend/app/services/recovery/command.py` — Recovery Command state
  machine (PROPOSED→REVIEWED→APPROVED→EXECUTED→VERIFIED, or →REJECTED),
  idempotent proposal, shared dry-run/execute simulation, simulated-only
  execution.
- `backend/app/services/recovery/convergence.py` — deterministic
  convergence checking (no duplicate commands, complete audit trail,
  re-simulation matches recorded execution, amount agreement). Explicitly
  scoped to what this system can honestly check (see LIMITATIONS.md) rather
  than faking cross-system checks against ledgers/settlements that don't
  exist in this build.
- `backend/app/api/routes_recovery.py` — Recovery Command API surface
  (propose/list/get/dry-run/review/approve/reject/execute/verify/convergence).
- `backend/tests/test_tenant_isolation.py` — 11 tests proving Tenant A
  cannot reach Tenant B's incidents, evidence, graph, exposure, recovery
  packets, audit logs, payments, financial events, or recovery commands.
- `backend/tests/test_rbac_permissions.py` — 8 tests on the permission
  matrix itself, including the brief's named property (Investigator can
  never approve or execute).
- `backend/tests/test_recovery_command.py` — 12 tests: full lifecycle,
  illegal state skips, idempotent propose/execute, proposer-cannot-
  approve-own-command, dry-run/execute never touching the real Payout row.
- `backend/tests/test_convergence.py` — 6 tests including two that
  deliberately break convergence (mutate the target after execution;
  introduce a duplicate command) to prove the check can actually fail, not
  just pass by construction.
- `frontend/src/pages/RecoveryCommand.tsx` — rebuilt around the real
  Recovery Command API (was previously a static "official next steps"
  list). Includes a role switcher using the 4 non-admin seeded demo tokens
  so the screen can demonstrate genuine RBAC rejection, not just success
  paths.

## Changed

- `backend/app/models/entities.py` — added `Tenant`, `TenantScoped` mixin
  (applied to every existing table except `Tenant` itself), `User`,
  `RecoveryCommand`; extended `Incident` with enterprise fields (severity,
  financial_exposure, recoverable/unrecoverable_amount, confidence,
  resolution_state) and `AuditEvent` with actor_user_id/before_state/
  after_state.
- `backend/app/core/database.py` — `SessionLocal` now constructs
  `TenantScopedSession` instances; `get_db()` re-documented as the
  unscoped, overridable base dependency everything else composes on.
- `backend/app/services/incident/detector.py` —
  `sync_financial_events_for_payouts` now explicitly propagates
  `tenant_id` from each source payout, rather than relying on session-wide
  tenant context, because it's called with batches spanning multiple
  tenants (the seed script's cross-tenant canonicalization pass).
- `backend/app/demo/chaos_lab.py` — `inject_scenario` now resolves the
  target merchant's tenant first (unscoped lookup) and sets the session's
  tenant before creating any rows.
- `backend/app/audit/logger.py` — `log()` accepts `actor_user_id`,
  `before_state`, `after_state`.
- `backend/seed/seed.py` — restructured around two tenants
  (`TEN_NORTHBRIDGE`: Arrow Industries + Harbor & Co + half the background
  merchants; `TEN_MERIDIAN`: the other half, isolation-test fodder only),
  seeds 5 users per tenant with deterministic bearer tokens, prints tokens
  on CLI run. Fixed a real bug caught during this pass: the initial
  restructuring only synced Arrow Industries' own payouts into
  `financial_events`, silently dropping ~4,700 events for Harbor and the
  background merchants — caught by comparing payout count to
  financial-event count after seeding, not by inspection.
- `backend/app/api/routes_incident.py`, `routes_evidence.py`,
  `routes_merchant.py`, `routes_metrics.py`, `routes_demo.py` — every route
  now depends on `get_tenant_db` or `get_system_db` instead of the old
  unscoped `get_db`; mutating routes additionally require the appropriate
  permission (`INVESTIGATE` for evidence upload/attestation, `EXECUTE`
  admin-only for demo reset/inject).
- `backend/app/schemas/schemas.py` — `DemoResetResponse` now returns
  seeded tenant IDs and demo tokens; added Recovery Command request/
  response schemas.
- `backend/tests/conftest.py`, `test_api_integration.py`,
  `test_evidence_upload_security_api.py` — updated for tenant-scoped
  sessions and bearer-token auth; added explicit tests proving
  unauthenticated/invalid-token requests get 401 and insufficient-
  permission requests get 403 (these didn't exist before RBAC did).
- `frontend/src/lib/api.ts` — added per-role `DEMO_TOKENS` and a
  `requestAs()` variant; added Recovery Command API functions. (One
  self-inflicted hiccup during this: an interrupted edit left `request()`
  without its function signature, breaking the file's syntax — caught
  immediately by `tsc --noEmit`, fixed by rewriting the file cleanly rather
  than patching around it.)

## Explicitly not touched in this pass

Every deterministic algorithm from the prior pass (financial baseline,
Incident Evidence Score, entity resolution, temporal reasoning, evidence
extraction/verification, blast-radius traversal, evidence upload path-
traversal fix) — none of it needed to change for multi-tenancy/RBAC/
Recovery Command to work, and none of it was refactored "while in there."
