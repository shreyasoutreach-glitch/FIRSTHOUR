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
AI interprets. Deterministic code establishes financial truth. Humans resolve what machines cannot know.

No LLM may generate authoritative amounts, beneficiaries, timestamps, exposure values or financial scores. Model extraction is candidate evidence only and must be verified against source records.

## Data-source boundary
The current schema includes a Razorpay-shaped payment vocabulary. Razorpay is a supported data-source shape, not a claimed partnership or current production connection. The first production onboarding path is generic payout/bank-statement CSV import.

## Read-only boundary
PRIMHORA never initiates or cancels payments, freezes or reverses funds, changes beneficiaries or credentials, claims funds were recovered, or treats AI output as financial truth.

## Scope
In scope: customer file ingestion, deterministic normalization/reconciliation, incident reconstruction, evidence provenance, graph/exposure views, human attestations, packet generation, PDF export, reproducible CI and evaluation.

Non-goals: money movement, autonomous fraud decisions, bank-account control, production payment execution and fabricated integrations.

## Roadmap
Phase 1 audit: complete.
Phase 2 market evidence: complete.
Phase 3 capstone repositioning: complete.
Phase 4 real ingestion, read-only enforcement, PDF export, Docker verification and CI: substantially complete, with production identity/provider onboarding still credential-dependent.
Phase 5 selected-segment UX and vendor-bank-change scenario: implemented; deployed browser verification remains.
Phase 6 executable precision/recall evaluation: complete for the current 60-case DB-backed API regression suite; broader incident-type coverage remains.

## Verification status
GitHub Actions is the reproducible verification path for backend tests, frontend lint/build, Docker health and synthetic evaluation. Render services are live. Production identity-provider activation and live provider adapters require customer credentials and are not represented as complete.

## Synthetic evaluation
CI run 36678195609 on 2026-09-30: 300 synthetic labeled cases, event detection precision/recall/F1 1.000, entity-link precision/recall/F1 1.000, entity exact-decision accuracy 0.833 on 6 cases, timeline fixture accuracy 1.000, replay consistency 1.000 across 5 runs.

These are synthetic fixture results only. They are not real-world fraud-detection accuracy, are not representative of Indian companies, and are not evidence of product-market fit. A DB-backed API evaluation suite is still required.