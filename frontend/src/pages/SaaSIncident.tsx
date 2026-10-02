import React, { useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  AlertTriangle, ArrowLeft, CheckCircle2, Clock3, FileSearch, GitBranch,
  History, ShieldCheck, Users, WalletCards
} from "lucide-react";
import { api, hasAccessTokenProvider } from "../lib/api";
import { useApiData } from "../lib/useApiData";
import ErrorBanner from "../components/ErrorBanner";

type Tab = "overview" | "timeline" | "evidence" | "activity";

function severityTone(value?: string) {
  const severity = String(value || "MEDIUM").toUpperCase();
  if (severity === "CRITICAL") return "border-vermillion/40 bg-vermillion/[0.08] text-vermillion";
  if (severity === "HIGH") return "border-amber/35 bg-amber/[0.06] text-amber";
  return "border-surface_border text-text_primary/55";
}

function formatINR(value: any) {
  const number = Number(value);
  if (!Number.isFinite(number)) return "₹0";
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(number);
}

function formatAge(date?: string) {
  if (!date) return "Unknown age";
  const ms = Date.now() - new Date(date).getTime();
  const mins = Math.max(0, Math.floor(ms / 60000));
  if (mins < 60) return `${mins}m old`;
  const hours = Math.floor(mins / 60);
  if (hours < 48) return `${hours}h old`;
  return `${Math.floor(hours / 24)}d old`;
}

export default function SaaSIncident() {
  const { id = "" } = useParams();
  const enabled = hasAccessTokenProvider();
  const [tab, setTab] = useState<Tab>("overview");

  const { data, error, loading, reload } = useApiData(
    () => enabled
      ? Promise.all([
          api.getIncident(id),
          api.getTimeline(id),
          api.getEvidence(id),
          api.getExposure(id),
          api.getAudit(id),
          api.getGraph(id),
        ])
      : Promise.resolve(null),
    [id, enabled]
  );

  if (!enabled) {
    return (
      <div className="mx-auto max-w-[1100px] px-5 py-16 sm:px-8">
        <div className="panel max-w-2xl p-10">
          <ShieldCheck size={20} />
          <p className="label-eyebrow text-text_primary/25 mt-6">WORKSPACE CASE</p>
          <h1 className="font-display text-3xl mt-2">Production identity required.</h1>
          <p className="text-sm text-text_primary/45 mt-3">
            Real workspace cases are protected by the production identity provider. Synthetic cases remain inside the demo environment.
          </p>
          <Link to="/app/incidents" className="inline-flex mt-6 rounded-xl border border-surface_border px-5 py-3 text-sm">
            Back to incidents
          </Link>
        </div>
      </div>
    );
  }

  if (loading) {
    return <div className="mx-auto max-w-[1100px] px-5 py-16 sm:px-8 text-text_primary/45">Loading case workspace…</div>;
  }

  if (error || !data) {
    return (
      <div className="mx-auto max-w-[1100px] px-5 py-16 sm:px-8">
        <ErrorBanner message={error || "Case unavailable"} onRetry={reload} />
      </div>
    );
  }

  const [incident, timeline, evidence, exposure, audit, graph] = data as any[];

  const stats = useMemo(() => ({
    exposure: exposure?.confirmed_moved?.total || exposure?.pending?.total || 0,
    evidence: evidence?.artifacts?.length || 0,
    entities: graph?.nodes?.length || incident?.affected_entities || 0,
    confidence: Math.round(Number(incident?.confidence || 0) * 100),
  }), [incident, exposure, evidence, graph]);

  const tabs: [Tab, string, any][] = [
    ["overview", "Overview", ShieldCheck],
    ["timeline", "Timeline", Clock3],
    ["evidence", "Evidence", FileSearch],
    ["activity", "Activity", History],
  ];

  return (
    <div className="min-h-[calc(100vh-72px)] bg-graphite text-text_primary">
      <div className="mx-auto max-w-[1500px] px-5 py-7 sm:px-8">
        <Link to="/app/incidents" className="inline-flex items-center gap-2 text-xs text-text_primary/35 hover:text-text_primary">
          <ArrowLeft size={13} /> Incident queue
        </Link>

        <div className="mt-6 panel overflow-hidden">
          <div className="bg-grid px-6 py-6 sm:px-8">
            <div className="flex flex-wrap items-start justify-between gap-6">
              <div className="min-w-0">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-mono text-[11px] text-text_primary/30">{incident.id}</span>
                  <span className="status-pill border-surface_border text-text_primary/55">{String(incident.state || "OPEN").replace(/_/g, " ")}</span>
                  <span className={`status-pill ${severityTone(incident.severity)}`}>{incident.severity || "MEDIUM"}</span>
                </div>
                <h1 className="font-display text-3xl sm:text-4xl mt-3 tracking-tight">
                  {incident.scenario || "Financial incident"}
                </h1>
                <p className="text-sm text-text_primary/45 mt-2">{incident.merchant_name} · {formatAge(incident.created_at)}</p>
              </div>

              <div className="text-right">
                <p className="label-eyebrow text-text_primary/25">Incident Evidence Score</p>
                <p className="font-display text-4xl mt-1">{incident.incident_evidence_score}</p>
                <p className="text-[11px] text-text_primary/30">deterministic signal, not a fraud probability</p>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 lg:grid-cols-4 divide-x divide-y lg:divide-y-0 divide-surface_border border-t border-surface_border">
            <CaseStat icon={WalletCards} label="Exposure" value={formatINR(stats.exposure)} />
            <CaseStat icon={FileSearch} label="Evidence" value={stats.evidence} />
            <CaseStat icon={GitBranch} label="Related entities" value={stats.entities} />
            <CaseStat icon={CheckCircle2} label="Confidence" value={`${stats.confidence}%`} />
          </div>

          <nav className="flex gap-1 overflow-x-auto border-t border-surface_border px-3 py-2">
            {tabs.map(([value, label, Icon]) => (
              <button
                key={value}
                onClick={() => setTab(value)}
                className={`inline-flex shrink-0 items-center gap-2 rounded-lg px-4 py-2.5 text-xs transition ${tab === value ? "bg-white/[0.07] text-text_primary" : "text-text_primary/35 hover:text-text_primary/70"}`}
              >
                <Icon size={14} /> {label}
              </button>
            ))}
          </nav>
        </div>

        {tab === "overview" && (
          <div className="grid xl:grid-cols-[1.35fr_.65fr] gap-5 mt-5">
            <section className="panel p-6">
              <SectionTitle icon={ShieldCheck} title="Case assessment" />
              <div className="grid md:grid-cols-2 gap-4 mt-5">
                <Fact label="Current state" value={String(incident.state || "OPEN").replace(/_/g, " ")} />
                <Fact label="Resolution state" value={incident.resolution_state || "OPEN"} />
                <Fact label="Evidence posture" value={stats.evidence ? `${stats.evidence} artifact(s) attached` : "No artifacts attached"} />
                <Fact label="Affected entities" value={String(incident.affected_entities || stats.entities || 0)} />
              </div>
              <div className="mt-6 rounded-xl border border-gold/15 bg-gold/[0.03] p-4">
                <p className="label-eyebrow text-text_primary/30">TRUTH BOUNDARY</p>
                <p className="text-sm leading-relaxed text-text_primary/55 mt-2">
                  Financial amounts and transaction state come from canonical records. Evidence claims remain unverified until deterministic cross-reference succeeds. Human attestations are stored separately.
                </p>
              </div>
            </section>

            <section className="panel p-6">
              <SectionTitle icon={Users} title="Investigation posture" />
              <div className="mt-5 space-y-4">
                <MiniRow label="Review age" value={formatAge(incident.created_at)} />
                <MiniRow label="Audit events" value={String(audit?.length || 0)} />
                <MiniRow label="Timeline events" value={String(timeline?.length || 0)} />
                <MiniRow label="Evidence claims" value={String(evidence?.claims?.length || 0)} />
              </div>
            </section>

            <section className="panel p-6 xl:col-span-2">
              <SectionTitle icon={Clock3} title="Latest case activity" />
              <ActivityList events={(audit || []).slice(-6).reverse()} empty="No case activity recorded yet." />
            </section>
          </div>
        )}

        {tab === "timeline" && (
          <section className="panel p-6 mt-5">
            <SectionTitle icon={Clock3} title="Deterministic incident timeline" />
            <p className="text-xs text-text_primary/35 mt-2 mb-6">Chronology is assembled from financial and communication records. It is not an LLM-authored narrative.</p>
            <Timeline events={timeline || []} />
          </section>
        )}

        {tab === "evidence" && (
          <section className="panel p-6 mt-5">
            <SectionTitle icon={FileSearch} title="Evidence ledger" />
            <p className="text-xs text-text_primary/35 mt-2 mb-6">Artifacts are source-backed. Claims can be verified, conflicting or remain unverified.</p>
            {(evidence?.artifacts || []).length === 0 ? (
              <EmptyPanel icon={FileSearch} text="No evidence artifacts attached to this case." />
            ) : (
              <div className="space-y-3">
                {(evidence.artifacts || []).map((artifact: any) => {
                  const claims = (evidence.claims || []).filter((c: any) => c.source_artifact_id === artifact.id);
                  return (
                    <div key={artifact.id} className="rounded-xl border border-surface_border p-4">
                      <div className="flex flex-wrap items-start justify-between gap-4">
                        <div>
                          <p className="text-sm font-medium">{artifact.filename}</p>
                          <p className="text-[11px] text-text_primary/30 mt-1">{artifact.mime_type} · {artifact.extraction_status}</p>
                        </div>
                        <span className="font-mono text-[10px] text-text_primary/25">{artifact.sha256?.slice(0, 16)}…</span>
                      </div>
                      <div className="flex flex-wrap gap-1.5 mt-4">
                        {claims.length === 0 ? <span className="text-xs text-text_primary/30">No extracted claims</span> : claims.map((claim: any) => (
                          <span key={claim.id} className={`status-pill ${claim.verification_status === "VERIFIED" ? "border-emerald/30 text-emerald" : claim.verification_status === "CONFLICTING" ? "border-vermillion/30 text-vermillion" : "border-surface_border text-text_primary/40"}`}>
                            {claim.claim_type}: {claim.verification_status}
                          </span>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </section>
        )}

        {tab === "activity" && (
          <section className="panel p-6 mt-5">
            <SectionTitle icon={History} title="Case activity" />
            <p className="text-xs text-text_primary/35 mt-2 mb-6">A unified history of material system and human events for this case.</p>
            <ActivityList events={(audit || []).slice().reverse()} empty="No activity recorded yet." />
          </section>
        )}
      </div>
    </div>
  );
}

function CaseStat({ icon: Icon, label, value }: { icon: any; label: string; value: string | number }) {
  return (
    <div className="p-5">
      <Icon size={15} className="text-text_primary/25" />
      <p className="label-eyebrow text-text_primary/25 mt-4">{label}</p>
      <p className="font-display text-2xl mt-1">{value}</p>
    </div>
  );
}

function SectionTitle({ icon: Icon, title }: { icon: any; title: string }) {
  return <div className="flex items-center gap-2"><Icon size={16} /><h2 className="font-display text-xl">{title}</h2></div>;
}

function Fact({ label, value }: { label: string; value: string }) {
  return <div className="rounded-xl border border-surface_border p-4"><p className="text-[11px] text-text_primary/30">{label}</p><p className="text-sm mt-2">{value}</p></div>;
}

function MiniRow({ label, value }: { label: string; value: string }) {
  return <div className="flex items-center justify-between gap-4 text-sm"><span className="text-text_primary/40">{label}</span><span>{value}</span></div>;
}

function Timeline({ events }: { events: any[] }) {
  return (
    <div className="space-y-0">
      {events.length === 0 ? <EmptyPanel icon={Clock3} text="No timeline events recorded yet." /> : events.map((event: any, index: number) => (
        <div key={event.id} className="relative flex gap-4 py-4 first:pt-0 last:pb-0">
          {index < events.length - 1 && <span className="absolute left-[7px] top-8 bottom-0 w-px bg-surface_border" />}
          <span className="relative mt-1.5 h-3.5 w-3.5 shrink-0 rounded-full border border-surface_border bg-graphite" />
          <div className="min-w-0 flex-1">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <p className="text-sm">{event.label || event.type}</p>
              <time className="text-[11px] text-text_primary/30">{event.timestamp}</time>
            </div>
            <p className="text-xs text-text_primary/40 mt-1">{event.detail || `${event.type} · ${event.source_reference || event.id}`}</p>
            <p className="font-mono text-[10px] text-text_primary/20 mt-2">{event.source_reference || event.source_artifact_id || event.id}</p>
          </div>
        </div>
      ))}
    </div>
  );
}

function ActivityList({ events, empty }: { events: any[]; empty: string }) {
  if (!events.length) return <EmptyPanel icon={History} text={empty} />;
  return (
    <div className="space-y-0">
      {events.map((event: any) => (
        <div key={event.id} className="flex gap-4 border-b border-surface_border py-4 last:border-0">
          <span className={`mt-1 h-2 w-2 shrink-0 rounded-full ${event.actor === "HUMAN" ? "bg-emerald" : "bg-text_primary/30"}`} />
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <p className="text-sm">{event.event_type}</p>
              <span className="text-[10px] text-text_primary/25">{event.actor}</span>
            </div>
            <p className="text-xs text-text_primary/40 mt-1">{event.summary}</p>
            <time className="text-[10px] text-text_primary/25 mt-2 block">{event.created_at}</time>
          </div>
        </div>
      ))}
    </div>
  );
}

function EmptyPanel({ icon: Icon, text }: { icon: any; text: string }) {
  return <div className="rounded-xl border border-dashed border-surface_border p-10 text-center"><Icon size={18} className="mx-auto text-text_primary/25" /><p className="text-sm text-text_primary/40 mt-3">{text}</p></div>;
}
