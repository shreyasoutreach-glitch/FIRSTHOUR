# FIRST HOUR: CUSTOMER ZERO PILOT

## WHAT IS FIRST HOUR?
FIRST HOUR is a Financial Attack Reconstruction and Incident Response platform. It reconstructs financial attacks from fragmented event data, identifies where legitimate behavior first diverged, maps connected exposure, and gives investigators a recovery-ready view before an incident becomes a larger loss.

## WHO IS IT FOR?
Payment gateways, BaaS providers, fintechs, UPI ecosystem companies, and financial enterprise fraud/risk teams.

## WHAT PROBLEM DOES IT SOLVE?
Existing anomaly detection systems evaluate single transactions in a vacuum, generating massive false-positive queues. When a stealth attack (like a dormant Account Takeover or Low-and-Slow drain) occurs, the blast radius is hidden across fragmented ledgers. FIRST HOUR automatically fuses identity, behavior, temporal velocity, and network graph signals to isolate the attack, map the exposure, and recommend targeted intervention.

## WHAT DOES FIRST HOUR DO?
- **Point-in-Time Replay:** Ingests historical data and accurately reconstructs the exact state of knowledge at any microsecond.
- **First Divergence:** Identifies the precise mathematical moment an account broke its historical baseline.
- **Graph Exposure:** Dynamically clusters fan-in/fan-out network anomalies (e.g., Money Mules).
- **Simulated Recovery:** Calculates prevented loss vs. operational friction.

## WHAT DOES IT NOT DO?
FIRST HOUR does not autonomously move money. It does not blindly authorize financial execution based on AI output. In Customer Zero pilots, it operates entirely in **Shadow Mode** (read-only evaluation).

## WHAT DOES A PILOT ENTAIL?
You provide a historical event export (CSV/JSON). We perform schema mapping, execute a Data Quality Gate, and run a full Point-in-Time Replay. We then deliver an Executive Report comparing FIRST HOUR's detection lead-time and blast-radius discovery against your existing historical controls.

## WHAT DOES SUCCESS LOOK LIKE?
A successful pilot demonstrates that FIRST HOUR discovered an incident earlier, mapped a broader connected exposure network, or reconstructed an attack timeline faster and more accurately than existing legacy controls.
