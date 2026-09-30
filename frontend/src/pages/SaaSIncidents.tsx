import React from "react";
import { Link } from "react-router-dom";
import { AlertTriangle, ShieldCheck, ArrowRight } from "lucide-react";
import { api, hasAccessTokenProvider } from "../lib/api";
import { useApiData } from "../lib/useApiData";
import ErrorBanner from "../components/ErrorBanner";

export default function SaaSIncidents(){
  const workspace=sessionStorage.getItem("primhora_workspace");
  const enabled=Boolean(workspace && hasAccessTokenProvider());
  const {data: incidents,loading,error,reload}=useApiData(
    ()=>enabled ? api.listIncidents() : Promise.resolve([]),
    [enabled]
  );

  if(!workspace) return <EmptyWorkspace/>;

  return <div className="min-h-[calc(100vh-64px)] bg-graphite text-text_primary"><div className="max-w-canvas mx-auto px-6 sm:px-10 py-10">
    <p className="label-eyebrow text-text_primary/35">OPERATIONS · INCIDENTS</p>
    <div className="flex items-end justify-between gap-4 flex-wrap mt-2"><div><h1 className="font-display text-4xl">Incident queue</h1><p className="text-sm leading-relaxed text-text_primary/45 mt-3 max-w-2xl">Cases created from your organization’s authorized financial data. Demo incidents never appear here.</p></div><Link to="/app/data-sources" className="rounded-xl border border-surface_border px-4 py-2.5 text-sm">Data sources</Link></div>
    {!enabled && <div className="mt-8 panel p-6 border-amber/20"><p className="label-eyebrow text-amber/70">Production identity required</p><p className="text-sm text-text_primary/55 mt-2">This browser is still in workspace preview mode. Real incident data is only fetched after the production identity provider supplies an access token.</p></div>}
    {error&&<div className="mt-8"><ErrorBanner message={error} onRetry={reload}/></div>}
    {loading&&<p className="mt-8 text-sm text-text_primary/40">Loading incidents…</p>}
    {!loading&&!error&&enabled&&incidents?.length===0&&<div className="mt-8 rounded-2xl border border-surface_border bg-surface p-12 text-center"><ShieldCheck size={20} className="mx-auto"/><h2 className="font-display text-2xl mt-5">No incidents yet</h2><p className="text-sm text-text_primary/40 max-w-md mx-auto mt-2">Import authorized financial data and PRIMHORA will create cases when deterministic checks identify an investigation-worthy anomaly.</p></div>}
    {!loading&&!error&&enabled&&(incidents ?? []).length>0&&<div className="mt-8 space-y-3">{(incidents ?? []).map((incident:any)=><Link key={incident.id} to={`/app/incidents/${incident.id}`} className="panel p-5 flex items-center justify-between gap-5 hover:bg-surface_raised transition"><div className="flex items-start gap-4"><div className="w-9 h-9 rounded-full border border-vermillion/25 flex items-center justify-center"><AlertTriangle size={16} className="text-vermillion"/></div><div><p className="label-eyebrow text-text_primary/35">{incident.id} · {incident.state}</p><h2 className="font-display text-xl mt-1">{incident.scenario || "Financial incident"}</h2><p className="text-xs text-text_primary/40 mt-1">{incident.merchant_name}</p></div></div><ArrowRight size={16} className="text-text_primary/30"/></Link>)}</div>}
  </div></div>;
}
function EmptyWorkspace(){return <div className="min-h-[calc(100vh-64px)] bg-graphite text-text_primary"><div className="max-w-canvas mx-auto px-6 sm:px-10 py-16"><div className="panel p-10 max-w-2xl"><h1 className="font-display text-3xl">Create your organization first.</h1><p className="text-sm text-text_primary/45 mt-3">Your workspace has no organization yet.</p><Link to="/app" className="inline-flex mt-6 rounded-xl bg-text_primary text-graphite px-5 py-3 text-sm">Set up workspace</Link></div></div></div>}
