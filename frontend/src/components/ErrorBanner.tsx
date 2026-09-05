import React from "react";
import { AlertTriangle } from "lucide-react";

export default function ErrorBanner({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="paper-card border border-vermillion/30 px-6 py-5 max-w-[640px] mb-8 flex items-start gap-3">
      <AlertTriangle size={17} className="text-vermillion mt-0.5 shrink-0" />
      <div>
        <p className="text-[13px] text-vermillion mb-1">We couldn&rsquo;t load this from the server.</p>
        <p className="text-[12px] text-forest/50 break-all">{message}</p>
        {onRetry && (
          <button onClick={onRetry} className="text-[12px] font-ui text-forest underline underline-offset-2 mt-2">
            Try again
          </button>
        )}
      </div>
    </div>
  );
}
