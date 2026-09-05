from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.demo.chaos_lab import inject_scenario
from app.schemas.schemas import DemoResetResponse, InjectIncidentRequest, InjectIncidentResponse

router = APIRouter(tags=["demo"])
settings = get_settings()


@router.post("/demo/inject-incident", response_model=InjectIncidentResponse)
def demo_inject_incident(body: InjectIncidentRequest, db: Session = Depends(get_db)):
    if not settings.demo_mode:
        raise HTTPException(403, "DEMO_MODE is disabled")
    result = inject_scenario(db, body.scenario, body.merchant_id)
    return InjectIncidentResponse(**result)


@router.post("/demo/reset", response_model=DemoResetResponse)
def demo_reset(db: Session = Depends(get_db)):
    if not settings.demo_mode:
        raise HTTPException(403, "DEMO_MODE is disabled")
    from seed.seed import run_seed  # local import: seed/ is only needed in demo mode

    flagship_id = run_seed(db, seed_value=settings.seed)
    return DemoResetResponse(status="reset_complete", dataset_version="v1", flagship_incident_id=flagship_id)
