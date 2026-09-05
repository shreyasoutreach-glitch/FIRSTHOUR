import React from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { MessageSquare, ArrowDownRight } from "lucide-react";
import { api } from "../lib/api";
import { useCase } from "../lib/CaseContext";
import { useApiData } from "../lib/useApiData";
import ErrorBanner from "../components/ErrorBanner";
import { formatINR, formatTime, formatDuration } from "../lib/format";
import SourceRef from "../components/SourceRef";
import { StepFooter } from "../components/AppShell";

export default function TheIncident() {
  const navigate = useNavigate();
  const { incidentId } = useCase();
  const { data, loading, error, reload } = useApiData(
    () => Promise.all([api.getIncident(incidentId), api.getTimeline(incidentId)])
      .then(([incident, timeline]) => ({ incident, timeline })),
    [incidentId]
  );

  if (error) {
    return (
      <div className="max-w-canvas mx-auto px-6 sm:px-10 py-16">
        <ErrorBanner message={error} onRetry={reload} />
      </div>
    );
  }

  if (loading || !data) {
    return <div className="max-w-canvas mx-auto px-6 sm:px-10 py-16 text-forest/50">Loading case file&hellip;</div>;
  }

  const { incident, timeline } = data;
  const h = incident.headline;
  const payoutCount = timeline.filter((e: any) => e.type === "payout").length;

  return (
    <div className="max-w-canvas mx-auto px-6 sm:px-10 py-16">
      <p className="label-eyebrow mb-4">The Incident &middot; {incident.id}</p>
      <h1 className="font-display text-[32px] sm:text-[36px] leading-tight mb-8">Here&rsquo;s what happened.</h1>

      <div className="mb-4">
        <p className="hero-money text-[52px] sm:text-[68px] leading-none text-forest">
          {formatINR(h.total_exposed)}
        </p>
        <p className="label-eyebrow text-vermillion mt-2">Exposed</p>
      </div>
      <p className="text-[15px] font-ui text-forest/60 mb-14">
        {payoutCount} payouts &middot; {h.beneficiary_count} beneficiaries &middot; {formatDuration(h.window_seconds)}
      </p>

      <div className="grid grid-cols-1 lg:grid-cols-[1fr_320px] gap-12">
        {/* Vertical incident spine */}
        <div className="relative pl-8">
          <div className="absolute left-[9px] top-2 bottom-2 w-px bg-gold/40" aria-hidden />
          <ol className="space-y-8">
            {timeline.map((event, i) => (
              <motion.li
                key={event.id}
                initial={{ opacity: 0, x: -6 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.15, duration: 0.35, ease: "easeOut" }}
                className="relative"
              >
                <span
                  className={`absolute -left-8 top-1 w-[19px] h-[19px] rounded-full border-2 flex items-center justify-center bg-ivory ${
                    event.type === "communication" ? "border-amber" : "border-vermillion"
                  }`}
                >
                  {event.type === "communication" ? (
                    <MessageSquare size={10} className="text-amber" />
                  ) : (
                    <ArrowDownRight size={10} className="text-vermillion" />
                  )}
                </span>
                <p className="text-[12px] font-ui text-forest/45 mb-1">{formatTime(event.timestamp)}</p>
                {event.type === "communication" ? (
                  <div>
                    <p className="label-eyebrow text-amber mb-1">Communication Event</p>
                    <p className="text-[14px] leading-snug max-w-[480px] text-forest/80">
                      &ldquo;{event.detail.length > 140 ? event.detail.slice(0, 140) + "…" : event.detail}&rdquo;
                      <SourceRef id={event.source_artifact_id} label="evidence" />
                    </p>
                  </div>
                ) : (
                  <div>
                    <p className={`label-eyebrow mb-1 ${event.label === "NEW BENEFICIARY" ? "text-vermillion" : "text-forest/50"}`}>
                      {event.label}
                    </p>
                    <p className="font-display text-[22px]">
                      {formatINR(event.amount)}
                      <SourceRef id={event.source_reference} label="payout" />
                    </p>
                    <p className="text-[13px] text-forest/55">{event.beneficiary}</p>
                  </div>
                )}
              </motion.li>
            ))}
          </ol>
        </div>

        {/* Right-hand evidence panel */}
        <aside className="paper-card px-6 py-6 h-fit">
          <p className="label-eyebrow mb-4">Why this stands out</p>
          <ul className="space-y-4">
            <li>
              <p className="font-display text-[22px] text-vermillion">{h.multiple_of_median.toFixed(0)}&times;</p>
              <p className="text-[13px] text-forest/60">normal payout amount</p>
            </li>
            <li>
              <p className="font-display text-[22px] text-vermillion">{h.new_beneficiary_count}</p>
              <p className="text-[13px] text-forest/60">new beneficiaries, never paid before</p>
            </li>
            <li>
              <p className="font-display text-[22px] text-vermillion">0</p>
              <p className="text-[13px] text-forest/60">prior transactions with these beneficiaries</p>
            </li>
            <li>
              <p className="font-display text-[22px] text-vermillion">{formatDuration(h.window_seconds)}</p>
              <p className="text-[13px] text-forest/60">velocity cluster &mdash; all three payouts back to back</p>
            </li>
          </ul>
          <div className="h-px bg-gold/25 my-5" />
          <p className="text-[12px] text-forest/45 leading-relaxed">
            Incident Evidence Score: <strong className="text-forest">{incident.incident_evidence_score}</strong>/100
            &mdash; a weighted, computed measure of how unusual this looks against Arrow Industries&rsquo; own
            history. Not a probability of fraud.
          </p>
        </aside>
      </div>

      <div className="mt-14">
        <button className="btn-primary" onClick={() => navigate("/graph")}>
          See the financial graph
        </button>
      </div>

      <StepFooter current="/incident" />
    </div>
  );
}
