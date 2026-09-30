import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ArrowRight, Database, Users, ShieldCheck, Plus, Building2, Check } from "lucide-react";
import { api, setWorkspaceToken } from "../lib/api";

export default function SaaS(){
 const navigate=useNavigate();
 const [showForm,setShowForm]=useState(false);
 const [name,setName]=useState("");
 const [industry,setIndustry]=useState("");
 const [created,setCreated]=useState(()=>sessionStorage.getItem("primhora_workspace")||"");
 const [loading,setLoading]=useState(false);
 const [error,setError]=useState("");

 const create=async()=>{
   const value=name.trim();
   if(!value)return;
   setLoading(true);\n   setError("");\n   try {\n     const workspace=await api.createWorkspace(value, industry.trim());\n     if (workspace.token) setWorkspaceToken(workspace.token);\n     sessionStorage.setItem("primhora_workspace",workspace.name);\n     sessionStorage.setItem("primhora_workspace_id",workspace.tenant_id);
   sessionStorage.setItem("primhora_workspace_industry",workspace.industry || industry.trim());
   setCreated(value);
   setShowForm(false);
 };

 if(created) return <div className="min-h-[calc(100vh-64px)] bg-graphite text-text_primary"><div className="max-w-canvas mx-auto px-6 sm:px-10 py-10">
   <p className="label-eyebrow text-text_primary/35 mb-3">WORKSPACE · {created.toUpperCase()}</p>
   <div className="max-w-3xl"><h1 className="font-display text-5xl tracking-tight">Workspace created.</h1><p className="text-base leading-relaxed text-text_primary/50 mt-4">Your organization exists, but Primhora has no financial data yet. Connect an authorized source to begin populating the workspace.</p></div>
   <div className="mt-10 grid md:grid-cols-3 gap-4">
    <Link to="/app/data-sources" className="rounded-2xl border border-surface_border bg-surface p-6 hover:bg-surface_raised transition"><Database size={18}/><p className="font-display text-xl mt-8">Connect data</p><p className="text-xs text-text_primary/40 mt-2">Add an authorized payment, bank, ledger or file source.</p><span className="inline-flex items-center gap-2 mt-5 text-xs">Continue <ArrowRight size={13}/></span></Link>
    <Link to="/app/team" className="rounded-2xl border border-surface_border bg-surface p-6 hover:bg-surface_raised transition"><Users size={18}/><p className="font-display text-xl mt-8">Invite team</p><p className="text-xs text-text_primary/40 mt-2">Prepare roles and separation of duties.</p></Link>
    <div className="rounded-2xl border border-surface_border bg-surface p-6"><ShieldCheck size={18}/><p className="font-display text-xl mt-8">Incidents</p><p className="text-xs text-text_primary/40 mt-2">No incidents yet. They appear when connected data creates a case.</p></div>
   </div>
 </div></div>;

 return <div className="min-h-[calc(100vh-64px)] bg-graphite text-text_primary"><div className="max-w-canvas mx-auto px-6 sm:px-10 py-10">
  <div className="max-w-3xl"><p className="label-eyebrow text-text_primary/35 mb-3">WORKSPACE · FIRST RUN</p><h1 className="font-display text-5xl tracking-tight">Your financial operations workspace.</h1><p className="text-base leading-relaxed text-text_primary/50 mt-4 max-w-2xl">This is your control plane, not a pre-filled demo. Set up your organization and connect authorized financial data before Primhora begins creating incidents.</p></div>
  <div className="mt-10 grid lg:grid-cols-[1.25fr_.75fr] gap-5">
   <section className="rounded-2xl border border-surface_border bg-surface p-7">
    <div className="flex items-start justify-between gap-6"><div><p className="label-eyebrow text-text_primary/35">GET STARTED</p><h2 className="font-display text-2xl mt-2">Build your workspace</h2></div><span className="rounded-full border border-amber/25 text-amber px-3 py-1.5 text-[10px] uppercase tracking-wider">Not connected</span></div>
    <div className="mt-8 space-y-3">{[["01","Set up your organization","Company identity, operating context and workspace ownership."],["02","Connect your data","Authorized payment, bank, ledger or file sources."],["03","Invite your team","Assign analyst, investigator and approver responsibilities."],["04","Start monitoring","Incidents appear only when your connected data creates them."]].map(([n,t,c],i)=><div key={n} className="flex gap-4 rounded-xl border border-surface_border p-4"><span className="font-ui text-xs text-text_primary/30 pt-1">{n}</span><div><p className="font-medium">{t}</p><p className="text-xs text-text_primary/40 mt-1">{c}</p></div>{i===0&&<span className="ml-auto text-xs text-text_primary/35">Start here</span>}</div>)}</div>
    {showForm ? <div className="mt-7 rounded-xl border border-surface_border p-5"><p className="font-medium">Create organization</p><p className="text-xs text-text_primary/40 mt-1">This creates a local workspace for this product preview. No external account or financial connection is made.</p><label className="block text-xs text-text_primary/50 mt-5">Organization name<input autoFocus value={name} onChange={e=>setName(e.target.value)} onKeyDown={e=>e.key==="Enter"&&create()} placeholder="e.g. Northstar Finance" className="mt-2 w-full rounded-lg border border-surface_border bg-graphite px-3 py-3 text-sm outline-none focus:border-text_primary/40"/></label><label className="block text-xs text-text_primary/50 mt-4">Industry <span className="text-text_primary/25">(optional)</span><input value={industry} onChange={e=>setIndustry(e.target.value)} placeholder="e.g. Fintech" className="mt-2 w-full rounded-lg border border-surface_border bg-graphite px-3 py-3 text-sm outline-none focus:border-text_primary/40"/></label><div className="flex gap-2 mt-5"><button onClick={create} disabled={!name.trim() || loading} className="inline-flex items-center gap-2 rounded-lg bg-text_primary text-graphite px-4 py-2.5 text-sm font-medium disabled:opacity-30"><Check size={14}/> {loading ? "Creating…" : "Create workspace"}</button><button onClick={()=>setShowForm(false)} className="px-4 py-2.5 text-sm text-text_primary/50">Cancel</button></div>{error && <p className="text-xs text-red-400 mt-4">{error}</p>}</div> : <button onClick={()=>setShowForm(true)} className="mt-7 inline-flex items-center gap-2 rounded-xl bg-text_primary text-graphite px-5 py-3 text-sm font-medium hover:opacity-90 transition"><Plus size={15}/> Create organization <ArrowRight size={14}/></button>}
   </section>
   <aside className="space-y-3"><div className="rounded-2xl border border-surface_border bg-surface p-6"><Building2 size={18}/><p className="font-display text-xl mt-7">No organization yet</p><p className="text-xs leading-relaxed text-text_primary/45 mt-2">A new Primhora workspace starts empty. There are no clients, incidents or financial records here until you add them.</p></div><Link to="/demo/setup" className="block rounded-2xl border border-amber/20 bg-amber/[0.04] p-6 hover:bg-amber/[0.07] transition"><ShieldCheck size={18} className="text-amber"/><p className="font-display text-xl mt-7">Want to see it working?</p><p className="text-xs leading-relaxed text-text_primary/45 mt-2">Open the synthetic demo and investigate a complete incident without connecting anything.</p><span className="inline-flex items-center gap-2 text-xs mt-5">Explore demo <ArrowRight size={13}/></span></Link></aside>
  </div>
 </div></div>;
}