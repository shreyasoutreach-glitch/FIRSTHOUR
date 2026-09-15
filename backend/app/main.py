from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import routes_demo, routes_evidence, routes_incident, routes_merchant, routes_metrics, routes_recovery
from app.core.config import get_settings
from app.core.database import Base, engine


settings = get_settings()

if not settings.demo_mode and (not settings.auth_provider_domain or not settings.auth_provider_audience):
    raise RuntimeError("DEMO_MODE is false but no production authentication provider is configured. System halted.")



@asynccontextmanager
async def lifespan(app: FastAPI):
    # Base.metadata.create_all(bind=engine)  # Removed for Alembic migrations
    yield



from fastapi.encoders import ENCODERS_BY_TYPE
from decimal import Decimal
ENCODERS_BY_TYPE[Decimal] = str

app = FastAPI(

    lifespan=lifespan,
    title="FIRST HOUR",
    description="Financial incident reconstruction -- AI interprets, deterministic systems establish "
                "financial truth, the graph connects facts, humans resolve what machines cannot know.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_incident.router)
app.include_router(routes_evidence.router)
app.include_router(routes_demo.router)
app.include_router(routes_metrics.router)
app.include_router(routes_merchant.router)
app.include_router(routes_recovery.router)


@app.get("/")
def root():
    return {"product": "FIRST HOUR", "status": "read-only demo/sandbox workspace",
            "demo_mode": settings.demo_mode}


@app.get("/health")
def health():
    return {"status": "ok"}
