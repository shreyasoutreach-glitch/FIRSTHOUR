import React, { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { api, CHAOS_MERCHANT_ID } from "../lib/api";
import { formatINR } from "../lib/format";
import ErrorBanner from "../components/ErrorBanner";

const SCENARIOS = [
  { id: "new_beneficiary_burst", label: "New Beneficiary Burst",
    description: "Three large payouts to a brand-new vendor inside nine minutes." },
  { id: "executive_impersonation", label: "Executive Impersonation",
    description: "An urgent, confidential-sounding instruction claiming to be from leadership." },
  { id: "dormant_vendor_activation", label: "Dormant Vendor Activation",
    description: "A vendor with no recent activity suddenly receives a large payout." },
  { id: "duplicate_payout", label: "Duplicate Payout",
    description: "The same invoice reference submitted twice in one batch." },
];

const CHAIN_STEPS: Record<string, string> = {
  FINANCIAL_EVENT_CREATED: "Financial event created",
  BASELINE_DEVIATION: "Baseline deviation measured",
  INCIDENT_DETECTED: "Incident detected",
  GRAPH_UPDATED: "Graph updated",
  EVIDENCE_CORRELATED: "Evidence correlated",
  HUMAN_CONTEXT_REQUIRED: "Human context required",
};

export default function ChaosLab() {
  const [baseline, setBaseline] = useState<any>(null);
  const [baselineError, setBaselineError] = useState<string | null>(null);
  const [selected, setSelected] = useState<string | null>(null);
  const [status, setStatus] = useState<"idle" | "injecting" | "error">("idle");
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [resetting, setResetting] = useState(false);

  const loadBaseline = () => {
    setBaselineError(null);
    api.getMerchantBaseline(CHAOS_MERCHANT_ID).then(setBaseline).catch((e) => {
      setBaseline(null);
      setBaselineError(String(e.message || e));
    });
  };

  useEffect(loadBaseline, []);

  const inject = async (scenarioId: string) => {
    setSelected(scenarioId);
    setStatus("injecting");
    setError(null);
    setResult(null);
    try {
      const res = await api.injectIncident(scenarioId, CHAOS_MERCHANT_ID);
      setResult(res);
      setStatus("idle");
      loadBaseline();
    } catch (e: any) {
      setError(String(e.message || e));
      setStatus("error");
    }
  };

  const reset = async () => {
    setResetting(true);
    try {
      await api.resetDemo();
      setResult(null);
      setSelected(null);
      setStatus("idle");
      setError(null);
      loadBaseline();
    } catch (e: any) {
      setError(String(e.message || e));
    } finally {
      setResetting(false);
    }
  };

  return (
    <div className="max-w-canvas mx-auto px-6 sm:px-10 py-16">
      <div className="flex items-start justify-between flex-wrap gap-4 mb-4">
        <div>
          <p className="label-eyebrow mb-4">Chaos Lab &middot; Live Demonstration</p>
          <h1 className="font-display text-[32px] sm:text-[36px] leading-tight">
            Break the financial reality.
          </h1>
        </div>
        <button className="btn-secondary" onClick={reset} disabled={resetting}>
          {resetting ? "Resettingâ€¦" : "Reset dataset"}
        </button>
      </div>
      <p className="text-[15px] leading-relaxed text-text_primary/70 mb-10 max-w-[600px]">
        This mutates the live backend dataset for Harbor &amp; Co, a clean merchant kept dormant
        for exactly this. Nothing here is pre-recorded.
      </p>

      <div className="paper-card px-6 py-5 mb-10 max-w-[640px]">
        <p className="label-eyebrow mb-3">Current state &middot; Harbor &amp; Co</p>
        {baselineError ? (
          <ErrorBanner message={baselineError} onRetry={loadBaseline} />
        ) : baseline ? (
          <div className="grid grid-cols-3 gap-4 text-[13px]">
            <div>
              <p className="text-text_primary/45 text-[11px] uppercase">Median payout</p>
              <p className="font-display text-[18px]">{formatINR(baseline.median_payout)}</p>
            </div>
            <div>
              <p className="text-text_primary/45 text-[11px] uppercase">Beneficiaries</p>
              <p className="font-display text-[18px]">{baseline.beneficiary_count}</p>
            </div>
            <div>
              <p className="text-text_primary/45 text-[11px] uppercase">Largest historical</p>
              <p className="font-display text-[18px]">{formatINR(baseline.largest_historical_payout)}</p>
            </div>
          </div>
        ) : (
          <p className="text-[13px] text-text_primary/45">Loading baseline&hellip;</p>
        )}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-5 max-w-[820px] mb-10">
        {SCENARIOS.map((s) => (
          <button
            key={s.id}
            onClick={() => inject(s.id)}
            disabled={status === "injecting"}
            className={`text-left paper-card px-5 py-5 transition-colors duration-250 hover:border-vermillion/40 disabled:opacity-50 ${
              selected === s.id ? "border-vermillion/50" : ""
            }`}
          >
            <p className="font-display text-[18px] mb-1.5">{s.label}</p>
            <p className="text-[13px] text-text_primary/55 leading-snug">{s.description}</p>
            <p className="label-eyebrow text-vermillion mt-3">Inject incident</p>
          </button>
        ))}
      </div>

      <AnimatePresence>
        {status === "injecting" && (
          <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                    className="text-[14px] text-text_primary/50 mb-8">
            Writing to the database and running the detector&hellip;
          </motion.p>
        )}
        {error && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                      className="paper-card border border-vermillion/30 px-6 py-5 max-w-[640px] mb-8">
            <p className="text-[13px] text-vermillion">Injection failed: {error}</p>
          </motion.div>
        )}
        {result && (
          <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
                      className="paper-card px-6 py-6 max-w-[640px]">
            <p className="label-eyebrow mb-4">Result &middot; {result.incident_id}</p>
            <ol className="space-y-2 mb-5">
              {result.audit_trail.map((step: string, i: number) => (
                <motion.li
                  key={step}
                  initial={{ opacity: 0, x: -4 }} animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.1 }}
                  className="text-[13px] font-ui text-text_primary/75 flex items-center gap-2"
                >
                  <span className="w-1.5 h-1.5 rounded-full bg-vermillion" />
                  {CHAIN_STEPS[step] || step}
                </motion.li>
              ))}
            </ol>
            <div className="h-px bg-surface_border/25 mb-5" />
            <div className="flex items-center justify-between">
              <div>
                <p className="text-text_primary/45 text-[11px] uppercase mb-1">Incident Evidence Score</p>
                <p className="font-display text-[26px] text-vermillion">{result.incident_evidence_score}/100</p>
              </div>
              <div className="text-right">
                <p className="text-text_primary/45 text-[11px] uppercase mb-1">Payouts injected</p>
                <p className="font-display text-[18px]">{result.payout_ids.length}</p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

