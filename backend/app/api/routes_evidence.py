from __future__ import annotations

import os
import uuid

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.audit.logger import log as audit_log
from app.core.authz import get_tenant_db, require_permission
from app.core.config import get_settings
from app.models import entities as m
from app.services.evidence.pipeline import (
    cross_reference_amount_claim,
    extract_candidate_claims,
    is_path_contained,
    safe_filename,
    sha256_bytes,
    validate_mime,
)

router = APIRouter(tags=["evidence"])
settings = get_settings()


@router.post("/evidence/upload")
async def upload_evidence(
    file: UploadFile,
    merchant_id: str = Form(...),
    incident_id: str = Form(""),
    source_label: str = Form("upload"),
    db: Session = Depends(get_tenant_db),
    _user: m.User = Depends(require_permission("INVESTIGATE")),
):
    data = await file.read()
    if not validate_mime(file.content_type or "application/octet-stream"):
        raise HTTPException(400, f"Unsupported MIME type: {file.content_type}")

    digest = sha256_bytes(data)
    os.makedirs(settings.evidence_storage_dir, exist_ok=True)
    artifact_id = f"EVD_{uuid.uuid4().hex[:10]}"

    # file.filename is untrusted client input -- safe_filename() strips any
    # directory components / traversal sequences before it ever touches a
    # path, and is_path_contained() below is a second, independent check on
    # the resolved destination so a single sanitization bug here can't turn
    # into an arbitrary-file-write.
    display_filename = safe_filename(file.filename)
    stored_path = os.path.join(settings.evidence_storage_dir, f"{artifact_id}_{display_filename}")
    if not is_path_contained(settings.evidence_storage_dir, stored_path):
        raise HTTPException(400, "Invalid filename.")

    with open(stored_path, "wb") as f:
        f.write(data)

    raw_text = ""
    extraction_status = "queued"
    if (file.content_type or "").startswith("text/"):
        raw_text = data.decode("utf-8", errors="ignore")
        extraction_status = "text_ready"
    else:
        # Image/PDF vision extraction is a real pipeline stage (see
        # ARCHITECTURE.md) but requires an OCR/vision backend this sandboxed
        # demo does not ship with. We are honest about that here rather than
        # faking a result.
        extraction_status = "queued_for_vision_extraction"

    artifact = m.EvidenceArtifact(
        id=artifact_id, incident_id=incident_id, merchant_id=merchant_id,
        filename=display_filename, mime_type=file.content_type or "application/octet-stream",
        sha256=digest, source_label=source_label, raw_text=raw_text,
        extraction_status=extraction_status,
    )
    db.add(artifact)
    audit_log(db, incident_id=incident_id, actor="SYSTEM", event_type="EVIDENCE_UPLOADED",
              summary=f"{display_filename} ({digest[:12]}...)", sources=[artifact_id], detail={})
    db.commit()

    return {
        "artifact_id": artifact.id, "filename": artifact.filename, "sha256": artifact.sha256,
        "mime_type": artifact.mime_type, "extraction_status": artifact.extraction_status,
    }


@router.post("/evidence/analyze")
def analyze_evidence(artifact_id: str = Form(...), db: Session = Depends(get_tenant_db),
                     _user: m.User = Depends(require_permission("INVESTIGATE"))):
    artifact = db.get(m.EvidenceArtifact, artifact_id)
    if artifact is None:
        raise HTTPException(404, "artifact not found")
    if artifact.extraction_status == "queued_for_vision_extraction":
        raise HTTPException(
            409,
            "This artifact needs vision/OCR extraction, which this offline demo build does not "
            "run. Provide ANTHROPIC_API_KEY and a vision-capable extractor, or upload a text export.",
        )

    candidates = extract_candidate_claims(artifact.raw_text, artifact.id)

    financial_events = (
        db.query(m.FinancialEvent).filter(m.FinancialEvent.merchant_id == artifact.merchant_id).all()
    )
    candidate_events = [(fe.id, fe.amount) for fe in financial_events]

    verified_count = conflicting_count = unverified_count = 0
    for c in candidates:
        status = "UNVERIFIED"
        matched = ""
        if c["claim_type"] == "amount":
            status, matched = cross_reference_amount_claim(c["claim_value"]["amount"], candidate_events)
        if status == "VERIFIED":
            verified_count += 1
        elif status == "CONFLICTING":
            conflicting_count += 1
        else:
            unverified_count += 1

        db.add(m.ExtractedClaim(
            id=c["id"], source_artifact_id=c["source_artifact_id"],
            source_location=c["source_location"], extraction_method=c["extraction_method"],
            claim_type=c["claim_type"], claim_value=c["claim_value"],
            verification_status=status, matched_financial_event_id=matched,
        ))

    artifact.extraction_status = "extracted"
    audit_log(db, incident_id=artifact.incident_id, actor="SYSTEM", event_type="EVIDENCE_ANALYZED",
              summary=f"{len(candidates)} candidate claims extracted from {artifact.filename}",
              sources=[artifact.id], detail={"verified": verified_count, "conflicting": conflicting_count,
                                              "unverified": unverified_count})
    db.commit()

    return {
        "artifact_id": artifact.id,
        "claims": candidates,
        "verification_summary": {
            "verified": verified_count, "conflicting": conflicting_count, "unverified": unverified_count,
        },
    }
