from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    routes_demo,
    routes_evidence,
    routes_incident,
    routes_merchant,
    routes_metrics,
    routes_recovery,
    routes_webhooks,
)
from app.core.config import get_settings


settings = get_settings()

if not settings.demo_mode:
    if not settings.auth_provider_domain or not settings.auth_provider_audience:
        raise RuntimeError("DEMO_MODE is false but no production authentication provider is configured. System halted.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="Primhora",
    description="Early investigation and exposure mitigation for complex financial incidents.",
    lifespan=lifespan,
)

if settings.cors_origin_list:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(routes_incident.router, prefix="/api")
app.include_router(routes_evidence.router, prefix="/api")
app.include_router(routes_merchant.router, prefix="/api")
app.include_router(routes_metrics.router, prefix="/api")
app.include_router(routes_demo.router, prefix="/api")
app.include_router(routes_recovery.router, prefix="/api")
app.include_router(routes_webhooks.router, prefix="/api")


def _health_payload() -> dict:
    return {
        "status": "ok",
        "service": "primhora",
        "demo_mode": settings.demo_mode,
        "integrations": {
            "razorpayx": bool(
                settings.razorpay_key_id
                and settings.razorpay_key_secret
                and settings.razorpay_account_number
            ),
            "gemini_evidence": bool(settings.gemini_api_key),
        },
    }


@app.get("/")
def root():
    return _health_payload()


@app.head("/")
def root_head():
    return None


@app.get("/health")
def health_check():
    return _health_payload()
