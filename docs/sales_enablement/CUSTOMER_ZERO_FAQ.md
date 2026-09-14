# FIRST HOUR: CUSTOMER ZERO FAQ

### Is FIRST HOUR going to block my customers?
No. During the Customer Zero pilot, FIRST HOUR operates entirely in Shadow Mode. It generates simulated interventions (e.g., "Would Have Blocked") strictly for analysis and ROI comparison. It cannot alter your production environment.

### Do I need to send PII?
No. FIRST HOUR requires stable unique identifiers to build graph networks and temporal baselines, but these can (and should) be hashed. A `device_id` can be an HMAC string; an `account_id` can be a UUID. We do not need raw names or SSNs to detect behavioral divergence.

### How do you prove FIRST HOUR is better than our existing rules engine?
By utilizing Point-in-Time replay. We replay your historical events chronologically without allowing future data to leak backwards. We then compare the exact timestamp FIRST HOUR would have recommended intervention against the timestamp your existing controls flagged the account.

### Why doesn't FIRST HOUR catch 100% of the fraud?
Attempting to catch the very first $10 stealth transaction on an account that normally spends $1,000 would require setting risk thresholds so low that thousands of legitimate customers would be blocked daily. FIRST HOUR is mathematically designed to wait for cumulative velocity or network graph anomalies to cross an economically viable threshold, minimizing customer friction while limiting the blast radius of an attack.

### Are the simulated financial results guaranteed?
No. Simulated ROI assumes that an intervention recommendation (like "HOLD_AND_REVIEW") successfully stops the outflow of capital. Real ROI depends on the operational effectiveness of your fraud teams and actual review costs. Simulated results represent *potential* exposure prevented.

### Does the AI make the final decision?
No. FIRST HOUR uses deterministic statistical baselines and network graphs to establish financial truth. Generative AI is used to interpret messy telemetry and synthesize human-readable timelines, but it does not dictate the financial action policy.
