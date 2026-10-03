# PRIMHORA Industrial Readiness

## What "industrial" means here

Industrial does not mean adding more AI or more screens. It means the system can process
real customer financial evidence repeatedly, at meaningful volume, with deterministic
reproducibility, controlled failure modes, auditable decisions, tenant isolation,
operational recovery, and measurable accuracy.

PRIMHORA is not at that bar yet.

## Algorithm hardening completed in this pass

### 1. Velocity no longer self-counts the event being scored

The incident detector previously included the candidate payout itself in the 10-minute
velocity window. That gave an isolated payout a non-zero velocity signal simply because
it existed.

The detector now builds the velocity window from events strictly before the candidate
timestamp. The current payout is evaluated for amount anomaly; velocity represents prior
activity pressure.

### 2. Case scoring now accounts for breadth

The previous incident score took the maximum component across all suspicious payouts.
That made one extreme payout capable of defining the entire case.

The new aggregation blends the case maximum with the mean component across the case. A
single-event incident is unchanged. Multi-event cases retain the strongest signal while
also reflecting whether the pattern is broad or isolated.

This is still an evidence score, not a fraud probability.

### 3. Existing deterministic truth boundary remains intact

The score is still computed without an LLM. Source-of-record financial events remain the
authority. Evidence extraction can propose claims, but deterministic cross-reference is
what can verify them.

## Why PRIMHORA cannot honestly be called industrial yet

### A. Algorithm validation

The current synthetic benchmark is intentionally separable. It demonstrates that the
engine can detect the seeded scenarios, but it does not establish production precision,
recall, false-positive cost, drift resistance, or calibration.

Required:
- 500-1,000+ adjudicated historical cases across multiple customer types.
- Clean, anomalous, conflicting, duplicate, replayed and incomplete datasets.
- Time-split validation so future data never leaks into the baseline.
- Per-tenant threshold/calibration analysis.
- False-positive and false-negative cost measurement.
- Detection latency and throughput benchmarks.
- Regression fixtures for every production incident pattern.

### B. Baseline and statistical maturity

The current baseline is merchant-level and robust, but it is still prototype-grade.

Gaps include:
- limited seasonality and day-of-week/hour-of-day modeling;
- no formal minimum-sample confidence policy exposed to investigators;
- no drift detection or baseline version lifecycle;
- no currency normalization strategy;
- no population segmentation for materially different payment behaviors;
- no calibration layer connecting evidence score to an empirically measured operating point.

The next algorithmic layer should be hierarchical baselines, temporal decay/seasonality,
data-quality confidence and explicit calibration. It should not silently turn the evidence
score into a probability.

### C. Source-of-record integration

CSV import is not an industrial integration strategy.

Required:
- durable provider adapters;
- webhook ingestion;
- replay-safe event IDs;
- cursor/checkpoint synchronization;
- schema/version negotiation;
- backfill and reconciliation jobs;
- source outage handling;
- provider-specific settlement semantics;
- ERP/ledger/bank adapters.

### D. Data durability and disaster recovery

Authoritative evidence bytes now live in the primary database, but industrial operation
requires tested backup/restore, retention, encryption/key management and recovery-point
objectives.

Required:
- automated backups;
- restore drills;
- RPO/RTO targets;
- retention/legal-hold policy;
- object storage for large artifacts;
- encryption/key rotation;
- evidence integrity verification after restore.

### E. Multi-tenancy and identity

The tenant-scoped data layer is implemented, but production organization lifecycle is
not complete.

Required:
- real OIDC activation;
- durable organization membership;
- invitations and deprovisioning;
- role assignment lifecycle;
- service-account model;
- tenant-aware authorization tests at every object boundary;
- security review of raw SQL and relationship loading;
- customer SSO/SCIM roadmap where required.

### F. Operational reliability

CI passing is not production reliability.

Required:
- structured logs;
- request/correlation IDs;
- metrics and traces;
- SLOs;
- alerting;
- rate limiting;
- abuse protection;
- queue/backpressure strategy;
- dependency timeouts/retries;
- dead-letter handling;
- deployment rollback procedure;
- incident runbooks.

### G. Concurrency and workflow integrity

The recovery workflow has explicit state transitions and idempotency, but industrial operation
needs broader concurrency testing.

Required:
- competing reviewer/approver tests;
- transaction isolation verification on Postgres;
- duplicate webhook race tests;
- import replay tests at scale;
- optimistic/pessimistic locking policy;
- immutable audit event guarantees.

### H. Audit and compliance

An audit table is not automatically an enterprise audit system.

Required:
- tamper-evident or append-only audit architecture;
- actor/device/session attribution appropriate to the customer environment;
- retention policy;
- export and legal discovery controls;
- access logging for sensitive evidence;
- SOC 2 / ISO 27001 control mapping as applicable;
- privacy/data residency analysis for target markets.

### I. Evidence verification

The deterministic boundary is directionally correct, but industrial evidence verification needs
stronger identity matching than amount-only corroboration.

Required:
- transaction/reference identifiers;
- merchant/provider identifiers;
- timestamps with documented tolerance;
- currency;
- beneficiary/account identifiers;
- duplicate-match ambiguity handling;
- provenance chains;
- explicit UNKNOWN/AMBIGUOUS outcomes rather than optimistic matching.

### J. Performance

Several prototype paths intentionally use Python-side scans and ORM queries. They are correct
at demo scale but not yet proven at industrial volume.

Required:
- indexed event/time queries;
- database window functions where appropriate;
- batch processing;
- asynchronous ingestion;
- pagination everywhere;
- load tests with millions of financial events;
- p95/p99 latency targets;
- memory and storage growth budgets.

## Current conclusion

PRIMHORA has crossed from a visual prototype into a hardened technical prototype with a
deterministic financial core, tenant-aware API, RBAC, evidence pipeline, recovery state
machine and CI verification.

It has **not** crossed into an industrial financial-investigation platform because the
remaining risk is no longer mainly UI or feature count. The hard problems are evidence
quality, statistical validation, source integration, operational reliability, durability,
security/compliance and production-scale behavior.

Shipping more screens before solving those layers would make the demo look more industrial
without making the system industrial.
