import React from "react";
import { api } from "../lib/api";
import { useCase } from "../lib/CaseContext";
import { useApiData } from "../lib/useApiData";
import ErrorBanner from "../components/ErrorBanner";
import { formatINR, formatDateTime } from "../lib/format";
import SourceRef from "../components/SourceRef";
import { StepFooter } from "../components/AppShell";

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="mb-10">
      <p className="label-eyebrow mb-3">{title}</p>
      {children}
      <div className="h-px bg-gold/20 mt-8" />
    </section>
  );
}

export default function RecoveryPacket() {
  const { incidentId } = useCase();
  const { data: packet, loading, error, reload } = useApiData(() => api.getRecoveryPacket(incidentId), [incidentId]);

  if (error) {
    return (
      <div className="max-w-canvas mx-auto px-6 sm:px-10 py-16">
        <ErrorBanner message={error} onRetry={reload} />
      </div>
    );
  }

  if (loading || !packet) {
    return <div className="max-w-canvas mx-auto px-6 sm:px-10 py-16 text-forest/50">Assembling recovery packet&hellip;</div>;
  }

  return (
    <div className="max-w-canvas mx-auto px-6 sm:px-10 py-16">
      <div className="max-w-[720px] bg-ivory border border-gold/25 shadow-raised px-10 py-12 sm:px-14 sm:py-14 mx-auto">
        <div className="flex items-baseline justify-between mb-2">
          <h1 className="font-display text-[28px]">Recovery Packet</h1>
          <span className="text-[13px] font-ui text-forest/50">Case {packet.case_id}</span>
        </div>
        <p className="text-[13px] text-forest/50 mb-10">
          Generated for internal use, your bank and Razorpay &mdash; every figure below traces to a source.
        </p>

        <Section title="Incident Summary">
          <p className="text-[14px] leading-relaxed text-forest/85">{packet.incident_summary}</p>
          <p className="text-[13px] text-forest/50 mt-2">
            Window: {packet.incident_window.start && formatDateTime(packet.incident_window.start)}
            {" – "}
            {packet.incident_window.end && formatDateTime(packet.incident_window.end)}
          </p>
        </Section>

        <Section title="Total Exposure">
          <div className="grid grid-cols-3 gap-4 text-[14px]">
            <div>
              <p className="text-forest/45 text-[12px]">Confirmed moved</p>
              <p className="font-display text-[20px] text-vermillion">{formatINR(packet.total_exposure.confirmed_moved.total)}</p>
            </div>
            <div>
              <p className="text-forest/45 text-[12px]">Pending</p>
              <p className="font-display text-[20px] text-amber">{formatINR(packet.total_exposure.pending.total)}</p>
            </div>
            <div>
              <p className="text-forest/45 text-[12px]">Attempted</p>
              <p className="font-display text-[20px] text-forest/60">{formatINR(packet.total_exposure.attempted.total)}</p>
            </div>
          </div>
        </Section>

        <Section title="Transaction Table">
          <table className="w-full text-[13px]">
            <thead>
              <tr className="text-left text-forest/45 text-[11px] uppercase tracking-wide">
                <th className="pb-2 font-normal">Time</th>
                <th className="pb-2 font-normal">Beneficiary</th>
                <th className="pb-2 font-normal text-right">Amount</th>
              </tr>
            </thead>
            <tbody>
              {packet.transaction_table.map((t: any) => (
                <tr key={t.payout_id} className="border-t border-gold/15">
                  <td className="py-2 text-forest/60">{formatDateTime(t.timestamp)}</td>
                  <td className="py-2">{t.beneficiary}</td>
                  <td className="py-2 text-right font-ui">
                    {formatINR(t.amount)}
                    <SourceRef id={t.source_reference} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Section>

        <Section title="Beneficiary Information">
          <ul className="space-y-2 text-[13px]">
            {packet.beneficiary_information.map((b: any) => (
              <li key={b.contact_id} className="flex justify-between">
                <span>{b.name}</span>
                <span className={b.is_new ? "text-vermillion" : "text-forest/50"}>
                  {b.is_new ? "New beneficiary" : "Known beneficiary"}
                </span>
              </li>
            ))}
          </ul>
        </Section>

        <Section title="Communication Evidence">
          <ul className="space-y-3 text-[13px]">
            {packet.communication_evidence.map((c: any) => (
              <li key={c.id}>
                <p className="text-forest/45 text-[11px] uppercase tracking-wide mb-1">
                  {c.channel} &middot; {formatDateTime(c.timestamp)} &middot; {c.correlation_status}
                </p>
                <p className="leading-snug">{c.body_text}</p>
              </li>
            ))}
          </ul>
        </Section>

        <Section title="Human Attestations">
          {packet.human_attestations.length === 0 ? (
            <p className="text-[13px] text-forest/45">No attestations recorded yet.</p>
          ) : (
            <ul className="space-y-2 text-[13px]">
              {packet.human_attestations.map((a: any, i: number) => (
                <li key={i}>
                  <span className="text-forest/60">{a.question}</span> &mdash;{" "}
                  <strong>{a.answer}</strong>
                </li>
              ))}
            </ul>
          )}
        </Section>

        <Section title="Evidence Index">
          <ul className="space-y-1 text-[12px] text-forest/60">
            {packet.evidence_index.map((e: any) => (
              <li key={e.artifact_id}>
                {e.filename} &middot; sha256:{e.sha256.slice(0, 16)}&hellip;
              </li>
            ))}
          </ul>
        </Section>

        <section>
          <p className="label-eyebrow mb-3">Official Next Steps</p>
          <ol className="space-y-2 text-[13px] list-decimal list-inside text-forest/80">
            {packet.official_next_steps.map((s: string, i: number) => <li key={i}>{s}</li>)}
          </ol>
        </section>
      </div>

      <StepFooter current="/recovery/packet" />
    </div>
  );
}
