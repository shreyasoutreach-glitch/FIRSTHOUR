import React from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowRight, Activity, Fingerprint, GitBranch, ShieldCheck } from "lucide-react";

export default function Welcome() {
  const navigate = useNavigate();
  return (
    <div className="min-h-[calc(100vh-56px)] bg-text_primary text-graphite">
      <section className="max-w-canvas mx-auto px-6 sm:px-10 pt-16 sm:pt-24 pb-20">
        <motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.7 }}>
          <p className="label-eyebrow text-graphite/45 mb-5 tracking-[0.2em]">FINANCIAL OPERATIONS INTELLIGENCE</p>
          <h1 className="font-display text-[54px] sm:text-[82px] leading-[0.92] tracking-[-0.04em] max-w-[980px]">
            When money moves wrong,<br /><span className="text-graphite/45">know why.</span>
          </h1>
          <p className="mt-8 text-[18px] sm:text-[20px] leading-relaxed text-graphite/60 max-w-[700px]">
            Primhora turns messy financial incidents into traceable cases: detect the anomaly,
            gather evidence, reconstruct what happened, decide what to do, and verify the outcome.
          </p>
          <div className="mt-10 flex flex-wrap gap-3">
            <button onClick={() => navigate("/demo/setup")} className="btn-primary inline-flex items-center gap-2 px-6 py-4">
              Explore the full demo <ArrowRight size={16} />
            </button>
            <a href="#how-it-works" className="btn-secondary inline-flex items-center px-6 py-4">See how it works</a>
          </div>
          <p className="mt-4 text-[11px] text-graphite/40">Synthetic data · simulated recovery · no bank or payment-gateway connection</p>
        </motion.div>

        <div id="how-it-works" className="grid md:grid-cols-3 gap-4 mt-24">
          {[
            [Activity, "Detect", "Surface unusual payment and payout behavior before the trail goes cold.", "Find the signal."],
            [Fingerprint, "Explain", "Connect ledger events, evidence and human context into one incident record.", "Build the case."],
            [GitBranch, "Resolve", "Create a governed recovery command with review, approval, execution and verification.", "Close the loop."],
          ].map(([Icon, title, copy, headline]: any, i) => (
            <motion.div key={title} initial={{ opacity: 0, y: 12 }} whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.08 }} viewport={{ once: true }}
              className="border border-graphite/10 rounded-2xl p-7 bg-graphite/[0.025]">
              <Icon size={20} className="mb-8" />
              <p className="label-eyebrow text-graphite/40 mb-2">{title}</p>
              <p className="font-display text-[22px] leading-tight mb-3">{headline}</p>
              <p className="text-[13px] leading-relaxed text-graphite/55">{copy}</p>
            </motion.div>
          ))}
        </div>

        <div className="mt-16 border-t border-graphite/10 pt-8 flex flex-wrap items-center gap-x-8 gap-y-3 text-[12px] text-graphite/45">
          <span className="inline-flex items-center gap-2"><ShieldCheck size={14} /> Human approval stays in the loop</span>
          <span>Evidence-backed reasoning</span><span>Full audit trail</span><span>Recovery is simulated in this demo</span>
        </div>
      </section>
    </div>
  );
}