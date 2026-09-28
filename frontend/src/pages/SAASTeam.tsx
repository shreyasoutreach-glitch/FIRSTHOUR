import React from "react";
import { ShieldCheck, UserRound, LockKeyhole } from "lucide-react";

export default function SAASTeam() {
  const roles = [
    ["ANALYST", "View cases and evidence", UserRound],
    ["INVESTIGATOR", "Investigate and recommend", ShieldCheck],
    ["APPROVER", "Review and approve recovery", LockKeyhole],
  ];
  return (
    <div className="min-h-[calc(100vh-56px)] bg-graphite text-text_primary">
      <div className="max-w-canvas mx-auto px-6 sm:px-10 py-10">
        <p className="label-eyebrow text-text_primary/35">Administration · Team</p>
        <h1 className="font-display text-4xl mt-2">Controls & separation of duties</h1>
        <p className="text-sm text-text_primary/45 mt-2 max-w-2xl">
          Primhora's recovery workflow is permission-aware. The preview uses seeded roles to demonstrate the same approval boundaries the production identity layer will enforce.
        </p>
        <div className="grid md:grid-cols-3 gap-4 mt-8">
          {roles.map(([role, copy, Icon]: any) => (
            <div key={role} className="rounded-2xl border border-surface_border bg-surface p-6">
              <Icon size={18} />
              <p className="font-ui text-sm mt-8">{role}</p>
              <p className="text-xs text-text_primary/45 mt-2">{copy}</p>
            </div>
          ))}
        </div>
        <div className="mt-6 rounded-2xl border border-amber/20 bg-amber/5 p-5 text-sm text-text_primary/65">
          This buyer preview deliberately does not claim to be an enterprise identity deployment. Live SSO, customer provisioning and MFA are the final identity-layer integration before a customer's production rollout.
        </div>
      </div>
    </div>
  );
}