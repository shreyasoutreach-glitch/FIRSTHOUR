import React, { useRef, useState } from "react";
import { Link } from "react-router-dom";
import { Database, UploadCloud, ShieldCheck, ArrowRight, FileCheck2, X } from "lucide-react";
import { api, hasAccessTokenProvider } from "../lib/api";

export default function SaaSDataSources(){
 const workspace=sessionStorage.getItem("primhora_workspace");
 const [file,setFile]=useState<File|null>(null);
 const [preview,setPreview]=useState<{rows:number,columns:string[]}|null>(null);
 const [importing,setImporting]=useState(false);
 const [importResult,setImportResult]=useState<any>(null);
 const [importError,setImportError]=useState<string|null>(null);
 const [merchantName,setMerchantName]=useState(()=>sessionStorage.getItem("primhora_last_merchant")||workspace||"");
 const inputRef=useRef<HTMLInputElement>(null);

 const inspect=(next:File|null)=>{
   setFile(next); setPreview(null);
   if(!next) return;
   if(!next.name.toLowerCase().endsWith(".csv")) return;
   const reader=new FileReader();
   reader.onload=()=>{const text=String(reader.result||"");const lines=text.split(/\r?
/).filter(Boolean);const columns=(lines[0]||"").split(",").map(x=>x.trim()).filter(Boolean);setPreview({rows:Math.max(0,lines.length-1),columns});};
   reader.readAsText(next.slice(0,1024*1024));
 };

 return <div className="min-h-[calc(100vh-56px)] bg-graphite text-text_primary"><div className="max-w-canvas mx-auto px-5 sm:px-10 py-10">
  <p className="label-eyebrow text-text_primary/35">Workspace · Data sources</p><h1 className="font-display text-4xl mt-2">Financial data</h1>
  <p className="text-sm text-text_primary/45 mt-2 max-w-2xl">Primhora separates data provenance from analysis. A source is only marked connected after the backend has actually accepted and validated it.</p>
  {!workspace ? <div className="mt-8 panel p-10 max-w-2xl"><Database size={20}/><h2 className="font-display text-2xl mt-6">Create your organization first</h2><p className="text-sm leading-relaxed text-text_primary/45 mt-2">Your workspace has no organization or data sources yet.</p><Link to="/app" className="inline-flex items-center gap-2 mt-6 rounded-xl bg-text_primary text-graphite px-5 py-3 text-sm font-medium">Set up workspace <ArrowRight size={14}/></Link></div> :
  <div className="mt-8 space-y-5">
   <div className="grid lg:grid-cols-2 gap-5">
    <Source title="Payment provider" status="NOT CONNECTED" copy="No live provider credentials are configured. Primhora will only show CONNECTED after an authorized backend connection has been verified." icon={ShieldCheck}/>
    <div className="panel p-6"><div className="flex justify-between"><UploadCloud size={20}/><span className="status-pill border-amber/25 text-amber/70">FILE IMPORT</span></div><h2 className="font-display text-xl mt-8">Ledger import</h2><p className="text-sm leading-relaxed text-text_primary/50 mt-2">Inspect a CSV locally first, then explicitly import it into this authorized workspace. The backend validates and records the accepted rows as read-only financial evidence.</p>
      <label className="block text-xs text-text_primary/50 mt-5">Merchant / business in this ledger<input value={merchantName} onChange={e=>setMerchantName(e.target.value)} placeholder="Arrow Industries" className="mt-2 w-full rounded-xl border border-surface_border bg-graphite px-3 py-3 text-sm focus-ring"/></label>
      <input ref={inputRef} type="file" accept=".csv,text/csv" className="hidden" onChange={e=>inspect(e.target.files?.[0]||null)}/>
      <button onClick={()=>inputRef.current?.click()} className="mt-5 inline-flex items-center gap-2 rounded-lg border border-surface_border px-4 py-2.5 text-sm hover:bg-surface_raised">{file?<FileCheck2 size={15}/>:<UploadCloud size={15}/>} {file?"Inspect another CSV":"Inspect CSV"}</button>{file&&preview&&<button disabled={importing||!hasAccessTokenProvider()} onClick={async()=>{setImporting(true);setImportError(null);setImportResult(null);try{const result=await api.importPayoutCsv(file,merchantName.trim());setImportResult(result);sessionStorage.setItem("primhora_last_merchant",result.merchant_name||merchantName.trim());const next=Math.max(1,Number(sessionStorage.getItem("primhora_connected_sources")||0)+1);sessionStorage.setItem("primhora_connected_sources",String(next))}catch(e:any){setImportError(e.message||"Import failed")}finally{setImporting(false)}}} className="mt-3 ml-2 inline-flex items-center gap-2 rounded-lg bg-text_primary text-graphite px-4 py-2.5 text-sm disabled:opacity-40">{importing?"Importing...":"Import to authorized workspace"}</button>}
      {file&&<div className="mt-4 rounded-xl border border-surface_border bg-graphite/60 p-4"><div className="flex justify-between gap-4"><div><p className="text-sm">{file.name}</p><p className="text-[11px] text-text_primary/35 mt-1">{(file.size/1024).toFixed(1)} KB · preview only</p></div><button aria-label="Clear file" onClick={()=>{setFile(null);setPreview(null)}} className="text-text_primary/35 hover:text-text_primary"><X size={14}/></button></div>{preview?<><p className="text-xs text-text_primary/55 mt-4">{preview.rows.toLocaleString()} data rows detected.</p><div className="flex flex-wrap gap-1.5 mt-2">{preview.columns.slice(0,8).map(c=><span key={c} className="status-pill border-surface_border text-text_primary/45 normal-case tracking-normal">{c}</span>)}</div></>:<p className="text-xs text-amber/70 mt-3">CSV preview unavailable. The file has not been uploaded.</p>}</div>}
    </div>
   </div>
   <div className="panel p-6"><p className="label-eyebrow text-text_primary/35">Workspace state</p><p className="font-display text-xl mt-3">{workspace}</p><div className="flex items-center gap-2 mt-3 text-xs text-text_primary/40"><span className={"w-1.5 h-1.5 rounded-full "+(importResult?"bg-emerald":"bg-text_primary/30")}/>{importResult?"CSV source connected":"No connected sources"}</div>{importResult&&<p className="text-xs text-emerald/70 mt-2">{importResult.imported_rows} row(s) imported. {importResult.incident_count} incident(s) created.</p>}<p className="text-xs text-text_primary/35 mt-2">Incidents are generated only from data accepted by the backend.</p></div>
  </div>}
 </div></div>;
}
function Source({title,status,copy,icon:Icon}:any){return <div className="panel p-6"><div className="flex justify-between"><Icon size={20}/><span className="status-pill border-surface_border text-text_primary/45">{status}</span></div><h2 className="font-display text-xl mt-8">{title}</h2><p className="text-sm leading-relaxed text-text_primary/50 mt-2">{copy}</p></div>}