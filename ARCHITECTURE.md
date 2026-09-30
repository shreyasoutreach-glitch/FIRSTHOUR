# PRIMHORA — Architecture

## System diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND (React)                            │
│  Welcome → Connect → Evidence Drop → Reconstruction → THE INCIDENT       │
│  → Financial Graph → Human Witness → Exposure → Recovery Command         │
│  → Recovery Packet → Audit          (+ Chaos Lab, reachable any time)    │
│                                                                            │
│  src/lib/api.ts  ── one function per endpoint, no client-side            │
│                     re-derivation of any financial fact                  │
└───────────────────────────────┬───────────────────────────────────────┘
                                 │  relative "/api" (see api.ts docstring)
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           BACKEND (FastAPI)                              │
│                                                                            │
│  api/routes_incident.py   ── incident, timeline, graph, exposure,        │
│                               evidence, questions, attestation,          │
│                               recovery-packet, audit                     │
│  api/routes_evidence.py   ── upload, analyze                             │
│  api/routes_demo.py       ── inject-incident, reset                     │
│  api/routes_merchant.py   ── connection, baseline                       │
│  api/routes_metrics.py    ── metrics, evaluation                        │
│                                                                            │
│  ┌─────────────────────────── services/ ───────────────────────────┐   │
│  │ financial/baseline.py   median/MAD, robust-z, rolling velocity,  │   │
│  │                          dormancy — pure functions, no LLM       │   │
│  │ incident/scoring.py     weighted Incident Evidence Score          │   │
│  │ incident/detector.py    orchestrates baseline + scoring into an   │   │
│  │                          Incident row (used by seed AND Chaos Lab)│   │
│  │ incident/state_machine.py   INGESTING → ... → ESCALATED           │   │
│  │ entity/resolution.py    strong-identifier-first entity matching   │   │
│  │ temporal/reasoning.py   interval-based event ordering             │   │
│  │ evidence/pipeline.py    hash → MIME-check → extract → verify      │   │
│  │                          (the ONLY place free-text is interpreted)│   │
│  │ graph/builder.py        node/edge graph + bounded blast-radius    │   │
│  │ exposure/engine.py      CONFIRMED / PENDING / ATTEMPTED / RELATED │   │
│  │ human/questions.py      impact × uncertainty × actionability      │   │
│  │ recovery/packet.py      assembles the recovery packet             │   │
│  └────────────────────────────────────────────────────────────────┘   │
│                                                                            │
│  audit/logger.py  ── every service above writes an AuditEvent row        │
│  evaluation/harness.py  ── fixture-based precision/recall/F1/replay      │
│  seed/seed.py  ── deterministic synthetic universe + flagship incident   │
└───────────────────────────────┬───────────────────────────────────────┘
                                 │  SQLAlchemy (portable types)
                                 ▼
                    SQLite (default) or Postgres (DATABASE_URL)
```

## Why services are organized this way

Every service module maps to one clause of the architecture's core principle:

> AI interprets. Deterministic systems establish financial truth. The graph connects
> facts. Humans resolve what machines cannot know.

- **`evidence/pipeline.py`** is the *only* file that touches free text before it becomes
  a structured claim. Its docstring explains exactly why the rule-based extractor is the
  real implementation for this synthetic demo (the seeded WhatsApp/SMS text has a fixed
  vocabulary), and exactly where a real Claude API call would slot in for production —
  the claim shape doesn't change either way.
- **`financial/`, `incident/scoring.py`, `entity/resolution.py`, `temporal/`** never
  import anything LLM-related. They are pure(ish) functions over numbers, strings and
  timestamps, which is why they're the most heavily unit-tested part of the codebase.
- **`graph/builder.py`** only connects rows that already exist — it never infers a
  relationship that isn't backed by a foreign key or a matched claim.
- **`human/questions.py`** decides *what to ask*, never *what the answer means* — the
  answer is stored verbatim in `human_attestations` and only a hand-written rule in
  `routes_incident.py` (e.g., "authorization = NO" → `INCIDENT_CONFIRMED`) reacts to it.

## Data model (full)

**Razorpay-shaped primitives:** `merchants`, `employees`, `orders`, `payments`,
`contacts`, `fund_accounts`, `payouts`, `transfers`, `settlements`, `webhook_events`.

**Incident layer:** `financial_events` (canonical, queryable normalization of every
payout — `event_type`, `source_record_id`, `counterparty_id`, `timestamp`, `amount`,
`attributes` JSON holding the per-event score breakdown), `evidence_artifacts` (sha256,
mime type, extraction status), `extracted_claims` (claim type/value, verification
status, matched financial event), `communication_events` (channel, mentioned amount/
beneficiary, correlation status), `entity_links` (signal, weight, decision),
`incidents` (score, score_components JSON, window, state, dataset/config version),
`incident_events` (join table, sequence-ordered), `human_attestations` (question,
answer, affected predicate — never a financial fact), `audit_events` (actor, event
type, summary, sources, detail).

Indexes exist on every timestamp, source ID, contact ID, fund-account ID, payout ID,
incident ID and beneficiary identifier used in a hot query path (see the bottom of
`app/models/entities.py`).

## The Incident Evidence Score

Six independently-computed 0–1 components, combined with fixed named weights that sum
to 100 (`app/services/incident/scoring.py`):

| Component | Weight | Computed from |
|---|---|---|
| New beneficiary | 25 | Zero prior payouts to this contact before this timestamp |
| Amount anomaly | 20 | Robust z-score: `0.6745 × (x − median) / MAD` over real payout history |
| Velocity anomaly | 20 | Rolling 10-minute payout count/amount vs. the merchant's median |
| Historical novelty | 15 | Inverse of prior transaction count with this beneficiary |
| Dormant entity | 10 | Log-scaled time since this beneficiary's last payout |
| Communication correlation | 10 | 1.0 if a communication's amount+timing matches a payout, 0.5 if plausible, 0 otherwise |

Never called a "fraud probability" anywhere in code, API responses, or UI copy.

## Entity resolution decision bands

Strongest-first, and a match on name similarity **alone can never reach `AUTO_LINK`**
(`app/services/entity/resolution.py`):

| Signal | Weight | Band |
|---|---|---|
| Exact transaction ID | 1.00 | AUTO_LINK |
| Exact fund account ID | 0.95 | AUTO_LINK |
| Exact UPI ID | 0.90 | AUTO_LINK |
| Exact phone (normalized, country-code-agnostic) | 0.85 | REVIEW |
| Normalized name | 0.70 | REVIEW |
| Address similarity | 0.40 | KEEP_SEPARATE |
| Temporal consistency | 0.30 | KEEP_SEPARATE |

## Blast radius

Bounded BFS (default depth 3) outward from a suspicious beneficiary's contact ID,
through **shared VPA / masked bank account values** (not `FundAccount.id`) — this is
deliberate: a mule pattern typically shows up as several different Contact records
(different display names) that all route to the *same* real account, each with their
own `FundAccount` row. Matching on row ID alone would never catch that; matching on the
underlying account value does.

## Scale-down notes (documented, not hidden)

The architecture doc specifies 500 merchants / 50,000+ financial events / 10,000+
payments / 5,000+ payouts as the production-shape target. This build's `seed/seed.py`
generates:

- 60 merchants (Arrow Industries + Harbor & Co + 58 background merchants)
- 143 beneficiaries for Arrow Industries (exact match to spec)
- ~950 historical payouts for Arrow Industries, ~9,200 payouts total
- ~18,400 payments total
- 6 months of history, anchored to a **fixed date** (2026-09-03), not `utcnow()` —
  this is what makes "same seed → same universe" actually true regardless of when or
  where you run it

Every generator function takes its volume from a constant at the top of `seed.py`
(`OTHER_MERCHANT_COUNT`, `ARROW_HISTORICAL_PAYOUTS`, etc.) — bump them and the same code
produces the full production-scale universe. The trade made here was seed runtime
(~13 seconds) and ZIP size, not architecture.

The evaluation harness is similarly scaled down from "50–100 hidden DB-backed cases" to
a fixture-based harness exercising the same pure scoring/resolution/temporal functions —
see the `scope_note` field in `GET /evaluation`'s response.

## Current implementation boundaries

- **Production customer identity and persistent organization provisioning.** The OIDC validation seam exists, but the deployed product still runs in explicitly labelled demo mode.
- **Generic customer ingestion is now implemented as a read-only CSV path.** Provider-specific live adapters remain credential-dependent.
- **PDF evidence-packet export is implemented.** External financial execution is intentionally absent.
- **Docker Compose verification is now executed in CI.**
- **Large hidden DB-backed evaluation is not complete.** The current benchmark is a synthetic fixture suite and must not be presented as production accuracy.
