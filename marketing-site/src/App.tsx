import React from 'react';
import { ShieldAlert, ArrowRight, Play, FileSearch, CheckCircle2, ShieldCheck } from 'lucide-react';

function App() {
  return (
    <div className="min-h-screen bg-[#07090E] text-[#F3F4F6] font-sans selection:bg-[#0066CC] selection:text-white">
      {/* Navigation */}
      <nav className="border-b border-white/5 bg-black/20 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-[#0066CC]" />
            <span className="font-semibold tracking-wide">FIRST HOUR</span>
          </div>
          <div className="flex items-center gap-6 text-sm">
            <a href="#platform" className="text-white/60 hover:text-white transition-colors">Platform</a>
            <a href="#architecture" className="text-white/60 hover:text-white transition-colors">Architecture</a>
            <button className="bg-white/10 hover:bg-white/20 px-4 py-2 rounded-full transition-colors font-medium">
              Request API Access
            </button>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <main className="relative overflow-hidden">
        {/* Glows */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-[#0066CC]/20 rounded-full blur-[120px] -z-10 pointer-events-none" />
        
        <div className="max-w-7xl mx-auto px-6 pt-32 pb-24 text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-[#0066CC]/30 bg-[#0066CC]/10 text-[#0066CC] text-xs font-semibold uppercase tracking-widest mb-8">
            The Incident Response Layer
          </div>
          <h1 className="text-5xl sm:text-7xl font-bold tracking-tight mb-8 leading-[1.1]">
            Financial incidents don't end<br/>
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-white to-white/40">
              when fraud is detected.
            </span>
          </h1>
          <p className="text-lg text-white/50 max-w-2xl mx-auto mb-12 leading-relaxed">
            FIRST HOUR reconstructs financial incidents from fragmented evidence, verifies claims against financial ledgers, and coordinates controlled recovery workflows.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <button className="bg-white text-black px-8 py-4 rounded-full font-medium hover:scale-105 active:scale-95 transition-all flex items-center gap-2">
              Request API Access <ArrowRight className="w-4 h-4" />
            </button>
            <a href="https://first-hour-app.vercel.app/" target="_blank" className="bg-white/5 border border-white/10 px-8 py-4 rounded-full font-medium hover:bg-white/10 active:scale-95 transition-all flex items-center gap-2">
              <Play className="w-4 h-4" /> View The Incident (Demo)
            </a>
          </div>
        </div>

        {/* Architecture Section */}
        <div id="architecture" className="max-w-7xl mx-auto px-6 py-24 border-t border-white/5">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold mb-4">Zero-Hallucination Architecture</h2>
            <p className="text-white/50 max-w-xl mx-auto">
              LLMs read unstructured text. Deterministic SQL engines verify the ledger. Humans authorize action.
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-white/[0.02] border border-white/5 rounded-3xl p-8 relative overflow-hidden group hover:border-[#0066CC]/30 transition-colors">
              <FileSearch className="w-10 h-10 text-[#0066CC] mb-6" />
              <h3 className="text-xl font-semibold mb-3">AI Interprets</h3>
              <p className="text-white/50 text-sm leading-relaxed">
                Gemini processes raw WhatsApp screenshots and unstructured emails, converting them into structured candidate claims.
              </p>
            </div>
            <div className="bg-white/[0.02] border border-white/5 rounded-3xl p-8 relative overflow-hidden group hover:border-emerald-500/30 transition-colors">
              <CheckCircle2 className="w-10 h-10 text-emerald-500 mb-6" />
              <h3 className="text-xl font-semibold mb-3">Ledger Verifies</h3>
              <p className="text-white/50 text-sm leading-relaxed">
                Candidate claims are cryptographically bound and strictly matched against Razorpay or Stripe actual transaction hashes.
              </p>
            </div>
            <div className="bg-white/[0.02] border border-white/5 rounded-3xl p-8 relative overflow-hidden group hover:border-amber-500/30 transition-colors">
              <ShieldCheck className="w-10 h-10 text-amber-500 mb-6" />
              <h3 className="text-xl font-semibold mb-3">Humans Authorize</h3>
              <p className="text-white/50 text-sm leading-relaxed">
                RBAC-controlled recovery commands separate Investigators (propose) from Finance Operators (approve & execute simulated reversals).
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
