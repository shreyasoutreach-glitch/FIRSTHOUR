import React from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { ShieldAlert, Server, Play, ChevronRight } from "lucide-react";

export default function Welcome() {
  const navigate = useNavigate();

  return (
    <div className="min-h-[calc(100vh-56px)] flex flex-col items-center justify-center px-6 relative overflow-hidden bg-charcoal text-parchment">
      {/* Royal Ambient Glow */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-gold/10 rounded-full blur-[120px] -z-10 pointer-events-none" />
      <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[600px] h-[400px] bg-champagne/10 rounded-full blur-[100px] -z-10 pointer-events-none" />

      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.7, ease: "easeOut" }}
        className="w-full max-w-[640px] text-center relative z-10"
      >
        {/* Animated Hero Icon */}
        <div className="mx-auto mb-8 relative flex items-center justify-center w-20 h-20 bg-parchment/5 rounded-3xl border border-parchment/10 backdrop-blur-xl shadow-raised">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
            className="absolute inset-0 rounded-3xl border border-gold/40 border-dashed"
          />
          <ShieldAlert className="w-10 h-10 text-gold" strokeWidth={1} />
        </div>

        <h1 className="font-display text-[44px] sm:text-[56px] leading-[1.05] mb-6 font-semibold tracking-tight bg-gradient-to-br from-parchment to-parchment/60 bg-clip-text text-transparent">
          First Hour.
        </h1>
        <p className="text-[17px] leading-relaxed text-parchment/60 mb-12 max-w-[480px] mx-auto font-ui font-light">
          The autonomous incident response layer for enterprise finance. Choose your environment to begin.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          {/* Demo Button */}
          <button 
            onClick={() => navigate("/connect?mode=demo")}
            className="group relative flex items-center justify-between gap-4 bg-parchment text-charcoal font-ui font-medium px-8 py-4 rounded-2xl transition-all hover:scale-[1.02] active:scale-[0.98] shadow-raised"
          >
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-charcoal/10 flex items-center justify-center">
                <Play className="w-4 h-4 text-charcoal" />
              </div>
              <div className="text-left">
                <div className="text-[15px]">Launch Demo</div>
                <div className="text-[12px] text-charcoal/60">Simulated mock ledger</div>
              </div>
            </div>
            <ChevronRight className="w-5 h-5 opacity-40 group-hover:opacity-100 transition-opacity" />
          </button>

          {/* Production Button */}
          <button 
            onClick={() => navigate("/connect?mode=production")}
            className="group relative flex items-center justify-between gap-4 bg-charcoal text-parchment font-ui font-medium px-8 py-4 rounded-2xl border border-parchment/10 transition-all hover:bg-parchment/5 hover:border-gold/30 active:scale-[0.98]"
          >
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-parchment/10 flex items-center justify-center">
                <Server className="w-4 h-4 text-gold" />
              </div>
              <div className="text-left">
                <div className="text-[15px]">Live Production</div>
                <div className="text-[12px] text-parchment/50">Connect real gateways</div>
              </div>
            </div>
            <ChevronRight className="w-5 h-5 text-gold opacity-40 group-hover:opacity-100 transition-opacity" />
          </button>
        </div>
      </motion.div>
    </div>
  );
}
