import uuid
from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.risk import RiskEventModel, AccountTrustStateModel, GraphRelationshipModel, RiskDecisionModel
from app.services.risk.events import RiskEvent
from app.services.risk.engines import RiskFusionEngine

class PointInTimeEventSourcing:
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id

    def ingest_event(self, event: RiskEvent) -> Tuple[bool, Optional[AccountTrustStateModel]]:
        # Phase 2: Idempotent Ingestion
        existing = self.db.query(RiskEventModel).filter_by(
            tenant_id=self.tenant_id, 
            source=event.source, 
            source_event_id=event.source_event_id
        ).first()
        if existing:
            return False, None # Duplicate, ignored safely

        # Insert Event
        db_event = RiskEventModel(
            event_id=event.event_id,
            tenant_id=self.tenant_id,
            entity_id=event.entity_id,
            event_type=event.event_type,
            event_time=event.event_time,
            source=event.source,
            source_event_id=event.source_event_id,
            payload=event.payload,
            payload_hash=event.compute_hash(),
            previous_event_hash=event.previous_event_hash
        )
        self.db.add(db_event)
        
        # Load State (Optimistic Concurrency via version handled natively by SQLAlchemy if configured, but here explicit)
        state = self.db.query(AccountTrustStateModel).filter_by(
            tenant_id=self.tenant_id, entity_id=event.entity_id
        ).with_for_update().first() # Phase 3: Concurrency protection
        
        if not state:
            state = AccountTrustStateModel(tenant_id=self.tenant_id, entity_id=event.entity_id)
            self.db.add(state)
        
        # Update state logically
        if not state.first_seen: state.first_seen = event.event_time
        state.last_seen = event.event_time
        state.last_event_hash = db_event.payload_hash
        
        if not state.active_incident_id: # Baseline isolation
            if event.event_type in ("LOGIN_SUCCESS", "SESSION_START"):
                if "device_id" in event.payload:
                    dev_list = list(state.known_devices)
                    if event.payload["device_id"] not in dev_list:
                        dev_list.append(event.payload["device_id"])
                        state.known_devices = dev_list
                if "ip" in event.payload:
                    ip_list = list(state.known_ips)
                    if event.payload["ip"] not in ip_list:
                        ip_list.append(event.payload["ip"])
                        state.known_ips = ip_list
            elif event.event_type == "BENEFICIARY_CREATED":
                if "beneficiary_id" in event.payload:
                    b_list = list(state.known_beneficiaries)
                    if event.payload["beneficiary_id"] not in b_list:
                        b_list.append(event.payload["beneficiary_id"])
                        state.known_beneficiaries = b_list
            elif event.event_type == "TRANSFER_COMPLETED":
                amount = event.payload.get("amount", 0.0)
                # naive rolling update for demo
                state.median_amount = (state.median_amount * state.total_transactions + amount) / (state.total_transactions + 1)
                state.mad_amount = abs(amount - state.median_amount) * 0.5 + state.mad_amount * 0.5
                state.total_transactions += 1
                
        # Phase 4 & 9: Create graph edges
        if event.event_type == "DEVICE_REGISTERED" and "device_id" in event.payload:
            self._upsert_edge("ACCOUNT", event.entity_id, "DEVICE", event.payload["device_id"], "REGISTERED_ON", event.event_time)
        elif event.event_type == "TRANSFER_COMPLETED" and "beneficiary_id" in event.payload:
            self._upsert_edge("ACCOUNT", event.entity_id, "BENEFICIARY", event.payload["beneficiary_id"], "SENT_TO", event.event_time)

        state.version += 1
        return True, state

    def _upsert_edge(self, s_type, s_id, t_type, t_id, rel, time_val):
        edge = GraphRelationshipModel(
            tenant_id=self.tenant_id, source_type=s_type, source_id=s_id, 
            target_type=t_type, target_id=t_id, relation_type=rel, valid_from=time_val
        )
        self.db.add(edge)

    def reconstruct_features_as_of(self, entity_id: str, timestamp: datetime) -> Dict[str, Any]:
        # Phase 7: Point-in-time feature extraction
        # Must only return features where valid_from <= timestamp
        history = self.db.query(RiskEventModel).filter(
            RiskEventModel.tenant_id == self.tenant_id,
            RiskEventModel.entity_id == entity_id,
            RiskEventModel.event_time <= timestamp
        ).order_by(RiskEventModel.event_time.asc()).limit(5).all()
        
        # Real graph traversal using CTE (simulated using standard query due to sqlite CTE support variations)
        # Phase 5 & 10: Bounded Graph Traversal
        sql = text("""
        WITH RECURSIVE graph_cte AS (
            SELECT target_id, 1 as depth
            FROM graph_relationships
            WHERE tenant_id = :tenant AND source_id = :entity AND valid_from <= :ts
            UNION ALL
            SELECT g.target_id, c.depth + 1
            FROM graph_relationships g
            JOIN graph_cte c ON g.source_id = c.target_id
            WHERE g.tenant_id = :tenant AND g.valid_from <= :ts AND c.depth < 3
        )
        SELECT COUNT(DISTINCT target_id) FROM graph_cte
        """)
        fan_out = self.db.execute(sql, {"tenant": self.tenant_id, "entity": entity_id, "ts": timestamp}).scalar() or 1
        
        return {
            "recent_events": [e.event_type for e in history],
            "graph_fan_out": fan_out
        }

class ShadowModeLogger:
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
        
    def log_decision(self, decision_obj, entity_id: str, event_id: str):
        # Phase 20 & 29: Shadow Mode Logging
        rec = RiskDecisionModel(
            decision_id=decision_obj.decision_id,
            tenant_id=self.tenant_id,
            entity_id=entity_id,
            event_id=event_id,
            risk_probability=decision_obj.risk_probability,
            risk_band=decision_obj.risk_band,
            recommended_action=decision_obj.recommended_action,
            reason_codes=decision_obj.reason_codes,
            supporting_events=decision_obj.supporting_event_ids,
            competing_hypotheses=decision_obj.competing_hypotheses,
            model_version=decision_obj.model_version,
            policy_version=decision_obj.policy_version,
            evaluated_at=decision_obj.evaluated_at
        )
        self.db.add(rec)
