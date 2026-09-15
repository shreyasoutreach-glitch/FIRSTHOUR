import React, { useCallback, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, DEMO_TOKENS } from "../lib/api";
import { useCase } from "../lib/CaseContext";
import { useApiData } from "../lib/useApiData";
import ErrorBanner from "../components/ErrorBanner";
import { formatINR } from "../lib/format";
import { StepFooter } from "../components/AppShell";

const LIFECYCLE = ["PROPOSED", "REVIEWED", "APPROVED", "EXECUTED", "VERIFIED"];
const ROLE_OPTIONS = ["ANALYST", "FINANCE_OPERATOR", "INVESTIGATOR", "APPROVER", "ADMINISTRATOR"];

const ACTION_LABELS: Record<string, string> = {
  FREEZE_PAYOUT: "Freeze payout before settlement",
  REVERSE_PAYOUT: "Request reversal of settled payout",
};

export default function RecoveryCommand() {
  const navigate = useNavigate();
  const { incidentId } = useCase();
  const [actingRole, setActingRole] = useState("INVESTIGATOR");
  const [actionError, setActionError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const { data, loading, error, reload } = useApiData(
    () => Promise.all([
      api.getIncident(incidentId),
      api.getTimeline(incidentId),
      api.getEvidence(incidentId),
      api.getExposure(incidentId),
      api.listRecoveryCommands(incidentId),
    ]).then(([incident, timeline, evidence, exposure, commands]) => ({
      incident, timeline, evidence, exposure, commands,
    })),
    [incidentId]
  );

  const command = data?.commands?.[0] ?? null;

  const target = React.useMemo(() => {
    if (!data) return null;
    const payoutEvents = data.timeline.filter((e: any) => e.type === "payout");
    if (payoutEvents.length === 0) return null;

    const confirmedIds: string[] = data.exposure.confirmed_moved.financial_event_ids;
    const pendingIds: string[] = data.exposure.pending.financial_event_ids;
    const confirmedTarget = payoutEvents.find((e: any) => confirmedIds.includes(e.id));
    const pendingTarget = payoutEvents.find((e: any) => pendingIds.includes(e.id));

    if (pendingTarget) return { event: pendingTarget, action: "FREEZE_PAYOUT" };
    if (confirmedTarget) return { event: confirmedTarget, action: "REVERSE_PAYOUT" };
    return { event: payoutEvents[0], action: "REVERSE_PAYOUT" };
  }, [data]);

  const why = React.useMemo(() => {
    if (!data) return null;
    const payoutEvents = data.timeline.filter((e: any) => e.type === "payout");
    const beneficiaryCounts: Record<string, number> = {};
    payoutEvents.forEach((e: any) => {
      beneficiaryCounts[e.beneficiary_contact_id] = (beneficiaryCounts[e.beneficiary_contact_id] || 0) + 1;
    });
    const sharedBeneficiary = Object.values(beneficiaryCounts).some((count) => count > 1);
    const maxRobustZ = Math.max(0, ...payoutEvents.map((e: any) => e.attributes?.robust_z ?? 0));

    const amountClaims = (data.evidence.claims || []).filter((c: any) => c.claim_type === "amount");
    const verifiedClaims = amountClaims.filter((c: any) => c.verification_status === "VERIFIED");
    const verifiedPct = amountClaims.length > 0
      ? Math.round((verifiedClaims.length / amountClaims.length) * 100)
      : null;

    return {
      anomalousPayouts: payoutEvents.length,
      sharedBeneficiary,
      sigma: maxRobustZ,
      verifiedPct,
    };
  }, [data]);

  const runAction = useCallback(async (fn: () => Promise<any>) => {
    setBusy(true);
    setActionError(null);
    try {
      await fn();
      await reload();
    } catch (e: any) {
      setActionError(String(e.message || e));
    } finally {
      setBusy(false);
    }
  }, [reload]);

  const propose = () => runAction(() => api.proposeRecoveryCommand(incidentId, {
    action: target!.action,
    target_id: target!.event.source_reference,
    amount: target!.event.amount,
    reason: `${why?.anomalousPayouts} anomalous payout(s) totaling ${formatINR(data!.incident.headline.total_exposed)}; `
          + `Incident Evidence Score ${data!.incident.incident_evidence_score}/100.`,
    supporting_evidence: [],
  }, DEMO_TOKENS[actingRole]));

  const review = () => runAction(() => api.reviewCommand(command.id, DEMO_TOKENS[actingRole]));
  const approve = () => runAction(() => api.approveCommand(command.id, DEMO_TOKENS[actingRole]));
  const reject = () => runAction(() => api.rejectCommand(command.id, DEMO_TOKENS[actingRole], "Rejected during review"));
  const dryRun = () => runAction(() => api.dryRunCommand(command.id, DEMO_TOKENS[actingRole]));
  const execute = () => runAction(() => api.executeCommand(command.id, DEMO_TOKENS[actingRole]));
  const verify = () => runAction(() => api.verifyCommand(command.id, DEMO_TOKENS[actingRole]));

  const stepIndex = command ? LIFECYCLE.indexOf(command.state) : -1;

  return (
    <div className="max-w-canvas mx-auto px-6 sm:px-10 py-16">
      <p className="label-eyebrow mb-4">Step 7 &middot; Recovery Command</p>
      <h1 className="font-display text-[32px] sm:text-[36px] leading-tight mb-4">
        What can still be recovered?
      </h1>
      <p className="text-[15px] leading-relaxed text-text_primary/70 mb-10 max-w-[600px]">
        Every action below is proposed, reviewed and approved separately &mdash; and even once
        executed, it is <strong>simulated</strong>. Nothing here moves real money.
      </p>

      {error && <ErrorBanner message={error} onRetry={reload} />}
      {loading && <p className="text-text_primary/40 text-[14px] mb-8">Loading case data&hellip;</p>}

      {!error && !loading && data && target && why && (
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_320px] gap-10">
          <div>
            <div className="paper-card px-8 py-8 mb-8">
              <p className="hero-money text-[42px] leading-none mb-1">
                {formatINR(data.incident.headline.total_exposed)}
              </p>
              <p className="text-[14px] text-text_primary/55 mb-6">{data.incident.merchant_name}</p>

              <div className="grid grid-cols-2 gap-6 mb-6">
                <div>
                  <p className="label-eyebrow mb-1">Target</p>
                  <p className="text-[14px] font-ui">Payout {target.event.source_reference}</p>
                </div>
                <div>
                  <p className="label-eyebrow mb-1">Recommended action</p>
                  <p className="text-[14px] font-ui">{ACTION_LABELS[target.action]}</p>
                </div>
              </div>

              <div className="h-px bg-surface_border/25 mb-6" />

              <p className="label-eyebrow mb-3">Why</p>
              <ul className="grid grid-cols-2 gap-y-2 text-[13px] text-text_primary/75">
                <li>{why.anomalousPayouts} anomalous payout(s)</li>
                <li>{why.sharedBeneficiary ? "Shared beneficiary" : "Distinct beneficiaries"}</li>
                <li>Historical novelty: {why.sigma.toFixed(1)}&sigma;</li>
                <li>{why.verifiedPct !== null ? `Evidence verified: ${why.verifiedPct}%` : "No verifiable amount claims"}</li>
              </ul>
            </div>

            <div className="paper-card px-8 py-8">
              <p className="label-eyebrow mb-5">Command lifecycle</p>
              <ol className="flex items-center gap-2 mb-8 flex-wrap">
                {LIFECYCLE.map((step, i) => (
                  <React.Fragment key={step}>
                    <li className="flex items-center gap-2">
                      <span className={`w-2.5 h-2.5 rounded-full ${
                        command?.state === "REJECTED" ? "bg-text_primary/20"
                        : i <= stepIndex ? "bg-vermillion" : "bg-text_primary/15"
                      }`} />
                      <span className={`text-[12px] font-ui ${
                        i <= stepIndex && command?.state !== "REJECTED" ? "text-text_primary" : "text-text_primary/35"
                      }`}>{step}</span>
                    </li>
                    {i < LIFECYCLE.length - 1 && <span className="text-text_primary/20">&rarr;</span>}
                  </React.Fragment>
                ))}
              </ol>

              {command?.state === "REJECTED" && (
                <p className="text-[13px] text-vermillion mb-4">This command was rejected. No further action is possible.</p>
              )}

              <div className="flex items-center gap-3 mb-5">
                <label className="text-[12px] font-ui text-text_primary/55">Acting as</label>
                <select
                  value={actingRole}
                  onChange={(e) => setActingRole(e.target.value)}
                  className="text-[13px] font-ui border border-forest/25 rounded-[2px] px-2 py-1.5 bg-graphite"
                >
                  {ROLE_OPTIONS.map((r) => <option key={r} value={r}>{r.replace("_", " ")}</option>)}
                </select>
                <span className="text-[11px] text-text_primary/40">
                  Try a role without permission &mdash; the backend will genuinely reject it.
                </span>
              </div>

              {actionError && <ErrorBanner message={actionError} />}

              <div className="flex flex-wrap gap-3">
                {!command && (
                  <button className="btn-primary" disabled={busy} onClick={propose}>Propose recovery command</button>
                )}
                {command?.state === "PROPOSED" && (
                  <>
                    <button className="btn-primary" disabled={busy} onClick={review}>Review</button>
                    <button className="btn-secondary" disabled={busy} onClick={reject}>Reject</button>
                  </>
                )}
                {command?.state === "REVIEWED" && (
                  <>
                    <button className="btn-primary" disabled={busy} onClick={approve}>Approve</button>
                    <button className="btn-secondary" disabled={busy} onClick={reject}>Reject</button>
                  </>
                )}
                {command?.state === "APPROVED" && (
                  <>
                    <button className="btn-secondary" disabled={busy} onClick={dryRun}>Dry run</button>
                    <button className="btn-primary" disabled={busy} onClick={execute}>Execute (simulated)</button>
                  </>
                )}
                {command?.state === "EXECUTED" && (
                  <button className="btn-primary" disabled={busy} onClick={verify}>Verify convergence</button>
                )}
              </div>

              {command?.dry_run_result?.after && (
                <div className="mt-6 pt-6 border-t border-gold/20 text-[13px]">
                  <p className="label-eyebrow mb-2">Dry run result</p>
                  <p className="text-text_primary/70">
                    Status would change: <strong>{command.dry_run_result.before?.status}</strong> &rarr;{" "}
                    <strong>{command.dry_run_result.after?.status}</strong>
                  </p>
                  {command.dry_run_result.risks?.length > 0 && (
                    <p className="text-amber mt-1">{command.dry_run_result.risks.join(" ")}</p>
                  )}
                </div>
              )}

              {command?.state === "EXECUTED" && command?.execution_result && (
                <div className="mt-6 pt-6 border-t border-gold/20 text-[13px]">
                  <p className="label-eyebrow mb-2">Execution result &middot; {command.execution_mode}</p>
                  <p className="text-text_primary/70">{command.execution_result.expected_convergence}</p>
                </div>
              )}

              {command?.state === "VERIFIED" && (
                <ConvergencePanel commandId={command.id} />
              )}
            </div>
          </div>

          <aside className="paper-card px-6 py-6 h-fit">
            <p className="label-eyebrow mb-3">What this does not do</p>
            <ul className="text-[13px] text-text_primary/65 space-y-2 leading-relaxed">
              <li>FIRST HOUR does not contact Arrow Industries&rsquo; bank.</li>
              <li>FIRST HOUR does not freeze or reverse anything with a real payment network.</li>
              <li>Execution here is always recorded as SIMULATED, never EXECUTED-for-real.</li>
              <li>Only an Administrator-permissioned user can execute, and never the same person who proposed it can approve it.</li>
            </ul>
          </aside>
        </div>
      )}

      <div className="mt-12">
        <button className="btn-primary" onClick={() => navigate("/recovery/packet")}>
          View recovery packet
        </button>
      </div>

      <StepFooter current="/recovery" />
    </div>
  );
}

function ConvergencePanel({ commandId }: { commandId: string }) {
  const { data } = useApiData(() => api.getConvergence(commandId), [commandId]);
  if (!data) return null;
  return (
    <div className="mt-6 pt-6 border-t border-gold/20 text-[13px]">
      <p className="label-eyebrow mb-2">Convergence</p>
      <p className={`font-display text-[20px] mb-2 ${data.status === "CONVERGED" ? "text-emerald" : "text-vermillion"}`}>
        {data.status}
      </p>
      {data.discrepancies.length > 0 && (
        <ul className="text-vermillion space-y-1">
          {data.discrepancies.map((d: string, i: number) => <li key={i}>{d}</li>)}
        </ul>
      )}
      <ul className="text-text_primary/55 mt-2 space-y-1">
        {data.checks.map((c: any) => (
          <li key={c.check}>{c.passed ? "âœ“" : "âœ—"} {c.check.replace(/_/g, " ")}</li>
        ))}
      </ul>
    </div>
  );
}

