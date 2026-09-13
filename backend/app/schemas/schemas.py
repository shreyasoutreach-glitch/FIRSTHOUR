"""Typed request/response schemas for the API layer."""
from __future__ import annotations

import datetime as dt

from pydantic import BaseModel, Field


class AttestationRequest(BaseModel):
    question_id: str
    answer: str = Field(pattern="^(YES|NO|NOT_SURE)$")
    note: str = ""


class AttestationResponse(BaseModel):
    id: str
    incident_id: str
    question_id: str
    question_text: str
    answer: str
    affected_predicate: str
    created_at: dt.datetime
    message: str
    new_state: str


class NextQuestionResponse(BaseModel):
    question_id: str | None
    question_text: str | None
    priority: float | None
    remaining_count: int


class InjectIncidentRequest(BaseModel):
    scenario: str = Field(pattern="^(new_beneficiary_burst|executive_impersonation|"
                                   "dormant_vendor_activation|duplicate_payout)$")
    merchant_id: str = "MER_ARROW"


class InjectIncidentResponse(BaseModel):
    incident_id: str
    scenario: str
    incident_evidence_score: float
    score_components: dict
    payout_ids: list[str]
    audit_trail: list[str]


class EvidenceUploadResponse(BaseModel):
    artifact_id: str
    filename: str
    sha256: str
    mime_type: str
    extraction_status: str


class EvidenceAnalyzeResponse(BaseModel):
    artifact_id: str
    claims: list[dict]
    verification_summary: dict


class DemoResetResponse(BaseModel):
    status: str
    dataset_version: str
    flagship_incident_id: str
    tenants: dict[str, str]
    tokens_by_tenant: dict[str, dict[str, str]] = Field(
        description="DEMO-ONLY bearer tokens, deterministic from the seed value. "
                    "Not real credentials -- see LIMITATIONS.md."
    )


class ProposeRecoveryCommandRequest(BaseModel):
    action: str = Field(pattern="^(FREEZE_PAYOUT|REVERSE_PAYOUT)$")
    target_type: str = "payout"
    target_id: str
    amount: float
    reason: str
    supporting_evidence: list[str] = Field(default_factory=list)
    idempotency_key: str | None = None
    risk: str = Field(default="MEDIUM", pattern="^(LOW|MEDIUM|HIGH)$")
    reversible: bool = True


class RecoveryCommandResponse(BaseModel):
    id: str
    incident_id: str
    action: str
    target_type: str
    target_id: str
    amount: float
    reason: str
    supporting_evidence: list[str]
    expected_effect: str
    risk: str
    reversible: bool
    state: str
    created_by: str
    reviewed_by: str
    approved_by: str
    execution_mode: str
    dry_run_result: dict
    execution_result: dict
    created_at: dt.datetime
    updated_at: dt.datetime


class RejectRecoveryCommandRequest(BaseModel):
    reason: str = ""


class ConvergenceResponse(BaseModel):
    status: str
    checks: list[dict]
    discrepancies: list[str]
