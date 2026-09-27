"""
SQLAlchemy engine/session wiring. DATABASE_URL selects SQLite locally or
Postgres on Render. The explicit psycopg2 dialect keeps SQLAlchemy 2.x from
trying to import the psycopg3 driver when psycopg2-binary is installed.
"""
import json
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.core.config import get_settings
from app.core.tenancy import TenantScopedSession

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)

def custom_dumps(d):
    return json.dumps(d, cls=DecimalEncoder)

settings = get_settings()
database_url = settings.database_url
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql+psycopg2://", 1)
elif database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+psycopg2://", 1)

connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
engine = create_engine(database_url, connect_args=connect_args, json_serializer=custom_dumps)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=TenantScopedSession)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
