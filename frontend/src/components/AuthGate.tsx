import React from "react";
import { useNavigate } from "react-router-dom";
import { getAccessToken, authConfigured, authRequired, authProviderName, handleCallback, login, logout, getReturnTo, clearReturnTo } from "../lib/auth";
import { setAccessTokenProvider } from "../lib/api";

type Status = "loading" | "ready" | "error";

export default function AuthGate({ children }: { children: React.ReactNode }) {
  const navigate = useNavigate();
  const [status, setStatus] = React.useState<Status>("loading");
  const [message, setMessage] = React.useState("");

  React.useEffect(() => {
    let active = true;
    (async () => {
      try {
        if (!authRequired()) {
          setStatus("ready");
          return;
        }
        if (!authConfigured()) {
          throw new Error("Production authentication is required but the Vercel authentication variables are missing.");
        }

        const completed = await handleCallback();
        if (completed) {
          const destination = getReturnTo();
          clearReturnTo();
          navigate(destination, { replace: true });
        } else {
          try {
            getAccessToken();
          } catch {
            await login(window.location.pathname + window.location.search);
            return;
          }
        }

        setAccessTokenProvider(async () => getAccessToken());
        if (active) setStatus("ready");
      } catch (error: any) {
        if (!active) return;
        setMessage(error?.message || "Authentication could not be completed.");
        setStatus("error");
      }
    })();
    return () => { active = false; };
  }, [navigate]);

  if (status === "ready") return <>{children}</>;

  if (status === "error") {
    return (
      <div className="min-h-screen bg-graphite text-text_primary flex items-center justify-center px-6">
        <div className="w-full max-w-md rounded-2xl border border-surface_border bg-surface p-7">
          <p className="label-eyebrow text-text_primary/35">AUTHENTICATION</p>
          <h1 className="font-display text-3xl mt-3">Secure sign-in unavailable.</h1>
          <p className="text-sm leading-relaxed text-text_primary/50 mt-4">{message}</p>
          <div className="flex gap-3 mt-7">
            {authConfigured() && <button onClick={() => login(window.location.pathname)} className="rounded-lg bg-text_primary text-graphite px-4 py-2.5 text-sm font-medium">Try sign in</button>}
            <button onClick={() => logout()} className="rounded-lg border border-surface_border px-4 py-2.5 text-sm text-text_primary/60">Return home</button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-graphite text-text_primary flex items-center justify-center px-6">
      <div className="text-center max-w-sm">
        <div className="mx-auto mb-5 h-9 w-9 rounded-full border border-text_primary/20 border-t-text_primary animate-spin" />
        <p className="label-eyebrow text-text_primary/35">SECURE ACCESS</p>
        <p className="font-display text-2xl mt-3">Authenticating with {authProviderName()}.</p>
        <p className="text-sm text-text_primary/40 mt-3">Your session is established before workspace data is requested.</p>
      </div>
    </div>
  );
}
