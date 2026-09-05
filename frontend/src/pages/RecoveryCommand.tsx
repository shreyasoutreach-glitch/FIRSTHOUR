import React from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../lib/api";
import { useCase } from "../lib/CaseContext";
import { useApiData } from "../lib/useApiData";
import ErrorBanner from "../components/ErrorBanner";
import { StepFooter } from "../components/AppShell";

export default function RecoveryCommand() {
  const navigate = useNavigate();
  const { incidentId } = useCase();
  const { data: steps, loading, error, reload } = useApiData(
    () => api.getRecoveryPacket(incidentId).then((p) => p.official_next_steps as string[]),
    [incidentId]
  );

  return (
    <div className="max-w-canvas mx-auto px-6 sm:px-10 py-16">
      <p className="label-eyebrow mb-4">Step 7 &middot; Recovery</p>
      <h1 className="font-display text-[32px] sm:text-[36px] leading-tight mb-4">
        You have a clear case now.
      </h1>
      <p className="text-[15px] leading-relaxed text-forest/70 mb-12 max-w-[560px]">
        Everything below uses official channels. FIRST HOUR does not contact your bank, Razorpay
        or the police on your behalf &mdash; it gives you exactly what they&rsquo;ll ask for.
      </p>

      {error && <ErrorBanner message={error} onRetry={reload} />}
      {loading && <p className="text-forest/40 text-[14px] mb-8">Preparing your next steps&hellip;</p>}

      {!error && steps && (
        <ol className="max-w-[640px] space-y-5 mb-14">
          {steps.map((step, i) => (
            <li key={i} className="flex gap-4">
              <span className="font-display text-[20px] text-gold w-7 shrink-0">{i + 1}</span>
              <p className="text-[14px] leading-relaxed text-forest/80 pt-0.5">{step}</p>
            </li>
          ))}
        </ol>
      )}

      <button className="btn-primary" disabled={loading || !!error} onClick={() => navigate("/recovery/packet")}>
        View recovery packet
      </button>

      <StepFooter current="/recovery" />
    </div>
  );
}
