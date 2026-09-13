# AUDIT.md — FIRST HOUR, as it exists today

Scope: full repository inspection (backend, frontend, data model, tests, docker,
docs). No code changed to produce this document. Every claim below was verified
against the actual repo in this pass (grepped, not assumed) — see the verification
commands referenced inline.

---

## A. What already works (real, verified, end-to-end)

- **Deterministic incident scoring** — median/MAD robust z-score, rolling velocity,
  dormancy, historical novelty, communication correlation, combined into a
  weighted Incident Evidence Score (`services/incident/scoring.py`). No
  `is_fraud = true` anywhere (`grep -r is_fraud backend/` → zero matches).
- **Entity resolution** with strong-identifier-first decision bands; name
  similarity alone cannot reach `AUTO_LINK`.
- **Evidence pipeline**: SHA-256 hashing, MIME allow-listing, regex-based claim
  extraction, cross-verification against `financial_events` (`VERIFIED` /
  `CONFLICTING` / `UNVERIFIED`).
- **Bounded blast-radius graph traversal** that matches on shared VPA/bank
  account value, not row ID (catches the "same account, different display
  name" mule pattern).
- **Human witness question prioritization** (impact × uncertainty ×
  actionability), one question at a time, answers stored as immutable
  `human_attestations` that never overwrite a financial row.
- **State machine** (`INGESTING → ... → ESCALATED`, with `CONFLICTING_EVIDENCE`
  as a legitimate first-class state).
- **Audit log** — every service writes an `AuditEvent` row.
- **Chaos Lab** — 4 scenarios that write real rows and re-run the real
  detector; verified live via HTTP in the prior session.
- **78 backend tests passing**, including path-traversal regression tests
  added in the last pass; **frontend `tsc --noEmit` and `npm run build`
  both clean**.
- **File-upload path traversal is fixed** — `safe_filename()` +
  `is_path_contained()` with a resolved-path containment check, tested
  against Unix and Windows-style traversal strings.

## B. What is genuinely production-*like* (real architecture, not yet real scale)

- The data model is Razorpay-shaped (Payments/Payouts/Contacts/FundAccounts,
  not one generic "transaction" table) and uses portable SQLAlchemy types —
  Postgres works today via `DATABASE_URL`, no code change required.
- The service-layer boundary between deterministic code and the one place
  free text is interpreted (`evidence/pipeline.py`) is real and enforced by
  code structure, not just convention.
- `docker-compose.yml` is written and YAML/consistency-validated but **has
  never actually been run** (no Docker daemon in the build environment) —
  this is stated plainly in the existing docs and repeated here.

## C. What is demo-only (verified by grep + reading, not assumed)

- **No authentication of any kind.** Every API endpoint is open. Confirmed:
  zero hits for `oauth|jwt|auth0` in `backend/app`.
- **No multi-tenancy.** `merchant_id` exists as a foreign key, but there is
  no `tenant_id`, no request-scoped tenant context, and nothing prevents one
  caller from reading any other merchant's incidents, evidence, or audit log
  by ID. Confirmed: zero hits for `tenant` anywhere in `backend/app`.
- **No RBAC.** There is exactly one implicit role (unauthenticated caller =
  full access to everything). Confirmed: zero hits for `role|rbac|permission`
  outside of unrelated fields (`Employee.role`, `IncidentEvent.role`, which are
  data labels, not authorization).
- **No recovery execution.** `services/recovery/packet.py` only *assembles a
  document*. There is no recovery command object, no approval state machine,
  no dry-run, no execute step, no idempotency key anywhere in the codebase.
  Confirmed: zero hits for `approv|execute_recovery|dry_run|idempoten`.
- **No convergence proof or "first divergence" concept.** Confirmed: zero
  hits for `converg|divergence`. The Incident Evidence Score is *not* the
  same computation as either of these — it measures anomalousness of a
  payout, not "where did expected vs. observed ledger state first split."
- **Evidence extraction is regex, not an LLM call.** This is disclosed
  honestly in the existing docs, not hidden — but it means "AI interprets
  evidence" is currently a placeholder architecture, not a working AI layer
  with failure handling, retries, or a provider abstraction.
- **The synthetic universe is scaled down** (60 merchants / ~9,200 payouts
  vs. the original spec's 500 / 50,000+) — disclosed in `ARCHITECTURE.md`.
- **The financial graph is a payout-centric subgraph**, not a general ledger
  reconciliation graph — it does not currently model orders/settlements as
  graph nodes for a given incident, only merchant/payout/contact/fund-account/
  communication/evidence.

## D. Security vulnerabilities

| # | Finding | Severity |
|---|---|---|
| D1 | No authentication on any endpoint | **P0** |
| D2 | No tenant isolation — any caller can read/mutate any merchant's data by guessing/enumerating IDs (IDOR by design, not by bug) | **P0** |
| D3 | `/demo/reset` and `/demo/inject-incident` are unauthenticated and destructive (wipe + reseed the entire DB) — fine for a sandboxed demo, a real incident if ever exposed without `DEMO_MODE` gating in front of a real deployment | **P0 if ever deployed without additional gating; currently mitigated by `DEMO_MODE` flag, not by auth** |
| D4 | CORS origin list defaults to a single dev origin but is fully attacker-controllable via env var with no validation of scheme/wildcard misuse if misconfigured | **P2** |
| D5 | No request size limit on `/evidence/upload` — a large file can be uploaded with no cap, only a MIME check | **P1** |
| D6 | No rate limiting anywhere | **P1** |
| D7 | Evidence file path traversal — **fixed in the prior pass**, regression-tested | **Resolved** |
| D8 | SQL injection — not found; all queries go through SQLAlchemy's ORM/parameterized query builder, no raw string-interpolated SQL anywhere (`grep -rn "execute(f\"\|% (" backend/app` → no matches in query construction) | **No finding** |
| D9 | Secrets in source — none found; `.env.example` files contain only placeholders | **No finding** |

## E. Data integrity risks

- **No immutability on financial rows.** A `Payout` row can be updated or
  deleted with a plain SQLAlchemy call; nothing enforces "financial evidence
  is never destroyed," which the enterprise brief explicitly requires.
- **No optimistic concurrency / versioning** on `Incident` — two concurrent
  writers (e.g., two Chaos Lab clicks) could race on `incident.state`.
- **`financial_events.id` is derived from `source_record_id`** (`FEV_PYO_{id}`)
  with no uniqueness enforcement beyond the primary key collision itself —
  acceptable for payouts (1:1), but this pattern would silently collide if
  ever extended to a source type with a different ID scheme.
- **No foreign-key `ON DELETE` policy specified** — SQLAlchemy/SQLite defaults
  apply; a merchant delete would not cleanly cascade or protect children.

## F. Architectural weaknesses

- **AI layer has no abstraction boundary.** `extract_candidate_claims` is
  called directly; there is no `AIProvider` interface, no `DemoProvider` /
  `RealLLMProvider` split, no timeout/retry/failure-handling path. Swapping
  in a real LLM call today means editing the function in place, not
  registering a new provider.
- **Recovery is display-only.** The "Recovery Command" screen shows official
  next steps as static-ish text; there is no structured, storable Recovery
  Command entity, so nothing about "what was recommended vs. what was
  approved vs. what was executed" can be queried, audited, or replayed.
- **No API versioning.** All routes are unprefixed (`/incident/...` not
  `/v1/incident/...`) — fine for a prototype, a real blocker for a platform
  that expects to evolve the contract under active integrations.
- **No OpenAPI customization** — FastAPI's auto-generated docs exist at
  `/docs` but response models are often bare `dict` returns rather than
  Pydantic response_model declarations, so the generated schema understates
  what the API actually returns.
- **Single-process, single-database assumption throughout** — no message
  queue, no background job runner; `Chaos Lab` injection and detection run
  synchronously in the request/response cycle, which is fine at demo scale
  and would not be at real transaction volume.

## G. Missing enterprise capabilities (relative to the request in this thread)

Everything in sections 2–9 of the enterprise brief is **absent today**:
multi-tenancy, RBAC, approval state machine, recovery command execution
(dry-run/execute/idempotency), counterfactual simulation, convergence proof,
first-divergence computation. These are not "partially implemented and need
polish" — they do not exist in the codebase in any form yet. Naming this
plainly because it matters for scoping what comes next.

## H. Fake/simulated behavior (must be labeled, not hidden)

- Regex-based evidence extraction presented as "AI interprets evidence" —
  true in spirit (it is the interpretation layer), but it is not a
  model call, and the docs should keep saying so explicitly (they currently
  do, in `ARCHITECTURE.md`'s "What is not implemented" section).
- The Connect screen's Razorpay connection is fully synthetic — already
  labeled "Demo / Sandbox Workspace" in the UI, which is correct and should
  stay.
- Chaos Lab mutations are real DB writes against synthetic data — real
  mechanism, synthetic subject. Already accurate in the UI copy.

## I. Highest-value improvements (if more engineering time is spent)

Ranked by "buyer credibility gained per hour spent," not by raw feature count:

1. **P0** — A structured Recovery Command entity + a real (even if minimal)
   PROPOSED → APPROVED → EXECUTED(simulated) → VERIFIED state machine, with
   dry-run. This directly answers the brief's own "final acceptance test"
   question chain ("what action was proposed / who approved it / what
   actually changed"), and today there is nothing to point to for it.
2. **P0** — A first, honest multi-tenancy pass: a `tenant_id` column on the
   core tables, a request-scoped tenant filter, and tests proving Tenant A
   cannot read Tenant B's data. Does not need to be a full auth system to be
   credible — even a header-based tenant context with tests proving
   isolation changes the conversation with a technical buyer.
3. **P1** — A minimal `AIProvider` abstraction (even with only a
   `DemoProvider` implementation) so "AI can fail without financial truth
   being affected" is demonstrable, not just asserted in prose.
4. **P1** — First-divergence + convergence-check as deterministic
   computations over the existing `financial_events`/`payouts` tables — this
   is genuinely buildable without new infrastructure, reuses the existing
   baseline/temporal services, and is one of the two capabilities the brief
   calls "signature."
5. **P2** — Basic RBAC (even 3 roles, enforced with a simple dependency, no
   real identity provider) — credible enough for a demo conversation without
   requiring a production IdP integration.

## J. Things that should NOT be built right now (low value for the effort)

- **A real OAuth/identity-provider integration.** An enterprise buyer expects
  to plug in *their own* IdP (Okta/Azure AD/etc.) via SSO — building a
  bespoke login system doesn't demonstrate anything they'll actually use,
  and is exactly the kind of code a real integration would delete on day one.
- **A real payment-processor/bank API integration.** No real money should
  move in this codebase under any circumstance; simulated execution is the
  correct ceiling, not a limitation to "fix."
- **A real production LLM wiring with prompt-tuning.** The value being sold
  is the *architecture* that constrains an LLM's blast radius — a slightly
  better regex extractor or a live Claude call doesn't change that story
  and costs real API-key/cost/latency complexity for a demo.
- **Kubernetes/infra-as-code/multi-region anything.** Nobody evaluating this
  is diligencing your Helm charts at this stage.
- **A polished billing/pricing page in-app.** Commercial material belongs in
  a doc a human reads, not a UI screen a demo has to load.

---

## Honest bottom line

What exists is a well-tested, honestly-documented **detection and
reconstruction** prototype with real algorithms behind it. What's being asked
for in the enterprise brief is a **response and recovery platform** with
authorization, execution control, and formal verification — that is a
different, larger system, not a finishing pass on this one. Section I above
is the ranked path from one to the other; it is genuinely multi-day work, not
a single-session extension.
