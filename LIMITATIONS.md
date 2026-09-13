# LIMITATIONS

Referenced from several places in the code (`app/core/authz.py`,
`frontend/src/lib/api.ts`, `AUDIT.md`) — this is the one place that collects
every "not real yet" honestly, in one list, so nobody has to piece it
together from comments scattered across the codebase.

## Authentication

There is no real identity provider. `users.api_token` is a plain string
compared with `==` — no hashing, no expiry, no revocation, no MFA, no rate
limiting on login attempts. The five seeded demo tokens (one per role, per
tenant) are deterministic from `SEED` and printed by `python -m seed.seed`
or returned by `POST /demo/reset`. **Do not point this at real user
credentials or reuse this auth code path against real data.** A production
deployment replaces this entirely with the customer's own IdP (Okta, Azure
AD, etc.) — the role/tenant assignment shape (`User.role`, `User.tenant_id`)
is what should survive that swap, not the token mechanism itself.

There is also no frontend login screen. `frontend/src/lib/api.ts` hardcodes
the deterministic Administrator token for `SEED=42` so the existing screens
keep working without one. The Recovery Command screen additionally exposes
a role switcher using the other four seeded demo tokens, specifically so it
can demonstrate real RBAC enforcement (an Investigator token genuinely
cannot approve) without needing a login flow.

## Multi-tenancy

Enforcement is structural (`TenantScopedSession` overriding `.get()`/
`.query()`/`.add()`) and is tested — see `tests/test_tenant_isolation.py`.
What it does **not** cover, and would need to before a real multi-tenant
production deployment:

- Raw SQL (`session.execute(text(...))`) is not intercepted. Nothing in
  this codebase currently does that, but nothing stops a future
  contributor from adding it and silently bypassing tenant scoping. A real
  deployment should add a lint rule or code-review checklist item for this.
- SQLAlchemy `relationship()`-based lazy loading is not intercepted. This
  codebase declares zero `relationship()` attributes (everything is
  explicit FK columns + manual queries), so this has zero surface area
  today — it would need the same treatment if relationships were added.
- Admin/system operations (`/demo/reset`, `/demo/inject-incident`) are
  intentionally cross-tenant and gated by role (Administrator) rather than
  tenant scoping. That's the right boundary for what they do, but it means
  an Administrator in any tenant can currently wipe *every* tenant's data
  via `/demo/reset` — acceptable for a demo/pilot environment, not for a
  real multi-customer production deployment, which would need
  platform-level admin separated from tenant-level admin.

## Recovery Command execution

**Execution is always simulated.** There is no real payment-processor,
bank, or UPI network integration anywhere in this codebase. When a command
reaches `EXECUTED`, `execution_mode` is unconditionally `"SIMULATED"` and
the authoritative `Payout` row is never modified — verified directly by
`test_recovery_command.py::test_execute_never_writes_to_the_real_payout_table`.
Before this could execute anything real, it would need an actual
integration with a payment processor's freeze/reversal API, and a much more
serious conversation about liability, reversibility guarantees, and
regulatory requirements than this build attempts to have.

## Convergence checking

The convergence check (`services/recovery/convergence.py`) verifies internal
consistency of this system's own records (no duplicate commands, complete
audit trail, re-simulation matches recorded execution, amounts agree). It
does **not** check agreement with an external ledger, settlement system, or
bank record, because this build has no such external system connected. The
brief's own example (gateway CAPTURED / order PAID / settlement RECEIVED /
ledger POSTED) describes cross-system checks this build cannot honestly
claim to perform yet.

## Evidence extraction

Claim extraction (`services/evidence/pipeline.py`) is a deterministic
regex-based extractor, not an LLM call, even though `ANTHROPIC_API_KEY` is
wired into `.env.example` as the seam for one. Image and PDF evidence
uploads are accepted and hashed but not processed — `POST
/evidence/analyze` returns a `409` with an honest explanation rather than
pretending to have run OCR/vision extraction on them.

## AI architecture

There is no `AIProvider` abstraction (`DemoProvider` / `RealLLMProvider`)
yet. The regex extractor is called directly. This means the "AI can fail
without financial truth being affected" property is true today only because
there is no live model call to fail in the first place — it hasn't been
demonstrated under an actual provider failure/timeout/retry scenario.

## Not built at all (stated plainly, not implied to exist)

- First-divergence as its own named, separately computed concept (the
  Incident Evidence Score and convergence checks are related but are not
  the same computation the brief describes).
- Counterfactual "what if we reverse/freeze this" simulation as a
  standalone exploratory tool — the Recovery Command dry-run computes this
  for one specific proposed action, not as an open-ended "try any
  hypothetical" interface.
- Observability: no structured logging, request IDs, latency tracking, or
  an internal health page beyond `/health` and `/metrics`.
- API versioning — every route is unprefixed (`/incident/...`, not
  `/v1/incident/...`).
- Rate limiting, request size limits on uploads, and CORS origin validation
  beyond a plain string match.
- SECURITY.md, THREAT_MODEL.md, API.md, DEPLOYMENT.md,
  ENTERPRISE_READINESS.md, COMMERCIAL.md, and BUYER_BRIEF.md have not been
  written yet.
- Docker Compose has been written and YAML/consistency-validated but never
  actually executed (`docker: not found` in the build environment) — see
  `FINAL_PASS_FAIL_SCORECARD.md`.

## What IS real (so this document isn't only a list of gaps)

Deterministic financial scoring, entity resolution, evidence
cross-verification, bounded blast-radius graph traversal, the full
Recovery Command state machine with genuine separation of duties, replay-
consistent convergence checking that can and does detect real divergence,
and structural (not conventional) tenant isolation — all backed by 119
passing tests, several of which exist specifically because they caught real
bugs during this build (see `FILE_CHANGE_MANIFEST.md` and the conversation
history for specifics). That is a meaningfully different, and considerably
more defensible, claim than "we built a demo."
