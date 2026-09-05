# FIRST HOUR — 5-Minute Demo Script

**Setup (before judges arrive):** backend seeded and running on :8000, frontend running
on :5173 (or the docker-compose stack on :8080). Load `http://localhost:5173/` fresh.

Honesty note: everything below is a real API call against a real SQLite/Postgres
database — nothing is pre-recorded. If a judge asks to see the request, open the
Network tab; every screen's data comes from the endpoints listed in `ARCHITECTURE.md`.

---

### 0:00 – 0:30 · Welcome → Connect
Open on the calm, dark Welcome screen. Say: *"FIRST HOUR starts after suspicious money
movement has already happened — the goal is turning panic into a clear case."* Click
**Start recovery** → **Connect**. Point out: read-only, Demo/Sandbox labeled explicitly,
scopes revealing (Payments, Payouts, Contacts, Fund Accounts, Events) are real merchant
data pulled live from `GET /merchant/MER_ARROW/connection`.

### 0:30 – 1:00 · Evidence Drop
Show the two WhatsApp exports already ingested from Arrow Industries' Finance Ops
thread (real rows in `evidence_artifacts`, fetched via `GET /incident/INC-001/evidence`).
Optionally drop a new `.txt` file live to show `POST /evidence/upload` +
`POST /evidence/analyze` running in real time — the tile updates from "Processing" to
"Processed" once the claim extraction genuinely completes.

### 1:00 – 1:30 · Reconstruction
Three columns — Evidence, Extracted Events, Razorpay Records — populate from three real
endpoints. Point at a `VERIFIED` badge and say: *"That's not the LLM being confident —
that's a regex-extracted ₹1,00,00,000 claim that matched a real payout row within 1%
tolerance. If it didn't match, it would say CONFLICTING, not VERIFIED."*

### 1:30 – 2:30 · THE INCIDENT (the centerpiece)
Hero number, incident spine, right-rail "Why this stands out." Say the numbers out loud
as you point at them — they're computed, not typed in:
- *"₹3,00,00,000 exposed, 3 payouts, 2 beneficiaries, 9 minutes 8 seconds — all from
  `GET /incident/INC-001/timeline`."*
- *"543× Arrow Industries' own median payout of ₹18,400 — that's a robust z-score over
  their real 6-month history, not a hardcoded threshold."*
- *"Incident Evidence Score: 90.01 out of 100 — a weighted sum of six components, each
  one inspectable. Never called a fraud probability."*

### 2:30 – 3:00 · Financial Graph
Click through Merchant → Payout → Contact → Fund Account nodes. Click a node, show the
provenance sheet populate with real row data. *"Every line here is a foreign key or a
matched claim — nothing is a suggested relationship."*

### 3:00 – 3:30 · Human Witness
Show the single highest-priority question ("Did you personally authorize these
payouts?"). Answer **No**. Point out the confirmation copy — *"Recorded. This does not
rewrite financial records"* — and that the incident state visibly moves to
`INCIDENT_CONFIRMED` in response to `POST /incident/INC-001/attestation`.

### 3:30 – 4:00 · Exposure
Confirmed / Pending / Attempted / Related, never combined into one scarier number.
Click a "source" tag next to an amount to show it resolves to an exact payout ID.

### 4:00 – 4:20 · Recovery Command → Recovery Packet
Say plainly: *"FIRST HOUR does not call the bank, does not call 1930, does not freeze
anything — it prepares everything those channels will ask for."* Scroll the Recovery
Packet to show it's the same case data, reassembled into something a bank's fraud desk
or the cybercrime portal can act on immediately.

### 4:20 – 4:40 · Audit
*"This is the accountable record — not a narrative."* Show `INCIDENT_CREATED` →
`ATTESTATION_ADDED` → `CASE_STATE_CHANGED`, each with real timestamps and source IDs.

### 4:40 – 5:00 · Chaos Lab (if time / on request)
Pick **New Beneficiary Burst** on Harbor & Co (a merchant kept clean specifically for
this). Click it. In under a second, real rows are written, the detector runs, and the
chain (`FINANCIAL_EVENT_CREATED → BASELINE_DEVIATION → INCIDENT_DETECTED → GRAPH_UPDATED
→ EVIDENCE_CORRELATED → HUMAN_CONTEXT_REQUIRED`) renders with a real computed score.
Close with **Reset dataset** to show the whole universe (including the flagship
incident) rebuilds deterministically from the same seed.

---

## If something goes wrong live
- **Backend not responding:** every screen shows an explicit error banner with a
  "Try again" button — no screen silently shows an empty state as if nothing were wrong.
- **Want to rewind:** Chaos Lab's **Reset dataset** button calls `POST /demo/reset`,
  which reseeds everything, including `INC-001`, in ~13 seconds.
- **A judge asks "is this real or a mock?"**: open `backend/app/services/incident/
  scoring.py` and `financial/baseline.py` on screen — there is no `is_fraud = true`
  anywhere in the codebase, and `grep -r "is_fraud" backend/` returns nothing.
