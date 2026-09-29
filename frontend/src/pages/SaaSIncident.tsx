import React from "react";
import { Link } from "react-router-dom";
import { ShieldCheck } from "lucide-react";

export default function SaaSIncident(){
 return <div className="min-h-[calc(100vh-64px)] bg-graphite text-text_primary"><div className="max-w-canvas mx-auto px-6 sm:px-10 py-16">
  <div className="rounded-2xl border border-surface_border bg-surface p-10 max-w-2xl">
   <ShieldCheck size={20}/>
   <p className="label-eyebrow text-text_primary/35 mt-6">OPERATIONS · CASES</p>
   <h1 className="font-display text-3xl mt-2">No workspace case exists yet.</h1>
   <p className="text-sm leading-relaxed text-text_primary/45 mt-3">This workspace does not have connected financial data, so there are no customer incidents to open. The seeded incident used in the product demonstration is intentionally kept inside the demo.</p>
   <div className="flex flex-wrap gap-3 mt-7"><Link to="/app" className="rounded-xl bg-text_primary text-graphite px-5 py-3 text-sm font-medium">Return to workspace</Link><Link to="/demo/setup" className="rounded-xl border border-surface_border px-5 py-3 text-sm">Open synthetic demo</Link></div>
  </div>
 </div></div>;
}