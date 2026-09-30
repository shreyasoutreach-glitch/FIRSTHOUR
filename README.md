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

## Research questions
1. Can PRIMHORA reconstruct a financial incident faster than a manual workflow?
2. Can deterministic reconciliation reduce unsupported conclusions?
3. Can provenance make findings easier to audit?
4. Which incident types justify paid software?
5. Will target users trust a read-only evidence workspace with sensitive exports?

## Scope
In scope: customer file ingestion, deterministic normalization/reconciliation, incident reconstruction, evidence provenance, graph/exposure views, human attestations, packet generation, PDF export, reproducible CI and evaluation.

Non-goals: money movement, autonomous fraud decisions, bank-account control, production payment execution and fabricated integrations.

## Evaluation
Every metric must state dataset version, population, date, definition, command and failures. Synthetic benchmark results are never presented as real-world accuracy.

## Methodology
source data -> normalization -> deterministic truth -> evidence extraction -> verification -> reconstruction -> human context -> packet.

## Roadmap
Phase 1 audit: complete.
Phase 2 market evidence: complete.
Phase 3 capstone repositioning: in progress.
Phase 4 real ingestion, read-only enforcement, PDF export, Docker verification and CI.
Phase 5 selected-segment UX and vendor-bank-change scenario.
Phase 6 executable precision/recall evaluation and failure reporting.

## Verification status
AUDIT.md records the current verified/unverified state. Render services are live. Local test execution was unavailable in the current audit environment, so unexecuted tests are not described as passing.
