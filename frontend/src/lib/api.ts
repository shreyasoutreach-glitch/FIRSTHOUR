/**
 * Thin fetch wrapper over the FIRST HOUR API. Every function here maps to
 * exactly one backend endpoint -- no client-side re-derivation of financial
 * facts happens anywhere in this file or in the components that call it.
 *
 * BASE resolves to, in order: an explicit VITE_API_BASE_URL (set this if the
 * frontend and backend are served from different origins in production),
 * otherwise the relative path "/api" -- which both the Vite dev server
 * (see vite.config.ts's proxy) and the docker-compose nginx config forward
 * to the backend. No absolute localhost/127.0.0.1 URL is ever hardcoded here.
 *
 * AUTH: the backend now requires a bearer token (see backend/app/core/authz.py).
 * There is no login screen yet -- this demo build ships with the
 * deterministic Administrator token for the default seed (SEED=42),
 * overridable via VITE_DEMO_API_TOKEN. This is explicitly NOT how a real
 * deployment would authenticate (see LIMITATIONS.md) -- it exists so the
 * existing screens keep working without a login flow this pass didn't have
 * time to build. The Recovery Command screen additionally uses requestAs()
 * with the per-role DEMO_TOKENS below, so it can demonstrate real
 * separation-of-duties instead of one admin token clicking through
 * everything.
 */
const BASE = import.meta.env.VITE_API_BASE_URL || "/api";

// Deterministic demo token for TEN_NORTHBRIDGE's ADMINISTRATOR user at the
// default SEED=42 -- printed by `python -m seed.seed` and returned by
// POST /demo/reset. Change SEED and this will stop matching; use
// VITE_DEMO_API_TOKEN to override.
const DEMO_TOKEN = import.meta.env.VITE_DEMO_API_TOKEN
  || "3e7d80fdfed273606f4c76ff8b24f98b098d2f129a31e399";

// Deterministic demo tokens for every seeded role in TEN_NORTHBRIDGE at the
// default SEED=42. NOT real credentials -- see LIMITATIONS.md.
export const DEMO_TOKENS: Record<string, string> = {
  ANALYST: "a043bae1603803a839c0cb52f511d9cb8f68d9d9b0341314",
  INVESTIGATOR: "a5534ea92b26fa8adc30543fe5a6e743849e63f8101ac616",
  FINANCE_OPERATOR: "f8fd0ba84a167fe482ed4a92c8c8050eed40ef171cc2784d",
  APPROVER: "638b34fa781359331a3ed13a32e97cc31667baf165d33764",
  ADMINISTRATOR: DEMO_TOKEN,
};

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  return requestAs<T>(DEMO_TOKEN, path, options);
}

async function requestAs<T>(token: string, path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`,
      ...(options?.headers || {}),
    },
    ...options,
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${body}`);
  }
  return res.json();
}

export const api = {
  getMerchantConnection: (merchantId: string) =>
    request<any>(`/merchant/${merchantId}/connection`),
  getMerchantBaseline: (merchantId: string) =>
    request<any>(`/merchant/${merchantId}/baseline`),

  listIncidents: () => request<any[]>(`/incidents`),
  getIncident: (incidentId: string) => request<any>(`/incident/${incidentId}`),
  getTimeline: (incidentId: string) => request<any[]>(`/incident/${incidentId}/timeline`),
  getGraph: (incidentId: string) => request<any>(`/incident/${incidentId}/graph`),
  getExposure: (incidentId: string) => request<any>(`/incident/${incidentId}/exposure`),
  getEvidence: (incidentId: string) => request<any>(`/incident/${incidentId}/evidence`),
  getNextQuestion: (incidentId: string) => request<any>(`/incident/${incidentId}/questions/next`),
  postAttestation: (incidentId: string, body: { question_id: string; answer: string; note?: string }) =>
    request<any>(`/incident/${incidentId}/attestation`, { method: "POST", body: JSON.stringify(body) }),
  getRecoveryPacket: (incidentId: string) => request<any>(`/incident/${incidentId}/recovery-packet`),
  getAudit: (incidentId: string) => request<any[]>(`/incident/${incidentId}/audit`),

  uploadEvidence: async (file: File, merchantId: string, incidentId: string, sourceLabel: string) => {
    const form = new FormData();
    form.append("file", file);
    form.append("merchant_id", merchantId);
    form.append("incident_id", incidentId);
    form.append("source_label", sourceLabel);
    const res = await fetch(`${BASE}/evidence/upload`, {
      method: "POST", body: form,
      headers: { "Authorization": `Bearer ${DEMO_TOKEN}` },
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },
  analyzeEvidence: async (artifactId: string) => {
    const form = new FormData();
    form.append("artifact_id", artifactId);
    const res = await fetch(`${BASE}/evidence/analyze`, {
      method: "POST", body: form,
      headers: { "Authorization": `Bearer ${DEMO_TOKEN}` },
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  injectIncident: (scenario: string, merchantId: string) =>
    request<any>(`/demo/inject-incident`, {
      method: "POST",
      body: JSON.stringify({ scenario, merchant_id: merchantId }),
    }),
  resetDemo: () => request<any>(`/demo/reset`, { method: "POST" }),

  getMetrics: () => request<any>(`/metrics`),
  getEvaluation: () => request<any>(`/evaluation`),

  // --- Recovery Command (propose/review/approve/reject/execute/verify) ---
  // These accept an explicit acting-role token so the UI can demonstrate
  // real RBAC enforcement (e.g. an Investigator token genuinely cannot
  // approve) rather than always acting as the one admin demo user.
  listRecoveryCommands: (incidentId: string) =>
    request<any[]>(`/incident/${incidentId}/recovery-commands`),
  proposeRecoveryCommand: (incidentId: string, body: any, actingToken: string) =>
    requestAs<any>(actingToken, `/incident/${incidentId}/recovery-commands`, {
      method: "POST", body: JSON.stringify(body),
    }),
  dryRunCommand: (commandId: string, actingToken: string) =>
    requestAs<any>(actingToken, `/recovery-commands/${commandId}/dry-run`, { method: "POST" }),
  reviewCommand: (commandId: string, actingToken: string) =>
    requestAs<any>(actingToken, `/recovery-commands/${commandId}/review`, { method: "POST" }),
  approveCommand: (commandId: string, actingToken: string) =>
    requestAs<any>(actingToken, `/recovery-commands/${commandId}/approve`, { method: "POST" }),
  rejectCommand: (commandId: string, actingToken: string, reason: string) =>
    requestAs<any>(actingToken, `/recovery-commands/${commandId}/reject`, {
      method: "POST", body: JSON.stringify({ reason }),
    }),
  executeCommand: (commandId: string, actingToken: string) =>
    requestAs<any>(actingToken, `/recovery-commands/${commandId}/execute`, { method: "POST" }),
  verifyCommand: (commandId: string, actingToken: string) =>
    requestAs<any>(actingToken, `/recovery-commands/${commandId}/verify`, { method: "POST" }),
  getConvergence: (commandId: string) =>
    request<any>(`/recovery-commands/${commandId}/convergence`),
};

export const FLAGSHIP_MERCHANT_ID = "MER_ARROW";
export const CHAOS_MERCHANT_ID = "MER_HARBOR";
export const FLAGSHIP_INCIDENT_ID = "INC-001";
