import React from "react";
import { Link, useLocation } from "react-router-dom";

const STEPS = [
  { path: "/", label: "Welcome" },
  { path: "/connect", label: "Connect" },
  { path: "/evidence", label: "Evidence" },
  { path: "/reconstruction", label: "Reconstruction" },
  { path: "/incident", label: "The Incident" },
  { path: "/graph", label: "Graph" },
  { path: "/witness", label: "Human Witness" },
  { path: "/exposure", label: "Exposure" },
  { path: "/recovery", label: "Recovery" },
];

export default function AppShell({ children }: { children: React.ReactNode }) {
  const location = useLocation();
  const isDark = location.pathname === "/";

  return (
    <div className={isDark ? "min-h-screen bg-text_primary text-graphite" : "min-h-screen bg-graphite text-text_primary"}>
      <header
        className={`sticky top-0 z-40 border-b ${
          isDark ? "border-ivory/10 bg-text_primary/95" : "border-forest/10 bg-graphite/95"
        } backdrop-blur-sm`}
      >
        <div className="max-w-canvas mx-auto flex items-center justify-between px-6 py-3 sm:px-10">
          <Link to="/" className="flex items-baseline gap-2.5">
            <span className="font-display text-[17px] tracking-tight">FIRST HOUR</span>
            <span className={`label-eyebrow ${isDark ? "text-graphite/50" : ""}`}>
              Private case &middot; Demo workspace
            </span>
          </Link>
          <nav className="flex items-center gap-5">
            <Link
              to="/audit"
              className={`text-[13px] font-ui transition-colors ${
                isDark ? "text-graphite/60 hover:text-graphite" : "text-text_primary/55 hover:text-text_primary"
              } ${location.pathname === "/audit" ? "underline underline-offset-4" : ""}`}
            >
              Audit
            </Link>
            <Link
              to="/chaos-lab"
              className={`text-[13px] font-ui transition-colors ${
                isDark ? "text-graphite/60 hover:text-graphite" : "text-text_primary/55 hover:text-text_primary"
              } ${location.pathname === "/chaos-lab" ? "underline underline-offset-4" : ""}`}
            >
              Chaos Lab
            </Link>
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
  return (
    <div className="max-w-canvas mx-auto px-6 sm:px-10 py-6">
      <ol className="flex flex-wrap gap-x-2 gap-y-1 text-[12px] font-ui text-text_primary/40">
        {STEPS.map((s, i) => (
          <li key={s.path} className="flex items-center gap-2">
            <span className={i === idx ? "text-text_primary font-medium" : i < idx ? "text-text_primary/60" : ""}>
              {s.label}
            </span>
            {i < STEPS.length - 1 && <span aria-hidden>&rarr;</span>}
          </li>
        ))}
      </ol>
    </div>
  );
}

