import React from "react";
import { Link } from "react-router-dom";
import { Database, UploadCloud, ShieldCheck, ArrowRight } from "lucide-react";

export default function SaaSDataSources(){
 const workspace=sessionStorage.getItem("primhora_workspace");
 return <div className="min-h-[calc(100vh-56px)] bg-graphite text-text_primary"><div className="max-w-canvas mx-auto px-6 sm:px-10 py-10">
  <p className="label-eyebrow text-text_primary/35">Workspace · Data sources</p><h1 className="font-display text-4xl mt-2">Financial data</h1>
  <p className="text-sm text-text_primary/45 mt-2 max-w-2xl">Connect authorized financial records to your organization. Primhora does not claim a live provider connection until one has actually been configured.</p>
  {!workspace ? <div className="mt-8 rounded-2xl border border-surface_border bg-surface p-10 max-w-2xl"><Database size={20}/><h2 className="font-display text-2xl mt-6">Create your organization first</h2><p className="text-sm leading-relaxed text-text_primary/45 mt-2">This new workspace has no organization or data sources yet. Once you create one, you can begin connecting authorized records.</p><Link to="/app" className="inline-flex items-center gap-2 mt-6 rounded-xl bg-text_primary text-graphite px-5 py-3 text-sm font-medium">Set up workspace <ArrowRight size={14}/></Link></div> :
  <><div className="grid lg:grid-cols-2 gap-5 mt-8">
   <Source title="Payment provider" status="NOT CONNECTED" copy="No live payment provider credentials are configured for this workspace. Primhora will only show CONNECTED after an authorized integration is actually established." icon={ShieldCheck}/>
   <Source title="Bank / ledger import" status="READY" copy="Import authorized CSV or ledger records for your organization. Imported records become workspace data, not demo data." icon={UploadCloud}/>
  </div>
  <div className="mt-6 rounded-2xl border border-surface_border bg-surface p-6"><p className="label-eyebrow text-text_primary/35">Workspace state</p><p className="font-display text-xl mt-3">{workspace}</p><p className="text-xs text-text_primary/40 mt-2">No sources connected yet. No incidents will be generated until financial data is available.</p></div></>}
 </div></div>;
}
function Source({title,status,copy,icon:Icon}:any){return <div className="rounded-2xl border border-surface_border bg-surface p-6"><div className="flex justify-between"><Icon size={20}/><span className="text-[10px] rounded-full border border-surface_border text-text_primary/45 px-2.5 py-1">{status}</span></div><h2 className="font-display text-xl mt-10">{title}</h2><p className="text-sm leading-relaxed text-text_primary/50 mt-2">{copy}</p></div>}