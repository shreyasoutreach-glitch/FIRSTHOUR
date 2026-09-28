import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Check, ArrowRight, Landmark, ShieldCheck } from "lucide-react";
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
    () => api.getMerchantConnection(merchantId), [merchantId]
  );
  const [revealed, setRevealed] = useState(0);
  const [account, setAccount] = useState<any>(null);

  useEffect(() => {
    try { setAccount(JSON.parse(sessionStorage.getItem("primhora_demo_account") || "null")); } catch {}
  }, []);

  useEffect(() => {
    if (!connection) return;
    const timer = setInterval(() => setRevealed((r) => r < SCOPES.length ? r + 1 : r), 180);
    return () => clearInterval(timer);
  }, [connection]);

  return (
    <div className="max-w-canvas mx-auto px-6 sm:px-10 py-14">
      <div className="max-w-[720px] mb-10">
        <p className="label-eyebrow mb-4">Demo · 02 · Financial workspace</p>
        <h1 className="font-display text-[38px] sm:text-[50px] leading-[1.02] mb-5">
          The financial record is ready.
        </h1>
        <p className="text-[16px] leading-relaxed text-text_primary/65 max-w-[620px]">
          In a real deployment this layer would be connected to an authorized financial data provider.
          For now, Primhora uses a synthetic ledger so you can experience the complete incident-response workflow.
        </p>
      </div>

      {error && <ErrorBanner message={error} onRetry={reload} />}

      {!error && (
        <div className="grid lg:grid-cols-[1fr_360px] gap-8 items-start">
          <div className="paper-card px-8 py-8">
            <div className="flex items-center justify-between mb-7">
              <div>
                <p className="label-eyebrow mb-1">Synthetic workspace</p>
                <p className="font-display text-[22px]">{loading ? "Loading…" : account?.business || connection?.merchant_name || "Demo business"}</p>
              </div>
              <span className="text-[11px] font-ui uppercase tracking-wide text-emerald border border-emerald/40 rounded-full px-2.5 py-1">SIMULATED</span>
            </div>

            <div className="h-px bg-surface_border/30 mb-6" />
            <p className="label-eyebrow mb-3">Available signals</p>
            <ul className="space-y-3">
              {SCOPES.map((scope, i) => (
                <li key={scope} className="flex items-center gap-3 text-[14px] font-ui">
                  <span className={`flex items-center justify-center w-5 h-5 rounded-full border ${i < revealed ? "bg-emerald/10 border-emerald text-emerald" : "border-forest/20 text-transparent"}`}>
                    <Check size={13} strokeWidth={2.5} />
                  </span>
                  <span className={i < revealed ? "text-text_primary" : "text-text_primary/30"}>{scope}</span>
                </li>
              ))}
            </ul>

            <div className="mt-7 p-4 rounded-xl bg-gold/5 border border-gold/15 flex gap-3">
              <ShieldCheck size={17} className="shrink-0 mt-0.5 text-text_secondary" />
              <p className="text-[12px] leading-relaxed text-text_primary/55">
                No live payment provider is connected. Every transaction, balance and recovery action in this experience is synthetic.
              </p>
            </div>

            <button className="btn-primary mt-7 inline-flex items-center gap-2" disabled={revealed < SCOPES.length}
              onClick={() => navigate("/evidence")}>
              Start the incident investigation <ArrowRight size={15} />
            </button>
          </div>

          <aside className="paper-card px-6 py-6">
            <Landmark size={20} className="mb-5 text-text_secondary" />
            <p className="label-eyebrow mb-3">Bank account on file</p>
            {account ? (
              <>
                <p className="font-display text-[18px] mb-1">{account.bank}</p>
                <p className="text-[13px] text-text_primary/55 mb-5">{account.holder}</p>
                <div className="space-y-3 text-[12px]">
                  <div className="flex justify-between"><span className="text-text_primary/40">Account</span><span>•••• {String(account.account).slice(-4)}</span></div>
                  <div className="flex justify-between"><span className="text-text_primary/40">IFSC / routing</span><span>{account.ifsc}</span></div>
                </div>
              </>
            ) : (
              <p className="text-[13px] text-text_primary/50">No demo account details entered.</p>
            )}
            <p className="text-[11px] leading-relaxed text-text_primary/35 mt-6">
              Stored only in this browser session for the demo UI. Primhora does not verify, transmit, or use these details to move money.
            </p>
          </aside>
        </div>
      )}

      <StepFooter current="/connect" />
    </div>
  );
}