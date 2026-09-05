from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import routes_demo, routes_evidence, routes_incident, routes_merchant, routes_metrics
from app.core.config import get_settings
from app.core.database import Base, engine

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


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


@app.get("/")
def root():
    return {"product": "FIRST HOUR", "status": "read-only demo/sandbox workspace",
            "demo_mode": settings.demo_mode}


@app.get("/health")
def health():
    return {"status": "ok"}
