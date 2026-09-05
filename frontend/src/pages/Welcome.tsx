import React from "react";
import { useNavigate } from "react-router-dom";

const STEPS = ["Gather", "Reconstruct", "Review"];

export default function Welcome() {
  const navigate = useNavigate();

  return (
    <div className="min-h-[calc(100vh-56px)] flex flex-col items-center justify-center px-6">
      <div className="w-full max-w-[560px] bg-ivory text-forest rounded-[3px] shadow-raised px-10 py-12 sm:px-14 sm:py-16">
        <p className="label-eyebrow mb-6">First Hour</p>
        <h1 className="font-display text-[34px] sm:text-[40px] leading-[1.08] mb-5">
          Let&rsquo;s get this organized.
        </h1>
        <p className="text-[15px] leading-relaxed text-forest/70 mb-10 max-w-[420px]">
          You do not need to remember everything. Give us what you have, and we&rsquo;ll build the
          case with you &mdash; one clear step at a time.
        </p>

        <div className="flex flex-col sm:flex-row gap-3 mb-12">
          <button className="btn-primary" onClick={() => navigate("/connect")}>
            Start recovery
          </button>
          <button className="btn-secondary" onClick={() => navigate("/connect")}>
            Connect Razorpay
          </button>
        </div>

        <ol className="flex items-center gap-3 text-[12px] font-ui text-forest/45">
          {STEPS.map((step, i) => (
            <li key={step} className="flex items-center gap-3">
              <span>{step}</span>
              {i < STEPS.length - 1 && <span aria-hidden className="text-gold">&rarr;</span>}
            </li>
          ))}
        </ol>
      </div>
    </div>
  );
}
