import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import AppShell from "./components/AppShell";
import { CaseProvider } from "./lib/CaseContext";

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

export default function App() {
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
