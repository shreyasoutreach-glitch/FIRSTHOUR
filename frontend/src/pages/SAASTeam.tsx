import React, { useState } from "react";
import { Link } from "react-router-dom";
import { ShieldCheck, UserRound, LockKeyhole, ArrowRight, Mail, Copy, Check } from "lucide-react";

export default function SAASTeam() {
 const workspace=sessionStorage.getItem("primhora_workspace");
 const [email,setEmail]=useState(""); const [role,setRole]=useState("ANALYST"); const [created,setCreated]=useState(false);
 const roles=[[ "ANALYST","View cases and evidence",UserRound ],[ "INVESTIGATOR","Investigate and recommend",ShieldCheck ],[ "APPROVER","Review and approve recovery",LockKeyhole ]];
 const invite=()=>{if(email.trim())setCreated(true)};
 return <div className="min-h-[calc(100vh-56px)] bg-graphite text-text_primary"><div className="max-w-canvas mx-auto px-5 sm:px-10 py-10">
  <p className="label-eyebrow text-text_primary/35">Administration · Team</p><h1 className="font-display text-4xl mt-2">Controls & separation of duties</h1>
  <p className="text-sm text-text_primary/45 mt-2 max-w-2xl">Define responsibilities without implying that an identity provider or invitation service is connected when it isn't.</p>
  {!workspace ? <div className="mt-8 panel p-10 max-w-2xl"><ShieldCheck size={20}/><h2 className="font-display text-2xl mt-6">Create your organization first</h2><p className="text-sm text-text_primary/45 mt-2">Team membership belongs to an organization.</p><Link to="/app" className="inline-flex items-center gap-2 mt-6 rounded-xl bg-text_primary text-graphite px-5 py-3 text-sm font-medium">Set up workspace <ArrowRight size={14}/></Link></div> :
  <div className="mt-8 grid lg:grid-cols-[1fr_360px] gap-5">
   <section><div className="grid md:grid-cols-3 gap-4">{roles.map(([role,copy,Icon]:any)=><div key={role} className="panel p-6"><Icon size={18}/><p className="font-ui text-sm mt-8">{role}</p><p className="text-xs text-text_primary/45 mt-2">{copy}</p><span className="status-pill border-surface_border text-text_primary/30 mt-5">No members</span></div>)}</div></section>
   <aside className="panel p-6"><p className="label-eyebrow text-text_primary/35">Invitation preview</p><h2 className="font-display text-2xl mt-3">Prepare a member invite</h2><p className="text-xs leading-relaxed text-text_primary/40 mt-2">This environment does not have email delivery or production identity provisioning. We will not pretend an invitation was sent.</p>
    <label className="block text-xs text-text_primary/50 mt-6">Email<input value={email} onChange={e=>{setEmail(e.target.value);setCreated(false)}} placeholder="finance@example.com" type="email" className="mt-2 w-full rounded-lg border border-surface_border bg-graphite px-3 py-3 text-sm focus-ring"/></label>
    <label className="block text-xs text-text_primary/50 mt-4">Role<select value={role} onChange={e=>setRole(e.target.value)} className="mt-2 w-full rounded-lg border border-surface_border bg-graphite px-3 py-3 text-sm focus-ring">{roles.map(([r]:any)=><option key={r}>{r}</option>)}</select></label>
    <button disabled={!email.trim()} onClick={invite} className="mt-5 inline-flex items-center gap-2 rounded-lg bg-text_primary text-graphite px-4 py-2.5 text-sm font-medium disabled:opacity-30"><Mail size={14}/> Prepare invite</button>
    {created&&<div className="mt-4 rounded-xl border border-surface_border p-4"><div className="flex items-center gap-2 text-sm"><Check size={14}/> Draft ready</div><p className="text-xs text-text_primary/40 mt-2">No email was sent. Production invitations require an identity/email provider.</p><button onClick={()=>navigator.clipboard?.writeText(`Invite ${email} as ${role} to ${workspace}`)} className="mt-3 inline-flex items-center gap-2 text-xs text-text_primary/55 hover:text-text_primary"><Copy size={13}/> Copy draft</button></div>}
   </aside>
  </div>}
 </div></div>;
}