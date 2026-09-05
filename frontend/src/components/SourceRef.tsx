import React, { useState } from "react";

/** Small clickable provenance affordance. Every material claim in the app
 * carries one of these instead of being presented as free-floating text. */
export default function SourceRef({ id, label }: { id: string; label?: string }) {
  const [open, setOpen] = useState(false);
  return (
    <span className="relative inline-block">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="ml-1.5 align-middle text-[11px] font-ui text-gold border border-gold/40 rounded-full
                   px-1.5 py-0.5 hover:bg-gold/10 transition-colors duration-250
                   focus-visible:outline focus-visible:outline-2 focus-visible:outline-gold"
        aria-label={`View source for ${label ?? id}`}
        aria-expanded={open}
      >
        source
      </button>
      {open && (
        <span
          role="tooltip"
          className="absolute z-50 left-0 top-full mt-1 whitespace-nowrap bg-forest text-ivory text-[12px]
                     font-ui px-3 py-1.5 rounded-[2px] shadow-raised"
        >
          {label ? `${label}: ` : ""}
          {id}
        </span>
      )}
    </span>
  );
}
