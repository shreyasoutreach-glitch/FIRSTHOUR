import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Activity, AlertTriangle, ArrowUpRight, Database, FileCheck2, ShieldCheck, Users, WalletCards } from "lucide-react";
import { api } from "../lib/api";
import { formatINR } from "../lib/format";

function Stat({label,value,sub,icon:Icon}:any){return <div className="rounded-2xl border border-surface_border bg-surface p-5"><div className="flex items-center justify-between"><span className="label-eyebrow text-text_primary/35">{label}</span><Icon size={16} className="text-text_primary/35"/></div><p className="font-display text-3xl mt-5">{value}</p><p className="text-xs text-text_primary/40 mt-1">{sub}</p></div>}

export default function SaaS(){
 const [metrics,setMetrics]=useState<any>(null); const [incidents,setIncidents]=useState<any[]>([]); const [error,setError]=useState("");
 const navigate=useNavigate();
 useEffect(()=>{Promise.all([api.getMetrics(),api.listIncidents()]).then(([m,i])=>{setMetrics(m);setIncidents(i)}).catch(e=>setError(e.message||String(e)))},[]);
 const open=incidents.filter(i=>!["RESOLVED","CLOSED"].includes(i.resolution_state||"")).length;
 return <div className="min-h-[calc(100vh-56px)] bg-graphite text-text_primary">
  <div className="max-w-canvas mx-auto px-6 sm:px-10 py-8">
   <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-5 mb-8">
    <div><p className="label-eyebrow text-text_primary/35 mb-3">Workspace · Northbridge</p><h1 className="font-display text-4xl tracking-tight">Financial operations</h1><p className="text-sm text-text_primary/50 mt-2">A working control plane for incidents, evidence and recovery.</p></div>
    <div className="flex items-center gap-2 text-xs"><span className="rounded-full border border-emerald/30 text-emerald px-3 py-1.5">WORKSPACE ACTIVE</span><span className="rounded-full border border-amber/25 text-amber px-3 py-1.5">BUYER PREVIEW</span></div>
   </div>
   {error && <div className="mb-6 rounded-xl border border-vermillion/30 bg-vermillion/5 p-4 text-sm text-vermillion">{error}</div>}
   <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-8">
    <Stat label="Open incidents" value={open} sub="requiring attention" icon={AlertTriangle}/>
    <Stat label="Transactions" value={metrics?.payouts?.toLocaleString() ?? "—"} sub="payout records" icon={Activity}/>
    <Stat label="Evidence" value={metrics?.evidence_artifacts ?? "—"} sub="artifacts retained" icon={FileCheck2}/>
    <Stat label="Audit events" value={metrics?.audit_events ?? "—"} sub="accountable actions" icon={ShieldCheck}/>
   </div>
   <div className="grid lg:grid-cols-[1fr_340px] gap-5">
    <section className="rounded-2xl border border-surface_border bg-surface">
     <div className="p-5 border-b border-surface_border flex items-center justify-between"><div><p className="label-eyebrow text-text_primary/35">Incident queue</p><h2 className="font-display text-xl mt-1">Cases requiring attention</h2></div><Link to="/app/incidents" className="text-xs text-text_primary/50 hover:text-text_primary">View all →</Link></div>
     {incidents.length===0 ? <div className="p-8 text-sm text-text_primary/40">No incidents in this workspace.</div> : <div>{incidents.slice(0,6).map((i:any)=><button key={i.id} onClick={()=>navigate("/app/incidents/"+i.id)} className="w-full text-left p-5 border-b last:border-b-0 border-surface_border hover:bg-surface_raised transition"><div className="flex items-start justify-between gap-4"><div><div className="flex items-center gap-2"><span className="font-ui text-xs text-text_primary/40">{i.id}</span><span className="text-[10px] rounded-full border border-vermillion/30 text-vermillion px-2 py-0.5">{i.severity||"OPEN"}</span></div><p className="mt-2 font-medium">{i.scenario||"Financial anomaly investigation"}</p><p className="text-xs text-text_primary/40 mt-1">{i.state}</p></div><ArrowUpRight size={16} className="text-text_primary/30"/></div></button>)}</div>}
    </section>
    <aside className="space-y-3">
      <Link to="/app/data-sources" className="block rounded-2xl border border-surface_border bg-surface p-5 hover:bg-surface_raised transition"><div className="flex justify-between"><Database size={18}/><ArrowUpRight size={15}/></div><p className="font-display text-lg mt-8">Data sources</p><p className="text-xs text-text_primary/45 mt-1">Connect or import financial records.</p></Link>
      <Link to="/app/team" className="block rounded-2xl border border-surface_border bg-surface p-5 hover:bg-surface_raised transition"><div className="flex justify-between"><Users size={18}/><ArrowUpRight size={15}/></div><p className="font-display text-lg mt-8">Team & controls</p><p className="text-xs text-text_primary/45 mt-1">Roles, approvals and separation of duties.</p></Link>
      <div className="rounded-2xl border border-surface_border bg-surface p-5"><WalletCards size={18}/><p className="font-display text-lg mt-8">Recovery operations</p><p className="text-xs text-text_primary/45 mt-1">Governed actions stay inside the case record.</p></div>
    </aside>
   </div>
  </div>
 </div>
}