import React, { useEffect, useState } from "react";
import { api } from "../lib/api";
import { useCase } from "../lib/CaseContext";
import { formatDateTime } from "../lib/format";

const ACTOR_COLOR: Record<string, string> = {
  SYSTEM: "text-forest/60 border-forest/20",
  HUMAN: "text-emerald border-emerald/40",
};

export default function Audit() {
  const { incidentId } = useCase();
  const [events, setEvents] = useState<any[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setEvents(null);
    setError(null);
    api.getAudit(incidentId).then(setEvents).catch((e) => setError(String(e)));
  }, [incidentId]);

  return (
    <div className="max-w-canvas mx-auto px-6 sm:px-10 py-16">
      <p className="label-eyebrow mb-4">Audit &middot; {incidentId}</p>
      <h1 className="font-display text-[32px] sm:text-[36px] leading-tight mb-4">
        The accountable record.
      </h1>
      <p className="text-[15px] leading-relaxed text-forest/70 mb-12 max-w-[560px]">
        Every material action FIRST HOUR or a human took on this case, in order. This is not a
        narrative &mdash; it is a log.
      </p>

      {error && (
        <div className="paper-card border border-vermillion/30 px-6 py-5 max-w-[640px] mb-8">
          <p className="text-[13px] text-vermillion">Could not load the audit trail: {error}</p>
        </div>
      )}

      {!events && !error && <p className="text-forest/40 text-[14px]">Loading audit trail&hellip;</p>}

      {events && events.length === 0 && (
        <p className="text-forest/45 text-[14px]">No audit events recorded for this case yet.</p>
      )}

      {events && events.length > 0 && (
        <div className="max-w-[900px] overflow-x-auto">
          <table className="w-full text-[13px] border-collapse">
            <thead>
              <tr className="text-left text-forest/45 text-[11px] uppercase tracking-wide border-b border-gold/25">
                <th className="pb-3 pr-4 font-normal">Time</th>
                <th className="pb-3 pr-4 font-normal">Actor</th>
                <th className="pb-3 pr-4 font-normal">Event</th>
                <th className="pb-3 pr-4 font-normal">Summary</th>
                <th className="pb-3 font-normal">Sources</th>
              </tr>
            </thead>
            <tbody>
              {events.map((e) => (
                <tr key={e.id} className="border-b border-gold/10 align-top">
                  <td className="py-3 pr-4 text-forest/55 whitespace-nowrap">{formatDateTime(e.created_at)}</td>
                  <td className="py-3 pr-4">
                    <span className={`text-[10.5px] uppercase tracking-wide border rounded-full px-2 py-0.5 ${ACTOR_COLOR[e.actor] || "text-forest/50 border-forest/20"}`}>
                      {e.actor}
                    </span>
                  </td>
                  <td className="py-3 pr-4 font-ui">{e.event_type}</td>
                  <td className="py-3 pr-4 text-forest/75 max-w-[280px]">{e.summary}</td>
                  <td className="py-3 text-forest/40 text-[12px] max-w-[220px]">
                    {(e.sources || []).slice(0, 4).join(", ")}
                    {(e.sources || []).length > 4 ? ` +${e.sources.length - 4} more` : ""}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
