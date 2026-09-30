# PRIMHORA

PRIMHORA is a read-only financial-incident investigation and evidence-reconstruction platform.

It helps finance, operations, and forensic teams answer: what happened, what can we prove, and what still requires a human answer?

PRIMHORA does not move, freeze, reverse, or recover money. It prepares evidence packets for authorized humans and institutions.

## Problem

Financial incidents combine payment exports, bank statements, invoices, messages, screenshots and human context. The product problem is reconstruction: establish source-backed financial facts, correlate evidence, expose contradictions and produce an auditable case packet.

See docs/MARKET_EVIDENCE.md for sourced market evidence, confidence levels, conflicting data series and the segment hypothesis.

## Target user

Primary hypothesis: mid-market finance, accounts-payable, treasury and operations teams investigating suspicious payments or reconciliation failures.

Secondary hypothesis: CA and forensic-accounting firms investigating client financial incidents.

These are hypotheses, not proven product-market fit.

## Product principle

**AI interprets. Deterministic code establishes financial truth. Humans resolve what machines cannot know.**

No LLM may generate authoritative amounts, beneficiaries, timestamps, exposure values or financial scores. Model extraction is candidate evidence only and must be verified against source records.

## Data-source boundary

The current schema includes a Razorpay-shaped payment vocabulary. Razorpay is a supported data-source shape, not a claimed partnership or current production connection.

The first production onboarding path is generic payout/bank-statement CSV import. Additional provider adapters remain credential-dependent or incomplete.

## Read-only boundary

PRIMHORA never initiates or cancels payments, freezes or reverses funds, changes beneficiaries or credentials, claims funds were recovered, or treats AI output as financial truth.

## Scope

In scope: customer file ingestion, deterministic normalization/reconciliation, incident reconstruction, evidence provenance, graph/exposure views, human attestations, packet generation, PDF export, reproducible CI and evaluation.

Non-goals: money movement, autonomous fraud decisions, bank-account control, production payment execution and fabricated integrations.

## Verification status

**Current production verification snapshot: 30 September 2026**

- GitHub Actions: passing.
- Backend: **146 tests passed** in the latest verified CI run.
- Frontend: lint and production build passed in CI.
- Docker Compose: build/startup and backend /health verification passed in CI.
- DB-backed API evaluation: **60 labeled regression cases** through the payout CSV API path, with clean/suspicious cases plus malformed-input and replay checks.
- Render backend: **LIVE** on the merged main commit.
- Render frontend: **LIVE** on the merged main commit.
- Workspace creation: **backend-persisted in the demo environment**, with a tenant and owner token created by the API rather than browser-only state.
- Render frontend API origin: **configured** to call the Render backend directly.
- API hardening: security headers added; metrics/evaluation endpoints require VIEW permission; evidence upload validates merchant/incident ownership.
- Fresh deployed-browser verification: **not yet completed**, so live UI behavior should not be described as browser-verified.
- Production identity-provider activation: **credential-dependent**, not represented as complete.
- Live payment/bank provider adapters beyond the generic CSV path: **not represented as complete**.

The repository is therefore in a substantially verified capstone/product state, but it is **not yet represented as fully production-ready for external customer data**. The detailed gap register is in `PRODUCTION_DISCREPANCIES.md`.

## Evaluation

### Synthetic benchmark

CI run 36678195609 on 2026-09-30 reported:

- 300 synthetic labeled cases.
- Event detection precision/recall/F1: 1.000.
- Entity-link precision/recall/F1: 1.000.
- Entity exact-decision accuracy: 0.833 on 6 cases.
- Timeline fixture accuracy: 1.000.
- Replay consistency: 1.000 across 5 runs.

These are synthetic fixture results only. They are not real-world fraud-detection accuracy, are not representative of Indian companies, and are not evidence of product-market fit.

### DB-backed API regression suite

The current regression suite exercises the real payout-CSV API path against a test database with **60 labeled cases**:

- 30 clean cases.
- 30 suspicious cases.
- Malformed CSV rejection.
- Replay/idempotency behavior.

The suite is a visible regression suite, not a hidden benchmark and not a substitute for broader real-world evaluation. Future coverage should expand across conflicting evidence, dormant vendors, duplicate payouts, vendor bank-detail changes, velocity anomalies, provider-specific payloads and cross-tenant attack cases.

## Roadmap

- Phase 1 audit: **complete**.
- Phase 2 market evidence: **complete**.
- Phase 3 capstone repositioning: **complete**.
- Phase 4 real ingestion, read-only enforcement, PDF export, Docker verification and CI: **substantially complete**, with production identity/provider onboarding still credential-dependent.
- Phase 5 selected-segment UX and vendor-bank-change scenario: **implemented**; deployed-browser verification remains.
- Production hardening pass: **implemented for the current application-level gaps identified in `PRODUCTION_DISCREPANCIES.md`**; infrastructure/customer-data gates remain.
- Phase 6 executable evaluation: **complete for the current 60-case DB-backed API regression suite**; broader incident-type and hidden-evaluation coverage remains.

## What PRIMHORA does not claim

PRIMHORA does not currently claim:

- autonomous fraud decisions;
- live access to a bank, payment processor or Razorpay account;
- automatic recovery or reversal of funds;
- production customer authentication without an activated identity provider;
- real-world fraud-detection precision/recall;
- product-market fit;
- browser-verified production UX.
- durable production evidence storage or a completed customer-data retention/backup policy.

That boundary is deliberate. The goal is a defensible capstone and a credible foundation for a real product, not a demo wearing a production costume.
