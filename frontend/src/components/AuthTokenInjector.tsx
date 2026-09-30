import React from "react";

/**
 * Production identity is intentionally not hard-wired to a vendor in the
 * frontend. The API client accepts an access-token provider when the real
 * identity layer is configured. Until then, the product remains in its
 * explicitly labelled demo mode.
 */
export default function AuthTokenInjector({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
