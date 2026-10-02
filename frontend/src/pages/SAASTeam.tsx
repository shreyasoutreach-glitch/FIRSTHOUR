import React, { useState } from "react";
import { Link } from "react-router-dom";
import {
  Check, ChevronDown, Copy, KeyRound, LockKeyhole, Mail, ShieldCheck,
  Users, UserRound, X
} from "lucide-react";
import { authRequired, authProviderName } from "../lib/auth";

const ROLES = [
  { name: "ANALYST", desc: "View investigations and evidence", color: "border-surface_border" },
  { name: "INVESTIGATOR", desc: "Investigate, attest and recommend", color: "border-emerald/25" },
  { name: "APPROVER", desc: "Review and approve governed actions", color: "border-gold/25" },
  { name: "ADMINISTRATOR", desc: "Manage workspace and controls", color: "border-vermillion/25" },
];

const MATRIX = [
  ["View incidents", true, true, true, true],
  ["View evidence", true, true, true, true],
  ["Add human attestation", false, true, true, true],
  ["Propose recovery command", false, true, false, true],
  ["Review command", false, true, true, true],
  ["Approve command", false, false, true, true],
  ["Manage identity / roles", false, false, false, true],
  ["Reset / inject synthetic demo", false, false, false, true],
];

export default function SAASTeam() {
  const workspace = sessionStorage.getItem("primhora_workspace");
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("ANALYST");
  const [draftReady, setDraftReady] = useState(false);
  const productionIdentity = authRequired();

  if (!workspace) {
    return (
      <div className="min-h-[calc(100vh-72px)] bg-grid">
        <div className="mx-auto max-w-[1100px] px-5 py-16 sm:px-8">
          <div className="panel max-w-2xl p-10">
            <Users size={20} />
            <h1 className="font-display text-3xl mt-5">Create your organization first.</h1>
            <p className="text-sm text-text_primary/45 mt-3">Team membership belongs to an organization.</p>
            <Link to="/app" className="inline-flex items-center gap-2 mt-6 rounded-xl bg-text_primary text-graphite px-5 py-3 text-sm font-medium">Set up workspace</Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-[calc(100vh-72px)] bg-graphite text-text_primary">
      <div className="mx-auto max-w-[1500px] px-5 py-9 sm:px-8">
        <div className="flex flex-wrap items-end justify-between gap-5">
          <div>
            <div className="flex items-center gap-2">
              <span className="status-dot bg-emerald" />
              <span className="label-eyebrow text-emerald/70">ADMINISTRATION · CONTROLS</span>
            </div>
            <h1 className="font-display text-4xl mt-2 tracking-tight">Identity & control policy</h1>
            <p className="text-sm text-text_primary/45 mt-3 max-w-2xl">
              Define who can see, investigate and approve sensitive work. PRIMHORA keeps proposal and approval separate.
            </p>
          </div>
        </div>

        <div className="grid lg:grid-cols-[1fr_360px] gap-5 mt-7">
          <section className="panel overflow-hidden">
            <div className="px-6 py-5 border-b border-surface_border">
              <div className="flex items-center justify-between gap-4">
                <div>
                  <p className="label-eyebrow text-text_primary/25">PERMISSION MATRIX</p>
                  <h2 className="font-display text-xl mt-1">Role capabilities</h2>
                </div>
                <span className="status-pill border-surface_border text-text_primary/35">Server enforced</span>
              </div>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[780px] text-xs">
                <thead>
                  <tr className="text-left text-[10px] uppercase tracking-[0.12em] text-text_primary/25 border-b border-surface_border">
                    <th className="px-6 py-3 font-normal">Capability</th>
                    {ROLES.map(roleItem => <th key={roleItem.name} className="px-4 py-3 font-normal">{roleItem.name}</th>)}
                  </tr>
                </thead>
                <tbody>
                  {MATRIX.map(([capability, ...permissions]) => (
                    <tr key={String(capability)} className="border-b border-surface_border last:border-0">
                      <td className="px-6 py-3.5 text-text_primary/65">{capability}</td>
                      {permissions.map((allowed: any, index: number) => (
                        <td key={index} className="px-4 py-3.5">
                          {allowed
                            ? <Check size={14} className="text-emerald" aria-label="Allowed" />
                            : <X size={14} className="text-text_primary/15" aria-label="Not allowed" />}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          <aside className="space-y-5">
            <div className="panel p-6">
              <div className="flex items-center gap-2"><KeyRound size={16}/><p className="font-medium">Identity provider</p></div>
              <p className="font-display text-2xl mt-4">{productionIdentity ? authProviderName() : "Synthetic access"}</p>
              <p className="text-xs text-text_primary/40 mt-2">
                {productionIdentity ? "Production OIDC is required before real customer cases are available." : "Demo bearer sessions are active only for the synthetic environment."}
              </p>
              <div className="mt-5 pt-5 border-t border-surface_border">
                <div className="flex items-center gap-2 text-xs"><span className={`status-dot ${productionIdentity ? "bg-emerald" : "bg-amber"}`}/>{productionIdentity ? "OIDC gate active" : "Synthetic identity mode"}</div>
              </div>
            </div>

            <div className="panel p-6">
              <div className="flex items-center gap-2"><LockKeyhole size={16}/><p className="font-medium">Separation of duties</p></div>
              <p className="text-sm text-text_primary/55 mt-3 leading-relaxed">
                Proposal and approval are intentionally separate. The backend rejects self-approval even when the same person has multiple permissions.
              </p>
              <div className="mt-5 grid grid-cols-2 gap-2 text-xs">
                <div className="rounded-xl border border-surface_border p-3"><span className="text-text_primary/30 block mb-1">Proposal</span><span>INVESTIGATOR</span></div>
                <div className="rounded-xl border border-gold/20 p-3"><span className="text-text_primary/30 block mb-1">Approval</span><span>APPROVER</span></div>
              </div>
            </div>
          </aside>
        </div>

        <section className="panel p-6 mt-5">
          <div className="flex items-center gap-2"><UserRound size={16}/><div><p className="label-eyebrow text-text_primary/25">ROLE CATALOG</p><h2 className="font-display text-xl mt-1">Standard roles</h2></div></div>
          <div className="grid md:grid-cols-2 xl:grid-cols-4 gap-3 mt-6">
            {ROLES.map(item => (
              <div key={item.name} className={`rounded-xl border ${item.color} bg-surface/[0.35] p-5`}>
                <p className="font-mono text-[11px]">{item.name}</p>
                <p className="text-xs leading-relaxed text-text_primary/40 mt-2">{item.desc}</p>
                <span className="status-pill border-surface_border text-text_primary/25 mt-4">0 members</span>
              </div>
            ))}
          </div>
        </section>

        <section className="grid lg:grid-cols-[1fr_360px] gap-5 mt-5">
          <div className="panel p-6">
            <div className="flex items-center gap-2"><ShieldCheck size={16}/><p className="font-medium">Control state</p></div>
            <div className="grid sm:grid-cols-2 gap-3 mt-5">
              <Control label="Read-only execution boundary" value="ENFORCED" />
              <Control label="Tenant isolation" value="SERVER-SCOPED" />
              <Control label="API responses" value="NO-STORE" />
              <Control label="Recovery self-approval" value="BLOCKED" />
            </div>
          </div>

          <div className="panel p-6">
            <p className="label-eyebrow text-text_primary/25">INVITATION DRAFT</p>
            <h2 className="font-display text-xl mt-2">Prepare a member invite</h2>
            <p className="text-xs text-text_primary/40 mt-2 leading-relaxed">
              This build has no production email/invitation service. We show the draft, but never claim it was sent.
            </p>
            <label className="block text-xs text-text_primary/50 mt-5">Email
              <input value={email} onChange={e => { setEmail(e.target.value); setDraftReady(false); }} placeholder="finance@example.com" type="email" className="mt-2 w-full rounded-xl border border-surface_border bg-graphite px-3 py-3 text-sm focus-ring" />
            </label>
            <label className="block text-xs text-text_primary/50 mt-4">Role
              <select value={role} onChange={e => setRole(e.target.value)} className="mt-2 w-full rounded-xl border border-surface_border bg-graphite px-3 py-3 text-sm focus-ring">
                {ROLES.map(item => <option key={item.name}>{item.name}</option>)}
              </select>
            </label>
            <button disabled={!email.trim()} onClick={() => setDraftReady(true)} className="mt-5 inline-flex items-center gap-2 rounded-xl bg-text_primary text-graphite px-4 py-2.5 text-sm font-medium disabled:opacity-30">
              <Mail size={14}/> Prepare draft
            </button>
            {draftReady && (
              <div className="mt-4 rounded-xl border border-emerald/15 bg-emerald/[0.03] p-4">
                <div className="flex items-center gap-2 text-sm"><Check size={14} className="text-emerald"/> Draft ready</div>
                <p className="text-xs text-text_primary/35 mt-2">{email} · {role}. No email was sent.</p>
                <button onClick={() => navigator.clipboard?.writeText(`Invite ${email} as ${role} to ${workspace}`)} className="mt-3 inline-flex items-center gap-2 text-xs text-text_primary/50 hover:text-text_primary"><Copy size={13}/> Copy</button>
              </div>
            )}
          </div>
        </section>

        <div className="mt-6 text-[11px] text-text_primary/25">
          Identity and authorization controls are enforced by the backend. UI state is not a security boundary.
        </div>
      </div>
    </div>
  );
}

function Control({label, value}:{label:string,value:string}) {
 return <div className="rounded-xl border border-surface_border p-4"><p className="text-[11px] text-text_primary/30">{label}</p><p className="font-mono text-xs mt-2">{value}</p></div>
}
