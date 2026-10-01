import React from "react";
import { BrowserRouter, Routes, Route, useLocation } from "react-router-dom";
import AppShell from "./components/AppShell";
import AuthGate from "./components/AuthGate";
import { CaseProvider } from "./lib/CaseContext";
import Welcome from "./pages/Welcome"; import DemoSetup from "./pages/DemoSetup"; import Connect from "./pages/Connect"; import EvidenceDrop from "./pages/EvidenceDrop"; import Reconstruction from "./pages/Reconstruction"; import TheIncident from "./pages/TheIncident"; import FinancialGraph from "./pages/FinancialGraph"; import HumanWitness from "./pages/HumanWitness"; import Exposure from "./pages/Exposure"; import RecoveryCommand from "./pages/RecoveryCommand"; import RecoveryPacket from "./pages/RecoveryPacket"; import Audit from "./pages/Audit"; import ChaosLab from "./pages/ChaosLab";
import SaaS from "./pages/SaaS"; import SaaSIncidents from "./pages/SaaSIncidents"; import SaaSIncident from "./pages/SaaSIncident"; import SaaSDataSources from "./pages/SaaSDataSources"; import SAASTeam from "./pages/SAASTeam";

function RouteTree() {
  const location = useLocation();
  const protectedWorkspace = location.pathname.startsWith("/app");

  return (
    <AppShell>
      {protectedWorkspace ? (
        <AuthGate>
          <Routes>
            <Route path="/app" element={<SaaS/>}/>
            <Route path="/app/incidents" element={<SaaSIncidents/>}/>
            <Route path="/app/incidents/:id" element={<SaaSIncident/>}/>
            <Route path="/app/data-sources" element={<SaaSDataSources/>}/>
            <Route path="/app/team" element={<SAASTeam/>}/>
          </Routes>
        </AuthGate>
      ) : (
        <Routes>
          <Route path="/" element={<Welcome/>}/>
          <Route path="/demo/setup" element={<DemoSetup/>}/>
          <Route path="/connect" element={<Connect/>}/>
          <Route path="/evidence" element={<EvidenceDrop/>}/>
          <Route path="/reconstruction" element={<Reconstruction/>}/>
          <Route path="/incident" element={<TheIncident/>}/>
          <Route path="/graph" element={<FinancialGraph/>}/>
          <Route path="/witness" element={<HumanWitness/>}/>
          <Route path="/exposure" element={<Exposure/>}/>
          <Route path="/recovery" element={<RecoveryCommand/>}/>
          <Route path="/recovery/packet" element={<RecoveryPacket/>}/>
          <Route path="/audit" element={<Audit/>}/>
          <Route path="/chaos-lab" element={<ChaosLab/>}/>
        </Routes>
      )}
    </AppShell>
  );
}

export default function App() {
  return (
    <CaseProvider>
      <BrowserRouter>
        <RouteTree />
      </BrowserRouter>
    </CaseProvider>
  );
}
