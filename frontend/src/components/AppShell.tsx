import React from "react";
import { Link, useLocation } from "react-router-dom";

const STEPS = [
  { path: "/", label: "Overview" }, { path: "/connect", label: "Connect" },
  { path: "/evidence", label: "Evidence" }, { path: "/reconstruction", label: "Reconstruction" },
  { path: "/incident", label: "Incident" }, { path: "/graph", label: "Graph" },
  { path: "/witness", label: "Human Witness" }, { path: "/exposure", label: "Exposure" },
  { path: "/recovery", label: "Recovery" },
];

export default function AppShell({ children }: { children: React.ReactNode }) {
  const location = useLocation();
  const isLanding = location.pathname === "/";
  return (
    <div className={isLanding ? "min-h-screen bg-text_primary text-graphite" : "min-h-screen bg-graphite text-text_primary"}>
      <header className={`sticky top-0 z-40 border-b ${isLanding ? "border-graphite/10 bg-text_primary/90" : "border-forest/10 bg-graphite/95"} backdrop-blur-md`}>
        <div className="max-w-canvas mx-auto flex items-center justify-between px-6 py-3 sm:px-10">
          <Link to="/" className="flex items-baseline gap-2.5">
            <span className="font-display text-[17px] tracking-tight">PRIMHORA</span>
            <span className={`label-eyebrow ${isLanding ? "text-graphite/40" : "text-text_primary/35"}`}>
              Financial incident response
            </span>
          </Link>
          <nav className="flex items-center gap-5">
            {!isLanding && <Link to="/audit" className="text-[13px] font-ui text-text_primary/55 hover:text-text_primary">Audit</Link>}
            {!isLanding && location.pathname !== "/demo/setup" && (
              <Link to="/demo/setup" className="text-[13px] font-ui text-text_primary/55 hover:text-text_primary">Restart demo</Link>
            )}
          </nav>
        </div>
      </header>
      <main>{children}</main>
    </div>
  );
}

export function StepFooter({ current }: { current: string }) {
  const idx = STEPS.findIndex((s) => s.path === current);
  if (idx === -1) return null;
  return <div className="max-w-canvas mx-auto px-6 sm:px-10 py-6">
    <ol className="flex flex-wrap gap-x-2 gap-y-1 text-[12px] font-ui text-text_primary/40">
      {STEPS.map((s, i) => <li key={s.path} className="flex items-center gap-2">
        <span className={i === idx ? "text-text_primary font-medium" : i < idx ? "text-text_primary/60" : ""}>{s.label}</span>
        {i < STEPS.length - 1 && <span aria-hidden>→</span>}
      </li>)}
    </ol>
  </div>;
}