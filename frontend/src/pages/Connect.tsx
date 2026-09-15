import React, { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { Check, Key, ShieldAlert } from "lucide-react";
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
    () => isProduction ? Promise.resolve(null) : api.getMerchantConnection(merchantId),
    [merchantId, isProduction]
  );
  
  const [revealed, setRevealed] = useState(0);
  const [apiKey, setApiKey] = useState("");
  const [isConnectingLive, setIsConnectingLive] = useState(false);

  useEffect(() => {
    if (isProduction) return;
    if (!connection) return;
    const timer = setInterval(() => {
      setRevealed((r) => (r < SCOPES.length ? r + 1 : r));
    }, 220);
    return () => clearInterval(timer);
  }, [connection, isProduction]);

  const handleLiveConnect = (e: React.FormEvent) => {
    e.preventDefault();
    if (!apiKey) return;
    setIsConnectingLive(true);
    // Simulate connection failure because this sandbox doesn't have live API keys yet
    setTimeout(() => {
      setIsConnectingLive(false);
      alert("Error: Live gateway connection requires the GatewayAdapter abstraction to be deployed. No mock data is loaded in this environment.");
    }, 1500);
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

      {error && !isProduction && <ErrorBanner message={error} onRetry={reload} />}

      {isProduction ? (
        <div className="paper-card max-w-[520px] px-8 py-8 mb-10 border-gold/30 shadow-lg">
          <div className="flex items-center gap-3 mb-6">
            <ShieldAlert className="w-6 h-6 text-text_secondary" />
            <p className="font-display text-[20px]">Live Production Mode</p>
          </div>
          <div className="h-px bg-surface_border/30 mb-6" />
          <form onSubmit={handleLiveConnect} className="space-y-4">
            <div>
              <label className="block text-[13px] font-ui text-text_primary/70 mb-2">
                Gateway Read-Only API Key (Stripe / Razorpay)
              </label>
              <div className="relative">
                <Key className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text_primary/40" />
                <input 
                  type="password" 
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder="rk_live_..."
                  className="w-full bg-transparent border border-forest/20 rounded-xl py-3 pl-10 pr-4 text-[14px] focus:outline-none focus:border-gold focus:ring-1 focus:ring-gold"
                />
              </div>
            </div>
            <button 
              type="submit"
              disabled={isConnectingLive || !apiKey}
              className="w-full btn-primary mt-2"
            >
              {isConnectingLive ? "Syncing Ledger..." : "Connect Gateway"}
            </button>
          </form>
          <p className="text-[12px] text-text_primary/45 mt-6 text-center">
            You are in the production environment. Mock data has been strictly disabled.
          </p>
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

