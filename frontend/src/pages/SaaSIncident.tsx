import React from "react";
import { Link, useParams } from "react-router-dom";
import { ArrowLeft, FileSearch, Clock3 } from "lucide-react";
import { api, hasAccessTokenProvider } from "../lib/api";
import { useApiData } from "../lib/useApiData";
import ErrorBanner from "../components/ErrorBanner";

export default function SaaSIncident(){
  const {id=""}=useParams();
  const enabled=hasAccessTokenProvider();
  const {data,error,loading,reload}=useApiData(
    ()=>enabled ? Promise.all([api.getIncident(id),api.getTimeline(id),api.getEvidence(id)]) : Promise.resolve(null),
    [id,enabled]
  );
  if(!enabled) return <div className="max-w-canvas mx-auto px-6 sm:px-10 py-16"><div className="panel p-10 max-w-2xl"><p className="label-eyebrow">Workspace case</p><h1 className="font-display text-3xl mt-2">Production identity required.</h1><p className="text-sm text-text_primary/45 mt-3">Real workspace cases are protected by the production identity provider. Synthetic cases stay inside the demo.</p><Link to="/app/incidents" className="inline-flex mt-6 rounded-xl border border-surface_border px-5 py-3 text-sm">Back to incidents</Link></div></div>;
  if(loading) return <div className="max-w-canvas mx-auto px-6 sm:px-10 py-16 text-text_primary/45">Loading case…</div>;
  if(error||!data) return <div className="max-w-canvas mx-auto px-6 sm:px-10 py-16"><ErrorBanner message={error||"Case unavailable"} onRetry={reload}/></div>;
  const [incident,timeline,evidence]=data as any[];
  return <div className="max-w-canvas mx-auto px-6 sm:px-10 py-10">
    <Link to="/app/incidents" className="inline-flex items-center gap-2 text-xs text-text_primary/40"><ArrowLeft size={13}/> Incidents</Link>
    <div className="mt-8 flex items-start justify-between gap-6 flex-wrap"><div><p className="label-eyebrow">{incident.id} · {incident.state}</p><h1 className="font-display text-4xl mt-2">{incident.scenario||"Financial incident"}</h1><p className="text-sm text-text_primary/45 mt-2">{incident.merchant_name}</p></div><div className="panel px-5 py-4"><p className="label-eyebrow">Evidence score</p><p className="font-display text-3xl mt-1">{incident.incident_evidence_score}</p><p className="text-[11px] text-text_primary/35">Deterministic, not a fraud probability</p></div></div>
    <div className="grid lg:grid-cols-2 gap-5 mt-8">
      <section className="panel p-6"><div className="flex items-center gap-2"><Clock3 size={17}/><h2 className="font-display text-xl">Timeline</h2></div><div className="mt-5 space-y-3">{timeline.map((e:any)=><div key={e.id} className="border-l border-surface_border pl-4"><p className="text-xs text-text_primary/35">{e.timestamp}</p><p className="text-sm mt-1">{e.type}</p><p className="text-xs text-text_primary/45 mt-1">{e.source_reference||e.id}</p></div>)}</div></section>
      <section className="panel p-6"><div className="flex items-center gap-2"><FileSearch size={17}/><h2 className="font-display text-xl">Evidence</h2></div><div className="mt-5 space-y-3">{evidence.artifacts?.map((a:any)=><div key={a.id} className="border border-surface_border rounded-xl p-4"><p className="text-sm">{a.filename}</p><p className="text-xs text-text_primary/40 mt-1">{a.extraction_status} · {a.sha256?.slice(0,16)}…</p></div>)}</div></section>
    </div>
    <p className="text-xs text-text_primary/35 mt-8">PRIMHORA has not moved or recovered money. This case contains source-backed analysis for authorized human resolution.</p>
  </div>;
}
