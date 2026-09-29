import React from "react";
import { Link } from "react-router-dom";
import { ShieldCheck, UserRound, LockKeyhole, ArrowRight } from "lucide-react";

export default function SAASTeam() {
 const workspace=sessionStorage.getItem("primhora_workspace");
 const roles=[[ "ANALYST","View cases and evidence",UserRound ],[ "INVESTIGATOR","Investigate and recommend",ShieldCheck ],[ "APPROVER","Review and approve recovery",LockKeyhole ]];
 return <div className="min-h-[calc(100vh-56px)] bg-graphite text-text_primary"><div className="max-w-canvas mx-auto px-6 sm:px-10 py-10">
  <p className="label-eyebrow text-text_primary/35">Administration · Team</p><h1 className="font-display text-4xl mt-2">Controls & separation of duties</h1>
  <p className="text-sm text-text_primary/45 mt-2 max-w-2xl">Define who can investigate, recommend and approve recovery actions. A new workspace starts without members or seeded customer roles.</p>
  {!workspace ? <div className="mt-8 rounded-2xl border border-surface_border bg-surface p-10 max-w-2xl"><ShieldCheck size={20}/><h2 className="font-display text-2xl mt-6">Create your organization first</h2><p className="text-sm leading-relaxed text-text_primary/45 mt-2">Team membership belongs to an organization. Create the workspace before inviting or assigning people.</p><Link to="/app" className="inline-flex items-center gap-2 mt-6 rounded-xl bg-text_primary text-graphite px-5 py-3 text-sm font-medium">Set up workspace <ArrowRight size={14}/></Link></div> :
  <><div className="grid md:grid-cols-3 gap-4 mt-8">{roles.map(([role,copy,Icon]:any)=><div key={role} className="rounded-2xl border border-surface_border bg-surface p-6"><Icon size={18}/><p className="font-ui text-sm mt-8">{role}</p><p className="text-xs text-text_primary/45 mt-2">{copy}</p><span className="inline-flex items-center gap-2 text-[11px] text-text_primary/30 mt-5">No member assigned</span></div>)}</div>
   <div className="mt-6 rounded-2xl border border-amber/20 bg-amber/5 p-5 text-sm text-text_primary/65">Live SSO, customer provisioning and MFA are identity-layer integrations for a production rollout. This workspace currently demonstrates the role model without claiming those controls are deployed.</div></>}
 </div></div>;
}