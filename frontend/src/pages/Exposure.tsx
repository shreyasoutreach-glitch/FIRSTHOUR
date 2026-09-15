import React from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../lib/api";
import { useCase } from "../lib/CaseContext";
import { useApiData } from "../lib/useApiData";
import ErrorBanner from "../components/ErrorBanner";
import { formatINR } from "../lib/format";
import SourceRef from "../components/SourceRef";
import { StepFooter } from "../components/AppShell";

const CATEGORIES = [
  { key: "confirmed_moved", label: "Confirmed moved", color: "text-vermillion", border: "border-vermillion/30" },
  { key: "pending", label: "Pending", color: "text-amber", border: "border-amber/30" },
  { key: "attempted", label: "Attempted", color: "text-text_primary/60", border: "border-forest/15" },
];

export default function Exposure() {
  const navigate = useNavigate();
  const { incidentId } = useCase();
  const { data: exposure, loading, error, reload } = useApiData(() => api.getExposure(incidentId), [incidentId]);

  return (
    <div className="max-w-canvas mx-auto px-6 sm:px-10 py-16">
      <p className="label-eyebrow mb-4">Step 6 &middot; Exposure</p>
      <h1 className="font-display text-[32px] sm:text-[36px] leading-tight mb-4">
        How much is actually exposed?
      </h1>
      <p className="text-[15px] leading-relaxed text-text_primary/70 mb-12 max-w-[560px]">
        We keep these separate on purpose. A frightening single total helps no one make a decision.
      </p>

      {error && <ErrorBanner message={error} onRetry={reload} />}
      {loading && <p className="text-text_primary/40 text-[14px] mb-8">Loading exposure&hellip;</p>}

      {!error && exposure && (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-5 mb-10 max-w-[900px]">
            {CATEGORIES.map((cat) => {
              const data = exposure[cat.key];
              return (
                <div key={cat.key} className={`paper-card border ${cat.border} px-6 py-6`}>
                  <p className="label-eyebrow mb-3">{cat.label}</p>
                  <p className={`hero-money text-[28px] ${cat.color}`}>{formatINR(data.total)}</p>
                  <p className="text-[12px] text-text_primary/45 mt-2">
                    {data.financial_event_ids.length} payout(s)
                    {data.financial_event_ids.slice(0, 3).map((id: string) => (
                      <SourceRef key={id} id={id} />
                    ))}
                  </p>
                </div>
              );
            })}
          </div>

          <div className="paper-card px-6 py-6 max-w-[560px] mb-12">
            <p className="label-eyebrow mb-3">Related &middot; Blast Radius</p>
            <p className="hero-money text-[28px] text-text_primary/70 mb-2">{formatINR(exposure.related.total)}</p>
            <p className="text-[13px] text-text_primary/55">
              Reachable within {exposure.blast_radius.traversal_depth} hops through shared beneficiaries
              and fund accounts &mdash; {exposure.related.affected_entities} entities,{" "}
              {exposure.related.affected_fund_accounts} fund accounts touched.
            </p>
          </div>
        </>
      )}

      <button className="btn-primary" disabled={loading || !!error} onClick={() => navigate("/recovery")}>
        Continue to recovery
      </button>

      <StepFooter current="/exposure" />
    </div>
  );
}

