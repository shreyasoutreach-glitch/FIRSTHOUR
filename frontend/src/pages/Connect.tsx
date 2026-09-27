import React, { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { Check, RefreshCw, ShieldAlert } from "lucide-react";
import { api } from "../lib/api";
import { useCase } from "../lib/CaseContext";
import { useApiData } from "../lib/useApiData";
import ErrorBanner from "../components/ErrorBanner";
import { StepFooter } from "../components/AppShell";

const SCOPES = ["Payments", "Payouts", "Contacts", "Fund Accounts", "Events"];

export default function Connect() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const isProduction = searchParams.get("mode") === "production";
  const { merchantId } = useCase();
  
  const { data: connection, loading, error, reload } = useApiData(
    () => api.getMerchantConnection(merchantId),
    [merchantId]
  );

  const [revealed, setRevealed] = useState(0);
  const [isConnectingLive, setIsConnectingLive] = useState(false);
  const [syncResult, setSyncResult] = useState<any>(null);
  const [syncError, setSyncError] = useState<string | null>(null);

  useEffect(() => {
    if (isProduction) return;
    if (!connection) return;
    const timer = setInterval(() => {
      setRevealed((r) => (r < SCOPES.length ? r + 1 : r));
    }, 220);
    return () => clearInterval(timer);
  }, [connection, isProduction]);

  const handleLiveConnect = async () => {
    setIsConnectingLive(true);
    setSyncError(null);
    setSyncResult(null);
    try {
      const result = await api.syncMerchant(merchantId);
      setSyncResult(result);
      reload();
    } catch (e: any) {
      setSyncError(String(e?.data?.detail || e?.message || e));
    } finally {
      setIsConnectingLive(false);
    }
  };

  return (
    <div className="max-w-canvas mx-auto px-6 sm:px-10 py-16">
      <div className="max-w-[640px]">
        <p className="label-eyebrow mb-4">Step 1 of 3 &middot; Connect</p>
        <h1 className="font-display text-[32px] sm:text-[36px] leading-tight mb-4">
          {isProduction ? "Connect your live gateway." : "Connect your financial record."}
        </h1>
        <p className="text-[15px] leading-relaxed text-text_primary/70 mb-10 max-w-[500px]">
          {isProduction 
            ? "Enter your read-only gateway key. FIRST HOUR will securely sync your live ledger without using mock data."
            : "FIRST HOUR reads your financial activity to reconstruct an incident. It does not initiate payouts, refunds, transfers or freezes."}
        </p>
      </div>

      {(error || syncError) && <ErrorBanner message={syncError || error || ""} onRetry={syncError ? handleLiveConnect : reload} />}

      {isProduction ? (
        <div className="paper-card max-w-[520px] px-8 py-8 mb-10 border-gold/30 shadow-lg">
          <div className="flex items-center gap-3 mb-6">
            <ShieldAlert className="w-6 h-6 text-text_secondary" />
            <p className="font-display text-[20px]">Live Production Mode</p>
          </div>
          <div className="h-px bg-surface_border/30 mb-6" />
          <button
            type="button"
            onClick={handleLiveConnect}
            disabled={isConnectingLive || !connection?.connected}
            className="w-full btn-primary mt-2 flex items-center justify-center gap-2"
          >
            <RefreshCw size={15} className={isConnectingLive ? "animate-spin" : ""} />
            {isConnectingLive ? "Syncing live payout ledger..." : "Sync live payout ledger"}
          </button>
          {syncResult && (
            <p className="text-[12px] text-text_primary/60 mt-4 text-center">
              Pulled {syncResult.fetched} payouts. {syncResult.imported_or_updated} are now available to FIRST HOUR.
            </p>
          )}
          {!connection?.connected && (
            <p className="text-[12px] text-text_primary/45 mt-6 text-center">
              No live RazorpayX integration is configured on this deployment. FIRST HOUR will not fabricate a connection.
            </p>
          )}
        </div>
      ) : (
        !error && (
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

          <div className="h-px bg-surface_border/30 mb-6" />

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
                <span className={i < revealed ? "text-text_primary" : "text-text_primary/30"}>{scope}</span>
              </li>
            ))}
          </ul>

          <p className="text-[12px] text-text_primary/45 mt-6">
            FIRST HOUR is read-only in this demo. Workspace: Demo / Sandbox &mdash; not a live
            production connection.
          </p>
        </div>
        )
      )}

      {!isProduction && (
        <button
          className="btn-primary"
          disabled={error !== null || revealed < SCOPES.length}
          onClick={() => navigate("/evidence")}
        >
          Continue to evidence
        </button>
      )}

      <StepFooter current="/connect" />
    </div>
  );
}

