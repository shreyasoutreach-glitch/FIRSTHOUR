import React, { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import {
  AlertTriangle, ArrowUpRight, CheckCircle2, ChevronDown, Clock3, Filter,
  Search, SlidersHorizontal, X
} from "lucide-react";
import { api, hasAccessTokenProvider } from "../lib/api";
import { useApiData } from "../lib/useApiData";
import ErrorBanner from "../components/ErrorBanner";

type SavedView = { name: string; state: string; severity: string; query: string };

const DEFAULT_VIEWS: SavedView[] = [
  { name: "All open", state: "OPEN", severity: "ALL", query: "" },
  { name: "Critical / high", state: "ALL", severity: "HIGH_CRITICAL", query: "" },
];

function ageLabel(date?: string) {
  if (!date) return "Unknown";
  const ms = Date.now() - new Date(date).getTime();
  if (!Number.isFinite(ms) || ms < 0) return "Just now";
  const mins = Math.floor(ms / 60000);
  if (mins < 60) return `${mins}m`;
  const hours = Math.floor(mins / 60);
  if (hours < 48) return `${hours}h`;
  return `${Math.floor(hours / 24)}d`;
}

function severityTone(severity?: string) {
  const value = String(severity || "MEDIUM").toUpperCase();
  if (value === "CRITICAL") return "border-vermillion/40 bg-vermillion/[0.08] text-vermillion";
  if (value === "HIGH") return "border-amber/35 bg-amber/[0.06] text-amber";
  if (value === "LOW") return "border-surface_border text-text_primary/45";
  return "border-surface_border text-text_primary/60";
}

function stateLabel(state?: string) {
  const value = String(state || "OPEN").replace(/_/g, " ");
  return value;
}

export default function SaaSIncidents() {
  const workspace = sessionStorage.getItem("primhora_workspace");
  const enabled = Boolean(workspace && hasAccessTokenProvider());
  const { data: incidents, loading, error, reload } = useApiData(
    () => enabled ? api.listIncidents() : Promise.resolve([]),
    [enabled]
  );

  const [searchParams, setSearchParams] = useSearchParams();
  const query = searchParams.get("q") || "";
  const state = searchParams.get("state") || "OPEN";
  const severity = searchParams.get("severity") || "ALL";
  const [savedViews, setSavedViews] = useState<SavedView[]>(() => {
    try {
      const raw = localStorage.getItem("primhora_saved_incident_views");
      return raw ? [...DEFAULT_VIEWS, ...JSON.parse(raw)] : DEFAULT_VIEWS;
    } catch { return DEFAULT_VIEWS; }
  });
  const [viewName, setViewName] = useState("");
  const [showSave, setShowSave] = useState(false);

  useEffect(() => {
    try { localStorage.setItem("primhora_saved_incident_views", JSON.stringify(savedViews.slice(DEFAULT_VIEWS.length))); } catch {}
  }, [savedViews]);

  const filtered = useMemo(() => {
    const items = (incidents || []).filter((incident: any) => {
      const haystack = `${incident.id} ${incident.merchant_name || ""} ${incident.scenario || ""}`.toLowerCase();
      const matchesQuery = !query || haystack.includes(query.toLowerCase());
      const incidentState = String(incident.state || "OPEN").toUpperCase();
      const matchesState =
        state === "ALL" ||
        (state === "OPEN" ? !["CLOSED", "RESOLVED"].includes(incidentState) : incidentState === state);
      const incidentSeverity = String(incident.severity || "MEDIUM").toUpperCase();
      const matchesSeverity =
        severity === "ALL" ||
        (severity === "HIGH_CRITICAL" ? ["HIGH", "CRITICAL"].includes(incidentSeverity) : incidentSeverity === severity);
      return matchesQuery && matchesState && matchesSeverity;
    });
    return [...items].sort((a: any, b: any) => {
      if (severity === "HIGH_CRITICAL") return Number(b.incident_evidence_score || 0) - Number(a.incident_evidence_score || 0);
      return new Date(b.created_at || 0).getTime() - new Date(a.created_at || 0).getTime();
    });
  }, [incidents, query, state, severity]);

  const setFilter = (key: string, value: string) => {
    const next = new URLSearchParams(searchParams);
    if (value === "ALL" || (key === "q" && !value)) next.delete(key);
    else next.set(key, value);
    setSearchParams(next);
  };

  const applyView = (view: SavedView) => {
    const next = new URLSearchParams();
    if (view.query) next.set("q", view.query);
    if (view.state !== "ALL") next.set("state", view.state);
    if (view.severity !== "ALL") next.set("severity", view.severity);
    setSearchParams(next);
  };

  const saveCurrentView = () => {
    const name = viewName.trim();
    if (!name) return;
    setSavedViews(current => [...current, { name, state, severity, query }]);
    setViewName("");
    setShowSave(false);
  };

  const clearFilters = () => setSearchParams({});

  if (!workspace) return <EmptyWorkspace />;
  const activeFilterCount = [query, state !== "OPEN" ? state : "", severity !== "ALL" ? severity : ""].filter(Boolean).length;

  return (
    <div className="min-h-[calc(100vh-72px)] bg-graphite text-text_primary">
      <div className="mx-auto max-w-[1500px] px-5 py-9 sm:px-8">
        <div className="flex flex-wrap items-end justify-between gap-5">
          <div>
            <div className="flex items-center gap-2">
              <span className="status-dot bg-emerald" />
              <span className="label-eyebrow text-emerald/70">OPERATIONS · INCIDENTS</span>
            </div>
            <h1 className="font-display text-4xl mt-2 tracking-tight">Incident queue</h1>
            <p className="text-sm leading-relaxed text-text_primary/45 mt-3 max-w-2xl">
              The operating list for financial investigations. Filter by case state, severity or text,
              then open the case with its full evidence and audit context.
            </p>
          </div>
          <Link to="/app/data-sources" className="btn-secondary">Data sources <ArrowUpRight size={14} /></Link>
        </div>

        {!enabled && (
          <div className="mt-7 panel p-5 border-amber/20">
            <p className="label-eyebrow text-amber/70">Production identity required</p>
            <p className="text-sm text-text_primary/50 mt-2">
              Real workspace cases are fetched only after the production identity provider establishes an access token.
            </p>
          </div>
        )}

        {enabled && (
          <>
            <div className="mt-7 panel p-3">
              <div className="flex flex-col lg:flex-row gap-2">
                <label className="flex-1 relative">
                  <Search size={15} className="absolute left-3 top-3 text-text_primary/25" />
                  <input
                    value={query}
                    onChange={e => setFilter("q", e.target.value)}
                    placeholder="Search case ID, merchant, or incident..."
                    className="w-full rounded-xl border border-surface_border bg-graphite py-2.5 pl-9 pr-3 text-sm focus-ring"
                  />
                </label>
                <label className="relative">
                  <SlidersHorizontal size={14} className="absolute left-3 top-3 text-text_primary/30 pointer-events-none" />
                  <select value={state} onChange={e => setFilter("state", e.target.value)} className="appearance-none rounded-xl border border-surface_border bg-graphite py-2.5 pl-8 pr-9 text-sm focus-ring">
                    <option value="OPEN">Open</option>
                    <option value="ALL">All states</option>
                    <option value="INGESTING">Ingesting</option>
                    <option value="INVESTIGATING">Investigating</option>
                    <option value="EXPOSURE_ASSESSED">Exposure assessed</option>
                    <option value="RECOVERY_READY">Recovery ready</option>
                    <option value="CLOSED">Closed</option>
                  </select>
                  <ChevronDown size={13} className="absolute right-3 top-3.5 text-text_primary/25 pointer-events-none" />
                </label>
                <label className="relative">
                  <Filter size={14} className="absolute left-3 top-3 text-text_primary/30 pointer-events-none" />
                  <select value={severity} onChange={e => setFilter("severity", e.target.value)} className="appearance-none rounded-xl border border-surface_border bg-graphite py-2.5 pl-8 pr-9 text-sm focus-ring">
                    <option value="ALL">All severity</option>
                    <option value="CRITICAL">Critical</option>
                    <option value="HIGH">High</option>
                    <option value="MEDIUM">Medium</option>
                    <option value="LOW">Low</option>
                    <option value="HIGH_CRITICAL">High + critical</option>
                  </select>
                  <ChevronDown size={13} className="absolute right-3 top-3.5 text-text_primary/25 pointer-events-none" />
                </label>
                <div className="flex gap-2">
                  <button onClick={() => setShowSave(v => !v)} className="btn-secondary">Save view</button>
                  {activeFilterCount > 0 && <button onClick={clearFilters} aria-label="Clear filters" className="rounded-xl border border-surface_border px-3 text-text_primary/45 hover:text-text_primary"><X size={15}/></button>}
                </div>
              </div>
              <div className="flex flex-wrap items-center gap-2 mt-3">
                <span className="text-[11px] text-text_primary/25">{filtered.length} of {incidents?.length || 0} cases</span>
                <span className="text-text_primary/15">·</span>
                <div className="flex flex-wrap gap-1.5">
                  {savedViews.map((view, index) => (
                    <button key={view.name + index} onClick={() => applyView(view)} className="status-pill border-surface_border text-text_primary/45 hover:text-text_primary hover:border-text_primary/20">
                      {view.name}
                    </button>
                  ))}
                </div>
              </div>
              {showSave && (
                <div className="mt-3 flex gap-2 max-w-md">
                  <input autoFocus value={viewName} onChange={e => setViewName(e.target.value)} onKeyDown={e => { if (e.key === "Enter") saveCurrentView(); }} placeholder="View name" className="flex-1 rounded-xl border border-surface_border bg-graphite px-3 py-2 text-sm focus-ring" />
                  <button onClick={saveCurrentView} className="btn-primary">Save</button>
                </div>
              )}
            </div>

            {error && <div className="mt-5"><ErrorBanner message={error} onRetry={reload} /></div>}
            {loading && <div className="mt-5 text-sm text-text_primary/35">Loading incident queue…</div>}

            {!loading && !error && filtered.length === 0 && (
              <div className="mt-5 panel p-12 text-center">
                <CheckCircle2 size={21} className="mx-auto text-emerald/80" />
                <h2 className="font-display text-2xl mt-4">Queue is clear</h2>
                <p className="text-sm text-text_primary/40 mt-2 max-w-md mx-auto">
                  No cases match the current view. Clear your filters or connect an authorized source.
                </p>
              </div>
            )}

            {!loading && !error && filtered.length > 0 && (
              <div className="mt-5 panel overflow-hidden">
                <div className="hidden md:grid grid-cols-[1.6fr_.8fr_.65fr_.9fr_.55fr_auto] gap-4 px-5 py-3 border-b border-surface_border text-[10px] uppercase tracking-[0.12em] text-text_primary/25">
                  <span>Case</span><span>State</span><span>Severity</span><span>Exposure</span><span>Age</span><span />
                </div>
                <div className="divide-y divide-surface_border">
                  {filtered.map((incident: any) => (
                    <Link key={incident.id} to={`/app/incidents/${incident.id}`} className="grid md:grid-cols-[1.6fr_.8fr_.65fr_.9fr_.55fr_auto] items-center gap-4 px-5 py-4 hover:bg-white/[0.025] transition group">
                      <div className="min-w-0">
                        <div className="flex items-center gap-2">
                          <p className="text-sm font-medium truncate">{incident.scenario || "Financial incident"}</p>
                          <span className="text-[10px] text-text_primary/25 font-mono shrink-0">{incident.id}</span>
                        </div>
                        <p className="text-xs text-text_primary/35 mt-1 truncate">{incident.merchant_name || "Unknown merchant"}</p>
                      </div>
                      <div><span className="status-pill border-surface_border text-text_primary/55">{stateLabel(incident.state)}</span></div>
                      <div><span className={`status-pill ${severityTone(incident.severity)}`}>{incident.severity || "MEDIUM"}</span></div>
                      <div>
                        <p className="text-sm font-ui">{incident.financial_exposure != null ? formatAmount(incident.financial_exposure) : "—"}</p>
                        <p className="text-[10px] text-text_primary/25 mt-1">{Math.round((incident.confidence || 0) * 100)}% confidence</p>
                      </div>
                      <div className="text-xs text-text_primary/40">{ageLabel(incident.created_at)}</div>
                      <ArrowUpRight size={15} className="text-text_primary/20 group-hover:text-text_primary/60 transition" />
                    </Link>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

function formatAmount(value: any) {
  const number = Number(value);
  if (!Number.isFinite(number)) return "—";
  return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(number);
}

function EmptyWorkspace() {
  return (
    <div className="min-h-[calc(100vh-72px)] bg-grid">
      <div className="mx-auto max-w-[1100px] px-5 py-20 sm:px-8">
        <div className="max-w-2xl panel p-8 sm:p-10">
          <h1 className="font-display text-3xl">Create your organization first.</h1>
          <p className="text-sm text-text_primary/45 mt-3">Your workspace has no organization yet.</p>
          <Link to="/app" className="inline-flex mt-6 rounded-xl bg-text_primary text-graphite px-5 py-3 text-sm">Set up workspace</Link>
        </div>
      </div>
    </div>
  );
}
