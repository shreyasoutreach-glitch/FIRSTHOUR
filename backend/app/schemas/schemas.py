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
