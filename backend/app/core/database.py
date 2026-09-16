"""
SQLAlchemy engine/session wiring. DATABASE_URL decides whether this is the
zero-setup SQLite fallback or a production-shaped Postgres instance -- the
models and services never know or care which one is active.

The session class is TenantScopedSession (see app/core/tenancy.py), not the
default Session -- every session created anywhere in this app, including in
tests and the seed script, is tenant-aware from the moment it's constructed.
A session with no tenant set (`db.current_tenant_id is None`) behaves like a
plain, unfiltered Session -- see get_db()/get_system_db() in
app/core/authz.py for exactly which code paths are allowed to do that.
"""
import json
from decimal import Decimal
from sqlalchemy import create_engine

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)

def custom_dumps(d):
    return json.dumps(d, cls=DecimalEncoder)
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import get_settings
from app.core.tenancy import TenantScopedSession

settings = get_settings()

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url.replace("postgres://", "postgresql://"), connect_args=connect_args, json_serializer=custom_dumps)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=TenantScopedSession)


class Base(DeclarativeBase):
    pass


def get_db():
    """Unscoped session -- exists for backward compatibility (e.g. Alembic-
    style scripts) and is NOT wired into any FastAPI route. Every route uses
    app.core.authz.get_tenant_db or get_system_db instead, which both
    construct a TenantScopedSession with an explicit, deliberate tenant
    setting rather than an accidental unfiltered one."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



