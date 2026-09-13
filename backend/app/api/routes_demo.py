from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.authz import get_system_db
from app.core.config import get_settings
from app.demo.chaos_lab import inject_scenario
from app.schemas.schemas import DemoResetResponse, InjectIncidentRequest, InjectIncidentResponse

router = APIRouter(tags=["demo"])
settings = get_settings()

# These endpoints are destructive (reset wipes and reseeds the ENTIRE
# database, across every tenant) and are gated two ways: DEMO_MODE must be
# on, AND the caller must authenticate as an ADMINISTRATOR (see
# app.core.authz.get_system_db). The very first Administrator token for a
# fresh database only exists after running `python -m seed.seed` once from
# the CLI -- see README.md's "Local setup" section.


@router.post("/demo/inject-incident", response_model=InjectIncidentResponse)
def demo_inject_incident(body: InjectIncidentRequest, db: Session = Depends(get_system_db)):
    if not settings.demo_mode:
        raise HTTPException(403, "DEMO_MODE is disabled")
    result = inject_scenario(db, body.scenario, body.merchant_id)
    return InjectIncidentResponse(**result)


@router.post("/demo/reset", response_model=DemoResetResponse)
def demo_reset(db: Session = Depends(get_system_db)):
    if not settings.demo_mode:
        raise HTTPException(403, "DEMO_MODE is disabled")
    from seed.seed import run_seed  # local import: seed/ is only needed in demo mode

    result = run_seed(db, seed_value=settings.seed)
    return DemoResetResponse(
        status="reset_complete",
        dataset_version="v1",
        flagship_incident_id=result["flagship_incident_id"],
        tenants=result["tenants"],
        tokens_by_tenant=result["tokens_by_tenant"],
    )
