# PRIMHORA Evaluation Report

## Reproducible CI evaluation
GitHub Actions executes the deterministic fixture benchmark and the DB-backed API-path evaluation.

### Fixture benchmark
Run 36678195609 on 2026-09-30 used dataset primhora-synthetic-eval-v2, population 300, seed 20260930.
Event detection precision/recall/F1: 1.000 / 1.000 / 1.000.
Entity-link precision/recall/F1: 1.000 / 1.000 / 1.000 across 6 labeled decisions.
Entity exact-decision accuracy: 0.833 across 6 decisions.
Timeline fixture accuracy: 1.000.
Replay consistency: 1.000 across 5 repeated runs.

These are synthetic fixture results only and must not be presented as real-world fraud-detection accuracy.

### DB-backed API-path suite
The current evaluation target executes through POST /api/import/payouts-csv with a real temporary SQLite database and TenantScopedSession.

Population: 60 labeled API cases, 30 clean and 30 suspicious, plus malformed-input and replayed-import checks.
Each labeled case is persisted through the same CSV onboarding route used by the product, then evaluated by the incident detector. CI emits TP/FP/TN/FN, precision, recall and an explicit failure list.

Coverage includes clean normal payouts, new beneficiaries, amount anomalies, malformed source data and replayed source IDs. Cross-tenant access, read-only recovery execution, evidence upload security and PDF generation remain separately covered by the API/security test suite.

## What this does not prove
- It does not establish production fraud-detection accuracy.
- It does not represent Indian companies or any external customer population.
- It does not test a live bank or payment-provider adapter.
- It does not establish product-market fit.

## Remaining evaluation gap
Future cases should add conflicting evidence, dormant-vendor reactivation, duplicate payouts, vendor bank-detail changes, velocity anomalies, cross-tenant attack cases and provider-specific malformed payloads as independently labeled API cases.