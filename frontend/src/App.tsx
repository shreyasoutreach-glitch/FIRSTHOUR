import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import AppShell from "./components/AppShell";
import { CaseProvider } from "./lib/CaseContext";
import { Auth0Provider } from "@auth0/auth0-react";
import AuthTokenInjector from "./components/AuthTokenInjector";

import Welcome from "./pages/Welcome";
import Connect from "./pages/Connect";
import EvidenceDrop from "./pages/EvidenceDrop";
import Reconstruction from "./pages/Reconstruction";
import TheIncident from "./pages/TheIncident";
import FinancialGraph from "./pages/FinancialGraph";
import HumanWitness from "./pages/HumanWitness";
import Exposure from "./pages/Exposure";
import RecoveryCommand from "./pages/RecoveryCommand";
import RecoveryPacket from "./pages/RecoveryPacket";
import Audit from "./pages/Audit";
import ChaosLab from "./pages/ChaosLab";

function InnerApp() {
  return (
    <CaseProvider>
      <BrowserRouter>
        <AppShell>
          <Routes>
            <Route path="/" element={<Welcome />} />
            <Route path="/connect" element={<Connect />} />
            <Route path="/evidence" element={<EvidenceDrop />} />
            <Route path="/reconstruction" element={<Reconstruction />} />
            <Route path="/incident" element={<TheIncident />} />
            <Route path="/graph" element={<FinancialGraph />} />
            <Route path="/witness" element={<HumanWitness />} />
            <Route path="/exposure" element={<Exposure />} />
            <Route path="/recovery" element={<RecoveryCommand />} />
            <Route path="/recovery/packet" element={<RecoveryPacket />} />
            <Route path="/audit" element={<Audit />} />
            <Route path="/chaos-lab" element={<ChaosLab />} />
          </Routes>
        </AppShell>
      </BrowserRouter>
    </CaseProvider>
  );
}

export default function App() {
  const domain = import.meta.env.VITE_AUTH0_DOMAIN;
  const clientId = import.meta.env.VITE_AUTH0_CLIENT_ID;
  const audience = import.meta.env.VITE_AUTH0_AUDIENCE;
  
  if (domain && clientId) {
    return (
      <Auth0Provider
        domain={domain}
        clientId={clientId}
        authorizationParams={{
          redirect_uri: window.location.origin,
          audience: audience
        }}
      >
        <AuthTokenInjector>
          <InnerApp />
        </AuthTokenInjector>
      </Auth0Provider>
    );
  }

  // Fallback for DEMO_MODE without Auth0 configuration
  return <InnerApp />;
}
