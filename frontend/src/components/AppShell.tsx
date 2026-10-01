import React from "react";
import { Link, useLocation } from "react-router-dom";
import { Menu, X } from "lucide-react";
import { logout } from "../lib/auth";

const STEPS=[{path:"/",label:"Overview"},{path:"/connect",label:"Connect"},{path:"/evidence",label:"Evidence"},{path:"/reconstruction",label:"Reconstruction"},{path:"/incident",label:"Incident"},{path:"/graph",label:"Graph"},{path:"/witness",label:"Human Witness"},{path:"/exposure",label:"Exposure"},{path:"/recovery",label:"Recovery"}];

export default function AppShell({children}:{children:React.ReactNode}){
  const location=useLocation();
  const isLanding=location.pathname==="/";
  const isSaaS=location.pathname.startsWith("/app");
  const [mobileOpen,setMobileOpen]=React.useState(false);

  React.useEffect(()=>setMobileOpen(false),[location.pathname]);

  if(isSaaS){
    const links=[["/app","Overview"],["/app/incidents","Incidents"],["/app/data-sources","Data sources"],["/app/team","Team"]];
    return <div className="min-h-screen bg-graphite text-text_primary">
      <header className="sticky top-0 z-40 border-b border-surface_border bg-graphite/95 backdrop-blur-md">
        <div className="max-w-canvas mx-auto px-5 sm:px-10 h-16 flex items-center justify-between gap-6">
          <Link to="/app" className="flex items-baseline gap-2.5 shrink-0"><span className="font-display text-[17px] tracking-tight">PRIMHORA</span><span className="label-eyebrow text-text_primary/30 hidden sm:inline">Operations</span></Link>
          <nav className="hidden md:flex items-center gap-6 text-[12px] text-text_primary/45">{links.map(([href,label])=><Link key={href} className={location.pathname===href||location.pathname.startsWith(href+"/")?"text-text_primary":"hover:text-text_primary"} to={href}>{label}</Link>)}</nav>
          <div className="flex items-center gap-3"><span className="hidden sm:inline status-pill border-amber/25 text-amber/70">Workspace</span><button aria-label="Open workspace navigation" onClick={()=>setMobileOpen(v=>!v)} className="md:hidden p-2 rounded-lg border border-surface_border focus-ring">{mobileOpen?<X size={16}/>:<Menu size={16}/>}</button><button onClick={logout} className="text-xs text-text_primary/45 hover:text-text_primary" aria-label="Sign out">Sign out</button></div>
        </div>
        {mobileOpen&&<nav className="md:hidden border-t border-surface_border px-5 py-3 bg-graphite">{links.map(([href,label])=><Link key={href} to={href} className="block py-3 text-sm text-text_primary/60">{label}</Link>)}</nav>}
      </header><main>{children}</main>
    </div>;
  }

  return <div className={isLanding?"min-h-screen bg-text_primary text-graphite":"min-h-screen bg-graphite text-text_primary"}>
    <header className={`sticky top-0 z-40 border-b ${isLanding?"border-graphite/10 bg-text_primary/90":"border-surface_border bg-graphite/95"} backdrop-blur-md`}>
      <div className="max-w-canvas mx-auto flex items-center justify-between px-5 py-3 sm:px-10">
        <Link to="/" className="flex items-baseline gap-2.5"><span className="font-display text-[17px] tracking-tight">PRIMHORA</span><span className={`label-eyebrow ${isLanding?"text-graphite/40":"text-text_primary/35"}`}>Financial incident response</span></Link>
        <nav className="flex items-center gap-5">{!isLanding&&<Link to="/audit" className="text-[13px] text-text_primary/55 hover:text-text_primary">Audit</Link>}{!isLanding&&location.pathname!=="/demo/setup"&&<Link to="/demo/setup" className="text-[13px] text-text_primary/55 hover:text-text_primary">Restart demo</Link>}</nav>
      </div>
    </header><main>{children}</main>
  </div>
}
export function StepFooter({current}:{current:string}){const idx=STEPS.findIndex(s=>s.path===current);if(idx===-1)return null;return <div className="max-w-canvas mx-auto px-5 sm:px-10 py-6"><ol className="flex flex-wrap gap-x-2 gap-y-1 text-[12px] font-ui text-text_primary/40">{STEPS.map((s,i)=><li key={s.path} className="flex items-center gap-2"><span className={i===idx?"text-text_primary font-medium":i<idx?"text-text_primary/60":""}>{s.label}</span>{i<STEPS.length-1&&<span aria-hidden>→</span>}</li>)}</ol></div>}
