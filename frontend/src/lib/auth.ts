const DOMAIN = (import.meta.env.VITE_AUTH0_DOMAIN || "").trim();
const CLIENT_ID = (import.meta.env.VITE_AUTH0_CLIENT_ID || "").trim();
const AUDIENCE = (import.meta.env.VITE_AUTH0_AUDIENCE || "").trim();
const REQUIRED = String(import.meta.env.VITE_AUTH_REQUIRED || "false").toLowerCase() === "true";

const STATE_KEY = "primhora_oidc_state";
const VERIFIER_KEY = "primhora_oidc_verifier";
const RETURN_KEY = "primhora_oidc_return_to";

let accessToken = "";
let accessTokenExpiresAt = 0;

function base64Url(bytes: Uint8Array): string {
  let binary = "";
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/g, "");
}

function randomString(bytes = 32): string {
  const data = new Uint8Array(bytes);
  crypto.getRandomValues(data);
  return base64Url(data);
}

async function sha256(value: string): Promise<string> {
  const data = new TextEncoder().encode(value);
  return base64Url(new Uint8Array(await crypto.subtle.digest("SHA-256", data)));
}

function redirectUri(): string {
  return `${window.location.origin}/app`;
}

function safeReturnTo(value: string | null): string {
  if (!value || !value.startsWith("/") || value.startsWith("//")) return "/app";
  return value;
}

function parseExpiry(token: string): number {
  try {
    const encoded = token.split(".")[1];
    if (!encoded) return 0;
    const padded = encoded.replace(/-/g, "+").replace(/_/g, "/").padEnd(Math.ceil(encoded.length / 4) * 4, "=");
    const payload = JSON.parse(atob(padded));
    return Number(payload.exp || 0) * 1000;
  } catch {
    return 0;
  }
}

export function authConfigured(): boolean {
  return Boolean(DOMAIN && CLIENT_ID && AUDIENCE);
}

export function authRequired(): boolean {
  return REQUIRED;
}

export function authProviderName(): string {
  return DOMAIN || "Identity Provider";
}

export async function login(returnTo = window.location.pathname + window.location.search): Promise<never> {
  if (!authConfigured()) throw new Error("Production authentication is not configured.");

  const state = randomString(24);
  const verifier = randomString(48);
  const challenge = await sha256(verifier);
  sessionStorage.setItem(STATE_KEY, state);
  sessionStorage.setItem(VERIFIER_KEY, verifier);
  sessionStorage.setItem(RETURN_KEY, safeReturnTo(returnTo));

  const params = new URLSearchParams({
    response_type: "code",
    client_id: CLIENT_ID,
    redirect_uri: redirectUri(),
    scope: "openid profile email",
    audience: AUDIENCE,
    state,
    code_challenge: challenge,
    code_challenge_method: "S256",
  });
  window.location.assign(`https://${DOMAIN}/authorize?${params.toString()}`);
  throw new Error("Redirecting to identity provider");
}

export async function handleCallback(): Promise<boolean> {
  const params = new URLSearchParams(window.location.search);
  const code = params.get("code");
  const returnedState = params.get("state");
  const error = params.get("error");
  if (error) throw new Error(params.get("error_description") || error);
  if (!code) return false;

  const expectedState = sessionStorage.getItem(STATE_KEY);
  const verifier = sessionStorage.getItem(VERIFIER_KEY);
  if (!expectedState || !verifier || !returnedState || returnedState !== expectedState) {
    throw new Error("Authentication state validation failed. Please start login again.");
  }

  const body = new URLSearchParams({
    grant_type: "authorization_code",
    client_id: CLIENT_ID,
    code,
    redirect_uri: redirectUri(),
    code_verifier: verifier,
  });

  const response = await fetch(`https://${DOMAIN}/oauth/token`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
  if (!response.ok) {
    let detail = "Identity provider token exchange failed.";
    try {
      const data = await response.json();
      detail = data.error_description || data.error || detail;
    } catch {}
    throw new Error(detail);
  }

  const data = await response.json();
  if (!data.access_token) throw new Error("Identity provider returned no access token.");
  accessToken = data.access_token;
  accessTokenExpiresAt = parseExpiry(accessToken) || Date.now() + Number(data.expires_in || 3600) * 1000;
  sessionStorage.removeItem(STATE_KEY);
  sessionStorage.removeItem(VERIFIER_KEY);
  return true;
}

export function getAccessToken(): string {
  if (!accessToken || (accessTokenExpiresAt && Date.now() >= accessTokenExpiresAt - 30_000)) {
    throw new Error("Authentication session expired.");
  }
  return accessToken;
}

export function getReturnTo(): string {
  return safeReturnTo(sessionStorage.getItem(RETURN_KEY));
}

export function clearReturnTo(): void {
  sessionStorage.removeItem(RETURN_KEY);
}

export function logout(): void {
  accessToken = "";
  accessTokenExpiresAt = 0;
  sessionStorage.removeItem(STATE_KEY);
  sessionStorage.removeItem(VERIFIER_KEY);
  sessionStorage.removeItem(RETURN_KEY);
  if (!authConfigured()) {
    window.location.assign("/");
    return;
  }
  const params = new URLSearchParams({ client_id: CLIENT_ID, returnTo: window.location.origin + "/" });
  window.location.assign(`https://${DOMAIN}/v2/logout?${params.toString()}`);
}
