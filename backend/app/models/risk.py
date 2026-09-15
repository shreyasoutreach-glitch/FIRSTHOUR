from decimal import Decimal
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy import String, Float, Integer, JSON, Numeric, Boolean, DateTime, ForeignKey, Text, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.types import TypeDecorator

from app.core.database import Base

# Fallback for JSONB in sqlite
class JSONVariant(TypeDecorator):
    impl = JSON
    cache_ok = True
    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(JSONB())
        else:
            return dialect.type_descriptor(JSON())

class RiskEventModel(Base):
    __tablename__ = "risk_events"
    
    event_id: Mapped[str] = mapped_column(String, primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    entity_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    event_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    
    source: Mapped[str] = mapped_column(String, nullable=False)
    source_event_id: Mapped[str] = mapped_column(String, nullable=False)
    schema_version: Mapped[str] = mapped_column(String, default="1.0", nullable=False)
    
    payload: Mapped[Dict[str, Any]] = mapped_column(JSONVariant, nullable=False)
    payload_hash: Mapped[str] = mapped_column(String, nullable=False)
    previous_event_hash: Mapped[str] = mapped_column(String, nullable=False)
    
    # Phase 2 & 3: Idempotency constraint
    __table_args__ = (
        UniqueConstraint('tenant_id', 'source', 'source_event_id', name='uq_risk_event_source'),
    )

class AccountTrustStateModel(Base):
    __tablename__ = "account_trust_states"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_id: Mapped[str] = mapped_column(String, nullable=False)
    entity_id: Mapped[str] = mapped_column(String, nullable=False)
    
    known_devices: Mapped[List[str]] = mapped_column(JSONVariant, default=list, nullable=False)
    known_ips: Mapped[List[str]] = mapped_column(JSONVariant, default=list, nullable=False)
    known_beneficiaries: Mapped[List[str]] = mapped_column(JSONVariant, default=list, nullable=False)
    
    first_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    
    median_amount: Mapped[Decimal] = mapped_column(Numeric(24, 6), default=0, nullable=False)
    mad_amount: Mapped[Decimal] = mapped_column(Numeric(24, 6), default=0, nullable=False)
    total_transactions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    active_incident_id: Mapped[str] = mapped_column(String, nullable=True)
    current_risk_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    first_divergence_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    last_event_hash: Mapped[str] = mapped_column(String, default="", nullable=False)
    
    # Phase 3 & 5: Optimistic concurrency control (version field)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    __table_args__ = (
        UniqueConstraint('tenant_id', 'entity_id', name='uq_trust_state_tenant_entity'),
    )

class GraphRelationshipModel(Base):
    __tablename__ = "graph_relationships"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    
    source_type: Mapped[str] = mapped_column(String, nullable=False) # e.g. ACCOUNT, DEVICE
    source_id: Mapped[str] = mapped_column(String, nullable=False)
    
    target_type: Mapped[str] = mapped_column(String, nullable=False) # e.g. DEVICE, BANK_ACCOUNT
    target_id: Mapped[str] = mapped_column(String, nullable=False)
    
    relation_type: Mapped[str] = mapped_column(String, nullable=False) # OWNS, USES, SENT_TO
    
    # Phase 7 & 10: Temporal graph
    valid_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    valid_to: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index('ix_graph_source', 'tenant_id', 'source_type', 'source_id'),
        Index('ix_graph_target', 'tenant_id', 'target_type', 'target_id'),
    )

class RiskDecisionModel(Base):
    __tablename__ = "risk_decisions"
    
    decision_id: Mapped[str] = mapped_column(String, primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    entity_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    
    event_id: Mapped[str] = mapped_column(String, nullable=False) # The event evaluated
    risk_probability: Mapped[float] = mapped_column(Float, nullable=False)
    risk_band: Mapped[str] = mapped_column(String, nullable=False)
    recommended_action: Mapped[str] = mapped_column(String, nullable=False)
    
    reason_codes: Mapped[List[str]] = mapped_column(JSONVariant, nullable=False)
    supporting_events: Mapped[List[str]] = mapped_column(JSONVariant, nullable=False)
    competing_hypotheses: Mapped[Dict[str, float]] = mapped_column(JSONVariant, nullable=False)
    
    model_version: Mapped[str] = mapped_column(String, nullable=False)
    policy_version: Mapped[str] = mapped_column(String, nullable=False)
    evaluated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    # Phase 20: Shadow Mode outcome tracking
    actual_outcome: Mapped[str] = mapped_column(String, nullable=True) # E.g. COMPLETED, REVERSED, FALSE_POSITIVE




