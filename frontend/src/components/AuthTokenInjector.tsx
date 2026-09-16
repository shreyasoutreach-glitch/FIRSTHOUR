import React, { useEffect } from "react";
import { useAuth0 } from "@auth0/auth0-react";
import { setAccessTokenProvider } from "../lib/api";

export default function AuthTokenInjector({ children }: { children: React.ReactNode }) {
  const { getAccessTokenSilently, isAuthenticated, loginWithRedirect, isLoading } = useAuth0();

  useEffect(() => {
    if (isAuthenticated) {
      setAccessTokenProvider(async () => {
        return await getAccessTokenSilently();
      });
    } else if (!isLoading) {
       loginWithRedirect();
    }
  }, [isAuthenticated, isLoading, getAccessTokenSilently, loginWithRedirect]);

  if (isLoading || !isAuthenticated) {
    return (
      <div style={{ display: 'flex', height: '100vh', alignItems: 'center', justifyContent: 'center', fontFamily: 'monospace' }}>
        Authenticating with Identity Provider...
      </div>
    );
  }

  return <>{children}</>;
}
