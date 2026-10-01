from __future__ import annotations

import argparse
import secrets
import uuid

from app.core.database import SessionLocal
from app.models import entities as m

ROLES = {"ANALYST", "INVESTIGATOR", "FINANCE_OPERATOR", "APPROVER", "ADMINISTRATOR"}

def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"

def main() -> None:
    parser = argparse.ArgumentParser(description="Provision an OIDC identity into Primhora.")
    parser.add_argument("--subject", required=True, help="Immutable OIDC sub claim.")
    parser.add_argument("--email", required=True)
    parser.add_argument("--name", default="")
    parser.add_argument("--role", choices=sorted(ROLES), default="ANALYST")
    parser.add_argument("--tenant-id", default="")
    parser.add_argument("--tenant-name", default="")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        db.set_tenant(None)
        existing = db.query(m.User).filter(m.User.idp_subject == args.subject).first()
        if existing:
            existing.email = args.email
            existing.display_name = args.name or existing.display_name
            existing.role = args.role
            db.commit()
            print(f"Updated existing identity: {existing.id} role={existing.role} tenant={existing.tenant_id}")
            return

        tenant_id = args.tenant_id or new_id("TEN")
        tenant = db.get(m.Tenant, tenant_id)
        if tenant is None:
            tenant = m.Tenant(id=tenant_id, name=args.tenant_name or f"{args.name or args.email}'s Primhora workspace")
            db.add(tenant)
            db.flush()

        user = m.User(
            id=new_id("USR"),
            tenant_id=tenant.id,
            email=args.email,
            idp_subject=args.subject,
            display_name=args.name or args.email.split("@", 1)[0],
            role=args.role,
            api_token=secrets.token_urlsafe(32)[:64],
        )
        db.add(user)
        db.commit()
        print(f"Provisioned identity: {user.id} role={user.role} tenant={tenant.id}")
    finally:
        db.close()

if __name__ == "__main__":
    main()