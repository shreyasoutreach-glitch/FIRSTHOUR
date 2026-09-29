import React from "react";
import { Link } from "react-router-dom";
import { ArrowLeft, ShieldCheck } from "lucide-react";

export default function SaaSIncidents(){
 return <div className="min-h-[calc(100vh-64px)] bg-graphite text-text_primary"><div className="max-w-canvas mx-auto px-6 sm:px-10 py-10">
  <Link to="/app" className="text-xs text-text_primary/40 hover:text-text_primary">← Workspace</Link>
  <div className="mt-8 max-w-2xl"><p className="label-eyebrow text-text_primary/35">OPERATIONS · INCIDENTS</p><h1 className="font-display text-4xl mt-2">Incident queue</h1><p className="text-sm leading-relaxed text-text_primary/45 mt-3">Real incidents will appear here after your organization connects its authorized financial data.</p></div>
  <div className="mt-8 rounded-2xl border border-surface_border bg-surface p-12 text-center"><div className="mx-auto w-11 h-11 rounded-full border border-surface_border flex items-center justify-center"><ShieldCheck size={18}/></div><h2 className="font-display text-2xl mt-6">No incidents yet</h2><p className="text-sm text-text_primary/40 max-w-md mx-auto mt-2">That's expected for a new workspace. Primhora will create a case when connected data reveals an anomaly that requires investigation.</p><Link to="/demo/setup" className="inline-flex items-center gap-2 mt-7 rounded-xl border border-surface_border px-5 py-3 text-sm hover:bg-surface_raised transition">See a simulated incident <ArrowLeft size={14}/></Link></div>
 </div></div>;
}