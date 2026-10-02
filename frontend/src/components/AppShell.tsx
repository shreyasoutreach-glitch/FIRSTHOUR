import React from "react";
import { Link, useLocation } from "react-router-dom";
import { Activity, Database, FileSearch, LayoutDashboard, Menu, ShieldCheck, Users, X, Zap, ArrowUpRight } from "lucide-react";
import { logout } from "../lib/auth";

const LINKS = [
  ["/app","Command Center",LayoutDashboard],
  ["/app/incidents","Incidents",FileSearch],
  ["/app/data-sources","Data Sources",Database],
  ["/app/team","Team & Controls",Users],
] as const;

export default function AppShell({children}:{children:React.ReactNode}) {
  const location = useLocation();
  const isLanding = location.pathname === "/";
  const isSaaS = location.pathname.startsWith("/app");
  const [mobileOpen,setMobileOpen] = React.useState(false);
  React.useEffect(()=>setMobileOpen(false),[location.pathname]);

  if (isSaaS) return <div className="min-h-screen bg-graphite text-text_primary">
    <aside className="fixed inset-y-0 left-0 z-50 hidden w-[248px] border-r border-violet/10 bg-[#0b0a1c] lg:flex lg:flex-col">
      <div className="px-6 pt-7 pb-6"><Link to="/app" className="flex items-center gap-3"><span className="flex h-9 w-9 items-center justify-center rounded-xl border border-violet/20 bg-violet/[0.07]"><Zap size={15} className="text-cyan"/></span><span><span className="block font-display text-[17px] tracking-tight">PRIMHORA</span><span className="label-eyebrow text-text_primary/25">Incident intelligence</span></span></Link></div>
      <nav className="px-3 space-y-1"><p className="label-eyebrow px-3 py-3 text-text_primary/20">Workspace</p>{LINKS.map(([href,label,Icon])=><Link key={href} to={href} className={location.pathname===href||location.pathname.startsWith(href+"/")?"nav-item nav-item-active":"nav-item"}><Icon size={16}/><span>{label}</span>{href==="/app/incidents"&&<span className="ml-auto h-1.5 w-1.5 rounded-full bg-amber"/>}</Link>)}</nav>
      <div className="mt-auto p-4"><div className="rounded-2xl border border-cyan/10 bg-cyan/[0.035] p-4"><div className="flex items-center gap-2"><span className="status-dot bg-emerald"/><span className="label-eyebrow text-cyan/80">System nominal</span></div><p className="mt-3 text-[11px] leading-relaxed text-text_primary/35">Read-only controls active. No money movement is permitted.</p></div><button onClick={logout} className="mt-4 w-full rounded-xl border border-surface_border px-3 py-2.5 text-left text-xs text-text_primary/40 hover:text-text_primary hover:bg-violet/[0.05] transition">Sign out</button></div>
    </aside>
    <header className="sticky top-0 z-40 border-b border-violet/10 bg-[#0b0a1c]/90 backdrop-blur-xl lg:ml-[248px]"><div className="mx-auto flex h-[72px] max-w-[1500px] items-center justify-between px-5 sm:px-8"><div className="lg:hidden"><Link to="/app" className="font-display tracking-tight">PRIMHORA</Link></div><div className="hidden lg:flex items-center gap-2 text-xs text-text_primary/35"><Activity size={13} className="text-cyan/70"/><span>Operations control plane</span><span className="text-text_primary/15">/</span><span>{sessionStorage.getItem("primhora_workspace")||"Workspace"}</span></div><div className="flex items-center gap-3"><span className="hidden sm:inline-flex status-pill border-cyan/20 text-cyan/75"><span className="status-dot bg-cyan mr-2"/> Read-only safe mode</span><button aria-label="Open workspace navigation" onClick={()=>setMobileOpen(v=>!v)} className="lg:hidden rounded-xl border border-surface_border p-2.5">{mobileOpen?<X size={16}/>:<Menu size={16}/>}</button></div></div>{mobileOpen&&<nav className="lg:hidden border-t border-violet/10 bg-[#0b0a1c] p-3 space-y-1">{LINKS.map(([href,label,Icon])=><Link key={href} to={href} className="nav-item"><Icon size={16}/><span>{label}</span></Link>)}</nav>}</header>
    <main className="lg:ml-[248px]">{children}</main>
  </div>;

  return <div className={isLanding?"min-h-screen bg-[#070611] text-white":"min-h-screen bg-graphite text-text_primary"}>
    <header className={"sticky top-0 z-40 border-b "+(isLanding?"border-white/10 bg-[#080713]/75 text-white":"border-surface_border bg-graphite/95")+" backdrop-blur-xl"}>
      <div className="mx-auto flex h-16 max-w-canvas items-center justify-between px-5 sm:px-10">
        <Link to="/" className="group flex items-center gap-3"><span className="flex h-8 w-8 items-center justify-center rounded-lg border border-white/10 bg-white/[0.03] transition group-hover:-rotate-3 group-hover:border-violet-300/30"><ShieldCheck size={14}/></span><span className="font-display text-[17px] tracking-tight">PRIMHORA</span><span className="label-eyebrow hidden sm:inline text-white/35">Financial incident intelligence</span></Link>
        <nav className="flex items-center gap-2">{isLanding&&<a href="#how-it-works" className="hidden rounded-lg px-3 py-2 text-[12px] text-white/45 transition hover:bg-white/[0.04] hover:text-white sm:inline-flex">How it works</a>}{!isLanding&&<Link to="/audit" className="rounded-lg px-3 py-2 text-[13px] text-text_primary/50 hover:bg-white/[0.03] hover:text-text_primary">Audit</Link>}{!isLanding&&<Link to="/demo/setup" className="rounded-lg px-3 py-2 text-[13px] text-text_primary/50 hover:bg-white/[0.03] hover:text-text_primary">Synthetic demo</Link>}{isLanding&&<Link to="/demo/setup" className="hidden items-center gap-2 rounded-lg border border-violet-300/20 bg-violet-400/10 px-3.5 py-2 text-[12px] font-medium text-violet-100 transition hover:bg-violet-400/20 sm:inline-flex">Enter demo <ArrowUpRight size={13}/></Link>}</nav>
      </div>
    </header>
    <main>{children}</main>
  </div>;
}
export function StepFooter({current}:{current:string}){return null}
