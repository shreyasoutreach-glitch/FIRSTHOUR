import React from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowRight, Activity, Fingerprint, GitBranch, ShieldCheck, Play, Building2 } from "lucide-react";

export default function Welcome() {
  const navigate = useNavigate();
  const cards = [
    [Play, "SANDBOX · SYNTHETIC DATA", "Explore the demo", "Follow a realistic financial incident from anomaly detection through evidence, reconstruction, human decision-making, simulated recovery and audit.", "Start guided investigation", "/demo/setup", false],
    [Building2, "WORKSPACE · YOUR OPERATIONS", "Enter the workspace", "Set up your organization, connect authorized data sources, invite your team and build your own financial operations control plane.", "Open workspace", "/app", true],
  ];
  return <div className="min-h-[calc(100vh-56px)] bg-text_primary text-graphite">
    <section className="max-w-canvas mx-auto px-6 sm:px-10 pt-16 sm:pt-24 pb-20">
      <motion.div initial={{opacity:0,y:18}} animate={{opacity:1,y:0}} transition={{duration:.7}}>
        <p className="label-eyebrow text-graphite/45 mb-5 tracking-[0.2em]">FINANCIAL OPERATIONS INTELLIGENCE</p>
        <h1 className="font-display text-[54px] sm:text-[82px] leading-[0.92] tracking-[-0.04em] max-w-[980px]">When money moves wrong,<br/><span className="text-graphite/45">know why.</span></h1>
        <p className="mt-8 text-[18px] sm:text-[20px] leading-relaxed text-graphite/60 max-w-[700px]">Primhora turns messy financial incidents into traceable cases: detect the anomaly, gather evidence, reconstruct what happened, decide what to do, and verify the outcome.</p>
      </motion.div>
      <motion.div initial={{opacity:0,y:18}} animate={{opacity:1,y:0}} transition={{delay:.15,duration:.7}} className="grid md:grid-cols-2 gap-4 mt-12 max-w-[900px]">
        {cards.map(([Icon,eyebrow,title,copy,cta,path,dark]:any)=><button key={title} onClick={()=>navigate(path)} className={"group text-left rounded-2xl border p-7 transition "+(dark?"border-graphite/15 bg-graphite text-text_primary hover:bg-graphite/95":"border-graphite/15 bg-graphite/[0.035] hover:bg-graphite/[0.06]")}>
          <div className="flex items-start justify-between"><div className={"w-10 h-10 rounded-full border flex items-center justify-center "+(dark?"border-text_primary/15":"border-graphite/15")}><Icon size={16}/></div><ArrowRight size={17} className="opacity-30 group-hover:opacity-100 transition"/></div>
          <p className={"label-eyebrow mt-8 "+(dark?"text-text_primary/40":"text-graphite/40")}>{eyebrow}</p>
          <h2 className="font-display text-[28px] mt-2">{title}</h2>
          <p className={"text-sm leading-relaxed mt-3 "+(dark?"text-text_primary/50":"text-graphite/55")}>{copy}</p>
          <span className="inline-flex items-center gap-2 mt-6 text-sm font-medium">{cta} <ArrowRight size={14}/></span>
        </button>)}
      </motion.div>
      <p className="mt-5 text-[11px] text-graphite/40">Demo uses synthetic data and simulated actions. Workspace data belongs to your organization.</p>
      <div id="how-it-works" className="grid md:grid-cols-3 gap-4 mt-24">
        {[[Activity,"Detect","Surface unusual payment and payout behavior before the trail goes cold.","Find the signal."],[Fingerprint,"Explain","Connect ledger events, evidence and human context into one incident record.","Build the case."],[GitBranch,"Resolve","Create a governed recovery command with review, approval, execution and verification.","Close the loop."]].map(([Icon,title,copy,headline]:any,i)=><motion.div key={title} initial={{opacity:0,y:12}} whileInView={{opacity:1,y:0}} transition={{delay:i*.08}} viewport={{once:true}} className="border border-graphite/10 rounded-2xl p-7 bg-graphite/[0.025]"><Icon size={20} className="mb-8"/><p className="label-eyebrow text-graphite/40 mb-2">{title}</p><p className="font-display text-[22px] leading-tight mb-3">{headline}</p><p className="text-[13px] leading-relaxed text-graphite/55">{copy}</p></motion.div>)}
      </div>
      <div className="mt-16 border-t border-graphite/10 pt-8 flex flex-wrap items-center gap-x-8 gap-y-3 text-[12px] text-graphite/45"><span className="inline-flex items-center gap-2"><ShieldCheck size={14}/> Human approval stays in the loop</span><span>Evidence-backed reasoning</span><span>Full audit trail</span><span>Recovery is simulated in the demo</span></div>
    </section>
  </div>;
}