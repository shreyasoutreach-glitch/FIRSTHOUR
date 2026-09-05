import React, { createContext, useContext, useState } from "react";
import { FLAGSHIP_INCIDENT_ID, FLAGSHIP_MERCHANT_ID } from "./api";

interface CaseState {
  merchantId: string;
  incidentId: string;
  setMerchantId: (id: string) => void;
  setIncidentId: (id: string) => void;
}

const CaseContext = createContext<CaseState | null>(null);

export function CaseProvider({ children }: { children: React.ReactNode }) {
  const [merchantId, setMerchantId] = useState(FLAGSHIP_MERCHANT_ID);
  const [incidentId, setIncidentId] = useState(FLAGSHIP_INCIDENT_ID);
  return (
    <CaseContext.Provider value={{ merchantId, incidentId, setMerchantId, setIncidentId }}>
      {children}
    </CaseContext.Provider>
  );
}

export function useCase(): CaseState {
  const ctx = useContext(CaseContext);
  if (!ctx) throw new Error("useCase must be used within CaseProvider");
  return ctx;
}
