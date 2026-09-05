"""
Financial graph construction. Prototype implementation uses relational edge
tables (as instructed) rather than a graph database, but the node/edge shape
is graph-native so swapping in Neo4j/etc. later only touches this file.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from app.models import entities as m


@dataclass
class GraphNode:
    id: str
    type: str  # Merchant/Account/Contact/FundAccount/Payment/Payout/Communication/Evidence/Employee
    label: str
    data: dict = field(default_factory=dict)


@dataclass
class GraphEdge:
    id: str
    source: str
    target: str
    type: str  # OWNS/PAID_TO/BELONGS_TO/CREATED_BY/MENTIONED_IN/SUPPORTED_BY/PRECEDES/ASSOCIATED_WITH/SAME_ENTITY
    data: dict = field(default_factory=dict)


def build_incident_graph(db: Session, incident_id: str) -> dict:
    incident = db.get(m.Incident, incident_id)
    if incident is None:
        return {"nodes": [], "edges": []}

    merchant = db.get(m.Merchant, incident.merchant_id)
    nodes: dict[str, GraphNode] = {}
    edges: list[GraphEdge] = []

    def add_node(node: GraphNode):
        nodes[node.id] = node

    add_node(GraphNode(id=merchant.id, type="Merchant", label=merchant.name,
                        data={"category": merchant.category}))

    incident_events = (
        db.query(m.IncidentEvent).filter(m.IncidentEvent.incident_id == incident_id)
        .order_by(m.IncidentEvent.sequence).all()
    )
    financial_event_ids = [ie.financial_event_id for ie in incident_events]
    fevents = db.query(m.FinancialEvent).filter(m.FinancialEvent.id.in_(financial_event_ids)).all()
    fevents_by_id = {f.id: f for f in fevents}

    seen_contacts: set[str] = set()
    seen_fund_accounts: set[str] = set()

    for ie in incident_events:
        fe = fevents_by_id.get(ie.financial_event_id)
        if fe is None:
            continue
        payout = db.get(m.Payout, fe.source_record_id)
        add_node(GraphNode(id=fe.id, type="Payout", label=f"₹{fe.amount:,.0f}",
                            data={"timestamp": fe.timestamp.isoformat(), "amount": fe.amount,
                                  "source_record_id": fe.source_record_id}))
        edges.append(GraphEdge(id=f"e_{merchant.id}_{fe.id}", source=merchant.id, target=fe.id, type="OWNS"))

        if payout:
            contact = db.get(m.Contact, payout.contact_id)
            fund_account = db.get(m.FundAccount, payout.fund_account_id)
            if contact and contact.id not in seen_contacts:
                add_node(GraphNode(id=contact.id, type="Contact", label=contact.name,
                                    data={"type": contact.type, "created_at": contact.created_at.isoformat()}))
                seen_contacts.add(contact.id)
            if contact:
                edges.append(GraphEdge(id=f"e_{fe.id}_{contact.id}", source=fe.id, target=contact.id,
                                        type="PAID_TO"))
            if fund_account and fund_account.id not in seen_fund_accounts:
                add_node(GraphNode(id=fund_account.id, type="FundAccount",
                                    label=fund_account.vpa or fund_account.masked_bank_account,
                                    data={"account_type": fund_account.account_type}))
                seen_fund_accounts.add(fund_account.id)
            if fund_account:
                edges.append(GraphEdge(id=f"e_{contact.id}_{fund_account.id}", source=contact.id,
                                        target=fund_account.id, type="OWNS"))

    comms = db.query(m.CommunicationEvent).filter(m.CommunicationEvent.incident_id == incident_id).all()
    for c in comms:
        add_node(GraphNode(id=c.id, type="Communication", label=c.channel,
                            data={"timestamp": c.timestamp.isoformat(), "sender": c.sender_label}))
        artifact = db.get(m.EvidenceArtifact, c.source_artifact_id)
        if artifact:
            add_node(GraphNode(id=artifact.id, type="Evidence", label=artifact.filename,
                                data={"mime_type": artifact.mime_type, "sha256": artifact.sha256[:12]}))
            edges.append(GraphEdge(id=f"e_{c.id}_{artifact.id}", source=c.id, target=artifact.id,
                                    type="SUPPORTED_BY"))
        if c.resolved_contact_id and c.resolved_contact_id in seen_contacts:
            edges.append(GraphEdge(id=f"e_{c.id}_{c.resolved_contact_id}", source=c.id,
                                    target=c.resolved_contact_id, type="MENTIONED_IN"))
        if c.correlated_financial_event_id:
            edges.append(GraphEdge(id=f"e_{c.id}_{c.correlated_financial_event_id}", source=c.id,
                                    target=c.correlated_financial_event_id, type="ASSOCIATED_WITH"))

    return {
        "nodes": [n.__dict__ for n in nodes.values()],
        "edges": [e.__dict__ for e in edges],
    }


def blast_radius(db: Session, seed_contact_ids: list[str], depth: int = 3) -> dict:
    """Bounded BFS outward from suspicious beneficiaries through shared fund
    accounts, contacts and payouts, up to `depth` hops. Returns the connected
    event count/amount and affected entities -- every number here is a plain
    aggregation over rows actually touched by the traversal, nothing modeled
    or estimated.

    "Shared fund account" is resolved by the underlying VPA / masked bank
    account value, not by FundAccount.id -- a mule pattern typically shows up
    as several different Contact records (different display names) that all
    route to the *same* real account, each with their own FundAccount row.
    Matching on id alone would never catch that.
    """
    visited_contacts: set[str] = set(seed_contact_ids)
    visited_fund_accounts: set[str] = set()
    connected_payout_ids: set[str] = set()

    frontier = list(seed_contact_ids)
    for _ in range(depth):
        if not frontier:
            break
        next_frontier: list[str] = []

        fund_accounts = db.query(m.FundAccount).filter(m.FundAccount.contact_id.in_(frontier)).all()
        for fa in fund_accounts:
            visited_fund_accounts.add(fa.id)

        payouts = db.query(m.Payout).filter(m.Payout.contact_id.in_(frontier)).all()
        for p in payouts:
            connected_payout_ids.add(p.id)

        # Any other FundAccount that shares the same real-world VPA / bank
        # account as one we've already touched -> its owning contact joins
        # the frontier, regardless of what that contact is named.
        account_keys = [(fa.vpa, fa.masked_bank_account) for fa in fund_accounts if fa.vpa or fa.masked_bank_account]
        for vpa, masked_bank_account in account_keys:
            q = db.query(m.FundAccount)
            if vpa:
                q = q.filter(m.FundAccount.vpa == vpa)
            elif masked_bank_account:
                q = q.filter(m.FundAccount.masked_bank_account == masked_bank_account)
            else:
                continue
            for shared_fa in q.all():
                visited_fund_accounts.add(shared_fa.id)
                if shared_fa.contact_id not in visited_contacts:
                    visited_contacts.add(shared_fa.contact_id)
                    next_frontier.append(shared_fa.contact_id)

        frontier = next_frontier

    payouts = db.query(m.Payout).filter(m.Payout.id.in_(connected_payout_ids)).all()
    connected_amount = sum(p.amount for p in payouts)
    pending_amount = sum(p.amount for p in payouts if p.status == "queued")

    return {
        "connected_event_count": len(connected_payout_ids),
        "connected_amount": connected_amount,
        "affected_entities": len(visited_contacts),
        "affected_fund_accounts": len(visited_fund_accounts),
        "pending_exposure": pending_amount,
        "traversal_depth": depth,
    }
