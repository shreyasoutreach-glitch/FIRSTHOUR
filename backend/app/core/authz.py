"""
Authentication + RBAC.

Deliberately NOT a real identity provider -- there is no password hashing, no
MFA, no session expiry, no token revocation flow. This is a bearer-token
lookup against a `users` table, seeded at demo-setup time. That is an
intentional scope decision (see AUDIT.md section J): building a bespoke
OAuth/SSO system would be thrown away by any real customer on day one in
favor of their own IdP (Okta/Azure AD/etc.), so it is not worth building here.
What IS real and worth building is everything downstream of "who is this" --
the role model, the permission checks, and the fact that a route's tenant
comes from the AUTHENTICATED user, never from a client-supplied header.

Permission model: five roles (Analyst, Investigator, Finance Operator,
Approver, Administrator), five permissions (VIEW, INVESTIGATE, RECOMMEND,
APPROVE, EXECUTE). No role has EXECUTE except Administrator -- an
Investigator who can propose a recovery command can never approve or execute
it themselves. This is the one property the enterprise brief calls out
explicitly and it is enforced here structurally (a fixed dict lookup), not by
convention.

Every dependency in this file composes on top of app.core.database.get_db
(via FastAPI's Depends), rather than constructing its own SessionLocal()
internally. That's deliberate: FastAPI caches a dependency's result within
one request, so get_current_user / get_tenant_db / get_system_db all end up
sharing the exact same Session instance for a given request -- and, just as
importantly, it means tests can override get_db the same way they already do
for every other route, instead of needing a second, parallel override
mechanism for auth. A version of this file that called SessionLocal()
directly was written and then caught by exactly this problem in testing.
"""
from __future__ import annotations

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.entities import User

ROLES = ("ANALYST", "INVESTIGATOR", "FINANCE_OPERATOR", "APPROVER", "ADMINISTRATOR")

PERMISSIONS = ("VIEW", "INVESTIGATE", "RECOMMEND", "APPROVE", "EXECUTE")

ROLE_PERMISSIONS: dict[str, set[str]] = {
    "ANALYST": {"VIEW"},
    "FINANCE_OPERATOR": {"VIEW", "INVESTIGATE"},
    "INVESTIGATOR": {"VIEW", "INVESTIGATE", "RECOMMEND"},
    "APPROVER": {"VIEW", "INVESTIGATE", "APPROVE"},
    "ADMINISTRATOR": {"VIEW", "INVESTIGATE", "RECOMMEND", "APPROVE", "EXECUTE"},
}


def get_current_user(authorization: str = Header(default=""), db: Session = Depends(get_db)) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing or malformed Authorization header (expected 'Bearer <token>')")
    token = authorization[len("Bearer "):].strip()
    if not token:
        raise HTTPException(401, "Empty bearer token")

    # Unscoped lookup -- at this point we don't know the caller's tenant yet;
    # the tenant is *derived from* the user we find, not supplied by the
    # caller. Explicitly reset to None first in case this session object is
    # somehow reused with a stale tenant from elsewhere (defensive; in
    # practice get_db always yields a fresh session per request).
    db.set_tenant(None)
    user = db.query(User).filter(User.api_token == token).first()
    if user is None:
        raise HTTPException(401, "Invalid token")
    return user


def require_permission(permission: str):
    """Dependency factory: Depends(require_permission("APPROVE")) rejects
    with 403 any authenticated user whose role doesn't carry that
    permission. This is checked on every high-risk route in addition to
    (not instead of) a RecoveryCommand's own state machine -- a permission
    check answers "is this role allowed to do this kind of thing at all",
    the state machine answers "is this command in a state where this
    transition is legal right now"."""
    if permission not in PERMISSIONS:
        raise ValueError(f"Unknown permission: {permission}")

    def _check(user: User = Depends(get_current_user)) -> User:
        if permission not in ROLE_PERMISSIONS.get(user.role, set()):
            raise HTTPException(
                403,
                f"Role '{user.role}' does not have '{permission}' permission",
            )
        return user

    return _check


def get_tenant_db(
    user: User = Depends(require_permission("VIEW")),
    db: Session = Depends(get_db),
) -> Session:
    """The standard DB dependency for tenant-scoped routes. Every user has at
    least VIEW, so this both authenticates the caller and scopes the shared
    request session to *their* tenant -- never a tenant the caller names
    themselves. By the time this function body runs, `user` has already been
    fully resolved (FastAPI resolves dependency arguments before calling),
    so this always sets the tenant *after* get_current_user's own temporary
    db.set_tenant(None) lookup step."""
    db.set_tenant(user.tenant_id)
    return db


def get_system_db(
    user: User = Depends(require_permission("EXECUTE")),
    db: Session = Depends(get_db),
) -> Session:
    """For genuinely cross-tenant admin/system operations (demo reset, demo
    seed injection). Requires EXECUTE, which today only ADMINISTRATOR has,
    and the session is intentionally left unscoped (tenant=None) because
    these operations legitimately touch every tenant's data. Gated by role,
    not by tenant scoping -- that's the correct boundary for an operation
    that isn't tenant-shaped in the first place."""
    if user.role != "ADMINISTRATOR":
        raise HTTPException(403, "Administrator role required for system operations")
    db.set_tenant(None)
    return db
