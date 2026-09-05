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
 */
const BASE = import.meta.env.VITE_API_BASE_URL || "/api";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(options?.headers || {}) },
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
    const res = await fetch(`${BASE}/evidence/upload`, { method: "POST", body: form });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },
  analyzeEvidence: async (artifactId: string) => {
    const form = new FormData();
    form.append("artifact_id", artifactId);
    const res = await fetch(`${BASE}/evidence/analyze`, { method: "POST", body: form });
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
};

export const FLAGSHIP_MERCHANT_ID = "MER_ARROW";
export const CHAOS_MERCHANT_ID = "MER_HARBOR";
export const FLAGSHIP_INCIDENT_ID = "INC-001";
