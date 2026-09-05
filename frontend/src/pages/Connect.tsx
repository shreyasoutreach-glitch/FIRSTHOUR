import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Check } from "lucide-react";
import { api } from "../lib/api";
import { useCase } from "../lib/CaseContext";
import { useApiData } from "../lib/useApiData";
import ErrorBanner from "../components/ErrorBanner";
import { StepFooter } from "../components/AppShell";

const SCOPES = ["Payments", "Payouts", "Contacts", "Fund Accounts", "Events"];

export default function Connect() {
  const navigate = useNavigate();
  const { merchantId } = useCase();
  const { data: connection, loading, error, reload } = useApiData(
    () => api.getMerchantConnection(merchantId),
    [merchantId]
  );
  const [revealed, setRevealed] = useState(0);

  useEffect(() => {
    if (!connection) return;
    const timer = setInterval(() => {
      setRevealed((r) => (r < SCOPES.length ? r + 1 : r));
    }, 220);
    return () => clearInterval(timer);
  }, [connection]);

  return (
    <div className="max-w-canvas mx-auto px-6 sm:px-10 py-16">
      <div className="max-w-[640px]">
        <p className="label-eyebrow mb-4">Step 1 of 3 &middot; Connect</p>
        <h1 className="font-display text-[32px] sm:text-[36px] leading-tight mb-4">
          Connect your financial record.
        </h1>
        <p className="text-[15px] leading-relaxed text-forest/70 mb-10 max-w-[500px]">
          FIRST HOUR reads your financial activity to reconstruct an incident. It does not
          initiate payouts, refunds, transfers or freezes.
        </p>
      </div>

      {error && <ErrorBanner message={error} onRetry={reload} />}

      {!error && (
      <div className="paper-card max-w-[520px] px-8 py-8 mb-10">
        <div className="flex items-center justify-between mb-6">
          <div>
            <p className="label-eyebrow mb-1">Razorpay Workspace</p>
            <p className="font-display text-[20px]">{loading ? "Loading\u2026" : connection?.merchant_name}</p>
          </div>
          <span className="text-[11px] font-ui uppercase tracking-wide text-emerald border border-emerald/40
                            rounded-full px-2.5 py-1">
            {connection?.connected ? "Connected" : "Connecting"}
          </span>
        </div>

        <div className="h-px bg-gold/30 mb-6" />

        <ul className="space-y-3">
          {SCOPES.map((scope, i) => (
            <li key={scope} className="flex items-center gap-3 text-[14px] font-ui">
              <span
                className={`flex items-center justify-center w-5 h-5 rounded-full border transition-colors duration-400 ${
                  i < revealed ? "bg-emerald/10 border-emerald text-emerald" : "border-forest/20 text-transparent"
                }`}
              >
                <Check size={13} strokeWidth={2.5} />
              </span>
              <span className={i < revealed ? "text-forest" : "text-forest/30"}>{scope}</span>
            </li>
          ))}
        </ul>

        <p className="text-[12px] text-forest/45 mt-6">
          FIRST HOUR is read-only in this demo. Workspace: Demo / Sandbox &mdash; not a live
          production connection.
        </p>
      </div>
      )}

      <button
        className="btn-primary"
        disabled={error !== null || revealed < SCOPES.length}
        onClick={() => navigate("/evidence")}
      >
        Continue to evidence
      </button>

      <StepFooter current="/connect" />
    </div>
  );
}
