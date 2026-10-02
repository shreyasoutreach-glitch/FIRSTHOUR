import React from "react";
import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import {
  ArrowRight, Activity, AlertTriangle, CheckCircle2, Database,
  Fingerprint, GitBranch, Play, ShieldCheck, Sparkles, Terminal,
  TimerReset, Workflow
} from "lucide-react";

const signalRows = [
  { label: "PAYOUT", value: "₹18.42L", note: "recipient cluster", tone: "hot" },
  { label: "LEDGER", value: "11 events", note: "03:14 → 03:19", tone: "warm" },
  { label: "EVIDENCE", value: "7 artifacts", note: "6 verified", tone: "good" },
];

const steps = [
  ["01", "Detect", "Surface the break before the trail goes cold.", Activity],
  ["02", "Reconstruct", "Turn scattered records into one deterministic timeline.", GitBranch],
  ["03", "Decide", "Keep humans in control of every material action.", ShieldCheck],
];

export default function Welcome() {
  return (
    <div className="relative overflow-hidden bg-text_primary text-graphite">
      <div className="landing-noise" />
      <div className="landing-grid" />
      <div className="landing-orb landing-orb-one" />
      <div className="landing-orb landing-orb-two" />

      <section className="relative mx-auto max-w-canvas px-6 pb-20 pt-16 sm:px-10 sm:pb-28 sm:pt-24">
        <div className="grid gap-12 lg:grid-cols-[1.08fr_.92fr] lg:items-center">
          <div>
            <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.65 }}
              className="inline-flex items-center gap-2 rounded-full border border-graphite/10 bg-white/55 px-3 py-1.5 backdrop-blur">
              <span className="landing-pulse-dot" />
              <span className="label-eyebrow text-graphite/55">PRIMHORA / FINANCIAL INCIDENT INTELLIGENCE</span>
            </motion.div>

            <motion.h1 initial={{ opacity: 0, y: 22 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.08, duration: 0.75 }}
              className="mt-7 max-w-[980px] font-display text-[58px] leading-[0.88] tracking-[-0.055em] sm:text-[88px]">
              Money moved.
              <br />
              <span className="landing-word-emphasis">Now reconstruct why.</span>
            </motion.h1>

            <motion.p initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.16, duration: 0.7 }}
              className="mt-8 max-w-[700px] text-[18px] leading-relaxed text-graphite/58 sm:text-[20px]">
              PRIMHORA converts fractured payment evidence into a source-backed incident record,
              so your team can see what happened, what can be proven, what is exposed, and what
              still needs a human answer.
            </motion.p>

            <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.24, duration: 0.65 }}
              className="mt-9 flex flex-wrap gap-3">
              <Link to="/demo/setup" className="landing-cta landing-cta-dark"><Play size={15} /> Run the synthetic case <ArrowRight size={15} /></Link>
              <Link to="/app" className="landing-cta landing-cta-light">Open workspace <ArrowRight size={15} /></Link>
            </motion.div>

            <div className="mt-10 flex flex-wrap items-center gap-x-7 gap-y-3 text-[11px] text-graphite/40">
              <span className="inline-flex items-center gap-2"><ShieldCheck size={13} /> Human approval stays in the loop</span>
              <span>Deterministic financial truth</span>
              <span>Read-only by design</span>
            </div>
          </div>

          <motion.div initial={{ opacity: 0, scale: 0.97, y: 16 }} animate={{ opacity: 1, scale: 1, y: 0 }}
            transition={{ delay: 0.18, duration: 0.85 }} className="relative min-h-[500px]">
            <div className="landing-console absolute inset-0">
              <div className="flex items-center justify-between border-b border-white/10 px-5 py-4">
                <div className="flex items-center gap-3">
                  <div className="flex gap-1.5"><span className="h-2 w-2 rounded-full bg-white/15" /><span className="h-2 w-2 rounded-full bg-white/10" /><span className="h-2 w-2 rounded-full bg-white/10" /></div>
                  <span className="font-label text-[9px] uppercase tracking-[0.18em] text-white/38">Live reconstruction</span>
                </div>
                <span className="status-pill border-white/10 text-white/45">Read-only</span>
              </div>

              <div className="grid gap-4 p-5 sm:p-6">
                <div className="grid gap-3 sm:grid-cols-3">
                  {signalRows.map((row, i) => (
                    <motion.div key={row.label} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.45 + i * 0.1, duration: 0.45 }} className="landing-mini-card">
                      <div className="flex items-center justify-between">
                        <span className="font-label text-[9px] tracking-[0.16em] text-white/28">{row.label}</span>
                        <span className={row.tone === "good" ? "landing-tone-good" : row.tone === "hot" ? "landing-tone-hot" : "landing-tone-warm"} />
                      </div>
                      <p className="mt-3 font-display text-[25px] text-white/92">{row.value}</p>
                      <p className="mt-1 text-[10px] text-white/30">{row.note}</p>
                    </motion.div>
                  ))}
                </div>

                <div className="landing-graph-card">
                  <div className="flex items-center justify-between">
                    <div><p className="font-label text-[9px] uppercase tracking-[0.18em] text-white/30">Incident graph</p><p className="mt-1 text-xs text-white/55">Entity correlation + evidence chain</p></div>
                    <span className="inline-flex items-center gap-1.5 rounded-full border border-emerald-400/15 bg-emerald-400/[0.05] px-2.5 py-1 font-label text-[9px] text-emerald-300/80"><CheckCircle2 size={11} /> VERIFIED</span>
                  </div>

                  <div className="relative mt-6 h-[220px] overflow-hidden rounded-xl border border-white/[0.06] bg-black/10">
                    <div className="absolute inset-x-8 top-1/2 h-px bg-white/8" />
                    <div className="absolute left-[15%] top-[28%] h-px w-[35%] rotate-[17deg] bg-white/18" />
                    <div className="absolute right-[15%] top-[54%] h-px w-[34%] -rotate-[22deg] bg-white/18" />
                    <div className="absolute left-[32%] top-[31%] h-[110px] w-px rotate-[10deg] bg-white/8" />
                    <div className="absolute left-[67%] top-[38%] h-[94px] w-px -rotate-[14deg] bg-white/8" />

                    {[
                      ["origin", "18%", "50%", "PAYMENT"], ["event", "44%", "30%", "LEDGER"],
                      ["entity", "70%", "58%", "ENTITY"], ["evidence", "84%", "27%", "EVIDENCE"],
                    ].map(([key, left, top, label], i) => (
                      <motion.div key={key} animate={{ y: [0, -5, 0], opacity: [0.72, 1, 0.72] }}
                        transition={{ duration: 3.2 + i * 0.35, repeat: Infinity, ease: "easeInOut", delay: i * 0.35 }}
                        className="absolute" style={{ left, top }}>
                        <div className="relative flex h-12 w-12 items-center justify-center rounded-2xl border border-white/14 bg-white/[0.055] shadow-[0_0_32px_rgba(255,255,255,.05)]">
                          <span className="h-2.5 w-2.5 rounded-full bg-white/78 shadow-[0_0_18px_rgba(255,255,255,.25)]" />
                          <span className="absolute -bottom-5 whitespace-nowrap font-label text-[8px] tracking-[0.14em] text-white/25">{label}</span>
                        </div>
                      </motion.div>
                    ))}

                    <motion.div animate={{ x: ["-10%", "110%"] }} transition={{ duration: 4.6, repeat: Infinity, ease: "linear" }}
                      className="absolute inset-y-0 w-[22%] bg-gradient-to-r from-transparent via-white/[0.055] to-transparent blur-xl" />
                  </div>
                </div>

                <div className="grid gap-3 sm:grid-cols-[1.1fr_.9fr]">
                  <div className="landing-log-card">
                    <div className="flex items-center gap-2 text-white/35"><Terminal size={12} /><span className="font-label text-[9px] tracking-[0.16em]">TRACE</span></div>
                    <div className="mt-4 space-y-2 font-mono text-[10px] text-white/42">
                      <p><span className="text-white/20">03:14:22</span> payout.created <span className="text-white/22">#PX-1842</span></p>
                      <p><span className="text-white/20">03:16:08</span> recipient.clustered <span className="text-white/22">+4</span></p>
                      <p><span className="text-white/20">03:19:41</span> evidence.verified <span className="text-emerald-300/65">true</span></p>
                    </div>
                  </div>
                  <div className="landing-recovery-card">
                    <div className="flex items-center justify-between"><span className="font-label text-[9px] tracking-[0.16em] text-white/28">NEXT</span><TimerReset size={13} className="text-white/25" /></div>
                    <p className="mt-3 font-display text-[22px] text-white/85">Human review</p>
                    <p className="mt-1 text-[10px] leading-relaxed text-white/28">Recovery stays blocked until an authorized person decides.</p>
                  </div>
                </div>
              </div>
            </div>

            <motion.div animate={{ y: [0, 8, 0], rotate: [0, 1.2, 0] }} transition={{ duration: 7, repeat: Infinity, ease: "easeInOut" }}
              className="absolute -bottom-6 -left-4 hidden rounded-2xl border border-graphite/10 bg-white/80 p-4 shadow-2xl backdrop-blur-md sm:block">
              <div className="flex items-center gap-3"><div className="flex h-9 w-9 items-center justify-center rounded-xl border border-graphite/10 bg-white"><Workflow size={15} /></div><div><p className="text-[11px] font-medium">Evidence chain intact</p><p className="mt-1 text-[9px] text-graphite/40">7 artifacts · 6 verified</p></div></div>
            </motion.div>

            <motion.div animate={{ y: [0, -6, 0], rotate: [0, -1, 0] }} transition={{ duration: 6.2, repeat: Infinity, ease: "easeInOut", delay: 0.4 }}
              className="absolute -right-3 top-12 hidden rounded-2xl border border-graphite/10 bg-graphite p-4 text-text_primary shadow-2xl sm:block">
              <div className="flex items-center gap-3"><div className="flex h-9 w-9 items-center justify-center rounded-xl border border-white/10 bg-white/[0.04]"><AlertTriangle size={15} className="text-amber-300/75" /></div><div><p className="text-[11px] font-medium">Exposure identified</p><p className="mt-1 text-[9px] text-white/30">₹18.42L across 5 entities</p></div></div>
            </motion.div>
          </motion.div>
        </div>

        <div className="mt-24 grid gap-3 border-y border-graphite/10 py-5 sm:grid-cols-3">
          {steps.map(([num, title, copy, Icon], i) => {
            const StepIcon = Icon as any;
            return <motion.div key={title} initial={{ opacity: 0, y: 10 }} whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.08, duration: 0.45 }} viewport={{ once: true, margin: "-40px" }}
              className="group flex gap-4 rounded-2xl p-4 transition hover:bg-graphite/[0.025]">
              <span className="font-label pt-1 text-[10px] text-graphite/20">{num}</span>
              <div className="flex-1"><div className="flex items-center gap-2"><StepIcon size={14} className="text-graphite/45" /><p className="font-display text-[22px]">{title}</p></div><p className="mt-2 max-w-sm text-[12px] leading-relaxed text-graphite/45">{copy}</p></div>
            </motion.div>;
          })}
        </div>

        <div id="how-it-works" className="mt-24 grid gap-4 lg:grid-cols-[1.05fr_.95fr]">
          <motion.div initial={{ opacity: 0, y: 14 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="landing-principle-card">
            <div className="flex items-center gap-2 text-graphite/40"><Sparkles size={15} /><span className="label-eyebrow text-graphite/40">THE OPERATING PRINCIPLE</span></div>
            <h2 className="mt-5 max-w-2xl font-display text-[38px] leading-[0.94] tracking-tight sm:text-[52px]">AI can interpret.<br />It cannot declare truth.</h2>
            <p className="mt-6 max-w-xl text-[14px] leading-relaxed text-graphite/52">Deterministic records anchor the case. Evidence shows where the claim came from. Humans decide what matters. The system keeps the chain intact.</p>
          </motion.div>

          <div className="grid gap-4">
            {[
              [Database, "Source-backed", "Financial events stay tied to their originating records."],
              [Fingerprint, "Evidence-native", "Artifacts, hashes and verification states travel with the case."],
              [ShieldCheck, "Human-governed", "Material recovery actions remain intentionally blocked in the product."],
            ].map(([Icon, title, copy], i) => {
              const ItemIcon = Icon as any;
              return <motion.div key={title} initial={{ opacity: 0, x: 10 }} whileInView={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.08, duration: 0.45 }} viewport={{ once: true }}
                className="group rounded-2xl border border-graphite/10 bg-graphite/[0.018] p-6 transition hover:-translate-y-0.5 hover:bg-graphite/[0.03]">
                <div className="flex items-start gap-4"><div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-graphite/10 bg-white/55"><ItemIcon size={16} /></div><div><h3 className="font-display text-[23px]">{title}</h3><p className="mt-2 text-[12px] leading-relaxed text-graphite/45">{copy}</p></div></div>
              </motion.div>;
            })}
          </div>
        </div>

        <motion.div initial={{ opacity: 0, y: 14 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
          className="mt-24 flex flex-col gap-5 rounded-3xl border border-graphite/10 bg-graphite p-6 text-text_primary sm:flex-row sm:items-center sm:justify-between sm:p-8">
          <div><p className="label-eyebrow text-white/30">NEXT MOVE</p><h2 className="mt-2 font-display text-[30px] tracking-tight">See an incident rebuilt from the inside.</h2><p className="mt-2 max-w-2xl text-[12px] leading-relaxed text-white/35">Synthetic data only. No money is moved. Every recovery action in the demo is simulated.</p></div>
          <Link to="/demo/setup" className="inline-flex shrink-0 items-center justify-center gap-2 rounded-xl bg-white px-5 py-3 text-sm font-medium text-graphite transition hover:bg-white/85">Enter synthetic demo <ArrowRight size={14} /></Link>
        </motion.div>
      </section>
    </div>
  );
}
