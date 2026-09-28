import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowRight, Building2, CreditCard, ShieldCheck } from "lucide-react";
import { StepFooter } from "../components/AppShell";

export default function DemoSetup() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    business: "Arrow Industries",
    holder: "Arrow Industries Pvt. Ltd.",
    bank: "Demo Bank",
    account: "001234567890",
    ifsc: "DEMO0001234",
  });

  const update = (key: keyof typeof form, value: string) =>
    setForm((current) => ({ ...current, [key]: value }));

  const start = (e: React.FormEvent) => {
    e.preventDefault();
    sessionStorage.setItem("primhora_demo_account", JSON.stringify(form));
    navigate("/connect?mode=demo");
  };

  return (
    <div className="max-w-canvas mx-auto px-6 sm:px-10 py-14">
      <div className="max-w-[760px] mb-10">
        <p className="label-eyebrow mb-4">Demo setup · 01</p>
        <h1 className="font-display text-[38px] sm:text-[52px] leading-[1.02] mb-5">
          Give Primhora a financial account to work with.
        </h1>
        <p className="text-[16px] leading-relaxed text-text_primary/65 max-w-[620px]">
          This creates a private, fictional workspace for the demonstration. Nothing is sent to a bank,
          payment gateway, or external financial network.
        </p>
      </div>

      <div className="grid lg:grid-cols-[1fr_360px] gap-8 items-start">
        <form onSubmit={start} className="paper-card p-7 sm:p-9">
          <div className="flex items-center gap-3 mb-7">
            <div className="w-10 h-10 rounded-xl bg-forest/5 border border-forest/10 flex items-center justify-center">
              <Building2 size={18} />
            </div>
            <div>
              <p className="font-display text-[19px]">Business workspace</p>
              <p className="text-[12px] text-text_primary/45">Use fictional details for the demo.</p>
            </div>
          </div>

          <div className="grid sm:grid-cols-2 gap-5">
            {[
              ["business", "Business name"],
              ["holder", "Account holder"],
              ["bank", "Bank / institution"],
              ["account", "Account number"],
              ["ifsc", "IFSC / routing code"],
            ].map(([key, label], i) => (
              <label key={key} className={i === 0 ? "sm:col-span-2" : ""}>
                <span className="label-eyebrow block mb-2">{label}</span>
                <input
                  value={form[key as keyof typeof form]}
                  onChange={(e) => update(key as keyof typeof form, e.target.value)}
                  required
                  className="w-full bg-graphite border border-forest/15 rounded-lg px-4 py-3 text-[14px] outline-none focus:border-gold/60"
                />
              </label>
            ))}
          </div>

          <div className="mt-7 p-4 rounded-xl bg-gold/5 border border-gold/15 flex gap-3">
            <ShieldCheck size={17} className="shrink-0 mt-0.5 text-text_secondary" />
            <p className="text-[12px] leading-relaxed text-text_primary/55">
              Demo only. Primhora does not validate or connect this account. Do not enter real banking
              credentials here.
            </p>
          </div>

          <button className="btn-primary mt-7 inline-flex items-center gap-2" type="submit">
            Enter the Primhora demo <ArrowRight size={15} />
          </button>
        </form>

        <aside className="paper-card p-7">
          <CreditCard size={20} className="mb-5 text-text_secondary" />
          <p className="label-eyebrow mb-3">What happens next</p>
          <ol className="space-y-5">
            {[
              ["01", "Connect", "Primhora establishes the simulated financial workspace."],
              ["02", "Investigate", "A synthetic payment incident appears and the system builds the case."],
              ["03", "Recover", "Evidence, human review and a simulated recovery command complete the loop."],
            ].map(([n, title, copy]) => (
              <li key={n} className="flex gap-4">
                <span className="font-label text-[11px] text-text_primary/30 pt-1">{n}</span>
                <div>
                  <p className="font-display text-[16px] mb-1">{title}</p>
                  <p className="text-[12px] leading-relaxed text-text_primary/50">{copy}</p>
                </div>
              </li>
            ))}
          </ol>
        </aside>
      </div>

      <StepFooter current="/connect" />
    </div>
  );
}
