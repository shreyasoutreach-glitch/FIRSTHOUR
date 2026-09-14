# FIRST HOUR: PILOT SUCCESS SCORECARD

The Customer Zero evaluation does not rely on generic classification metrics (like aggregate AUC). Success is measured in commercial and operational outcomes.

## PRIMARY METRICS (COMMERCIAL ROI)
- **INCIDENTS DISCOVERED:** Total distinct attacks identified.
- **INCIDENTS MISSED BY EXISTING CONTROLS:** Attacks FIRST HOUR found that legacy systems ignored.
- **INCREMENTAL LEAD TIME:** How much faster (hours/minutes) FIRST HOUR flagged the divergence vs. the legacy control.
- **FIRST DIVERGENCE TIME:** The timestamp of the earliest anomalous signal.
- **EXPOSURE BEFORE FIRST HOUR:** The financial loss incurred before FIRST HOUR recommended intervention.
- **EXPOSURE BEFORE EXISTING CONTROL:** The financial loss incurred before the legacy system intervened.
- **CONNECTED ACCOUNTS DISCOVERED:** Number of compromised accounts mapped in a single incident.
- **CONNECTED BENEFICIARIES DISCOVERED:** Number of mule destinations isolated.
- **INVESTIGATION TIME SAVED:** Simulated hours saved via automated chronological reconstruction.
- **POTENTIAL EXPOSURE PREVENTED:** Total capital that would have been saved by FIRST HOUR.

## SECONDARY METRICS (OPERATIONAL FRICTION)
- **False-Positive Events:** Legitimate transactions incorrectly flagged for intervention.
- **Review Workload:** The number of manual reviews generated.
- **Data Completeness:** The percentage of provided telemetry usable by the engines.
- **Latency (Simulated):** P95 processing time per event in the replay pipeline.
