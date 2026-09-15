import React from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { api } from "../lib/api";
import { useCase } from "../lib/CaseContext";
import { useApiData } from "../lib/useApiData";
import ErrorBanner from "../components/ErrorBanner";
import { formatINR, formatTime } from "../lib/format";
import { StepFooter } from "../components/AppShell";

export default function Reconstruction() {
  const navigate = useNavigate();
  const { incidentId } = useCase();
  const { data, loading, error, reload } = useApiData(
    () => Promise.all([api.getEvidence(incidentId), api.getTimeline(incidentId), api.getIncident(incidentId)])
      .then(([evidence, timeline, incident]) => ({ evidence, timeline, headline: incident.headline })),
    [incidentId]
  );

  const timeline = data?.timeline ?? [];
  const evidence = data?.evidence ?? null;
  const headline = data?.headline ?? null;
  const payoutEvents = timeline.filter((e: any) => e.type === "payout");
  const claims = evidence?.claims ?? [];
  const communications = evidence?.communications ?? [];

  const columnVariants = {
    hidden: { opacity: 0, y: 8 },
    show: (i: number) => ({ opacity: 1, y: 0, transition: { delay: i * 0.12, duration: 0.35, ease: "easeOut" } }),
  };

  return (
    <div className="max-w-canvas mx-auto px-6 sm:px-10 py-16">
      <div className="max-w-[640px] mb-10">
        <p className="label-eyebrow mb-4">Step 3 of 3 &middot; Reconstruction</p>
        <h1 className="font-display text-[32px] sm:text-[36px] leading-tight mb-4">
          Putting the story together.
        </h1>
        <p className="text-[15px] leading-relaxed text-text_primary/70">
          We&rsquo;re linking what you gave us to what your Razorpay records already show.
        </p>
      </div>

      {error && <ErrorBanner message={error} onRetry={reload} />}
      {loading && <p className="text-text_primary/40 text-[14px] mb-8">Loading reconstruction&hellip;</p>}

      {!error && !loading && (
      <>
      <div className="flex gap-8 mb-10 text-[13px] font-ui text-text_primary/60">
        <span><strong className="text-text_primary font-display text-[18px] mr-1">{evidence?.artifacts?.length ?? 0}</strong>evidence</span>
        <span><strong className="text-text_primary font-display text-[18px] mr-1">{payoutEvents.length}</strong>financial events</span>
        <span><strong className="text-text_primary font-display text-[18px] mr-1">{headline?.beneficiary_count ?? 0}</strong>beneficiaries</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <motion.div initial="hidden" animate="show" custom={0} variants={columnVariants}>
          <p className="label-eyebrow mb-3">Evidence</p>
          <div className="space-y-3">
            {communications.map((c: any) => (
              <div key={c.id} className="paper-card px-4 py-3">
                <p className="text-[11px] uppercase tracking-wide text-text_primary/40 mb-1">{c.channel}</p>
                <p className="text-[13px] leading-snug">{c.body_text}</p>
              </div>
            ))}
          </div>
        </motion.div>

        <motion.div initial="hidden" animate="show" custom={1} variants={columnVariants}>
          <p className="label-eyebrow mb-3">Extracted Events</p>
          <div className="space-y-3">
            {claims.filter((c: any) => c.claim_type === "amount").map((c: any) => (
              <div key={c.id} className="paper-card px-4 py-3 flex items-center justify-between">
                <span className="text-[14px] font-ui">{formatINR(c.claim_value.amount)}</span>
                <span
                  className={`text-[10.5px] uppercase tracking-wide px-2 py-0.5 rounded-full border ${
                    c.verification_status === "VERIFIED"
                      ? "border-emerald/40 text-emerald"
                      : c.verification_status === "CONFLICTING"
                      ? "border-vermillion/40 text-vermillion"
                      : "border-amber/40 text-amber"
                  }`}
                >
                  {c.verification_status.toLowerCase()}
                </span>
              </div>
            ))}
          </div>
        </motion.div>

        <motion.div initial="hidden" animate="show" custom={2} variants={columnVariants}>
          <p className="label-eyebrow mb-3">Razorpay Records</p>
          <div className="space-y-3">
            {payoutEvents.map((e: any) => (
              <div key={e.id} className="paper-card px-4 py-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="font-display text-[16px]">{formatINR(e.amount)}</span>
                  <span className="text-[11px] text-text_primary/40">{formatTime(e.timestamp)}</span>
                </div>
                <p className="text-[12px] text-text_primary/50">{e.source_reference} &middot; {e.beneficiary}</p>
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      </>
      )}

      <div className="mt-12">
        <button className="btn-primary" disabled={loading || !!error} onClick={() => navigate("/incident")}>
          View the incident
        </button>
      </div>

      <StepFooter current="/reconstruction" />
    </div>
  );
}

