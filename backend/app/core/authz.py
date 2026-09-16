from __future__ import annotations

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session
import jwt
from jwt import PyJWKClient

from app.core.database import get_db
from app.models.entities import User
from app.core.config import get_settings

ROLES = ("ANALYST", "INVESTIGATOR", "FINANCE_OPERATOR", "APPROVER", "ADMINISTRATOR")

PERMISSIONS = ("VIEW", "INVESTIGATE", "RECOMMEND", "APPROVE", "EXECUTE")

ROLE_PERMISSIONS: dict[str, set[str]] = {
    "ANALYST": {"VIEW"},
    "FINANCE_OPERATOR": {"VIEW", "INVESTIGATE"},
    "INVESTIGATOR": {"VIEW", "INVESTIGATE", "RECOMMEND"},
    "APPROVER": {"VIEW", "INVESTIGATE", "APPROVE"},
    "ADMINISTRATOR": {"VIEW", "INVESTIGATE", "RECOMMEND", "APPROVE", "EXECUTE"},
}

settings = get_settings()

jwks_client = None
if not settings.demo_mode:
    if settings.auth_provider_domain:
        jwks_url = f"https://{settings.auth_provider_domain}/.well-known/jwks.json"
        jwks_client = PyJWKClient(jwks_url)

def get_current_user(authorization: str = Header(default=""), db: Session = Depends(get_db)) -> User:
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(401, "Missing or malformed Authorization header (expected 'Bearer <token>')")
    token = authorization[len("Bearer "):].strip()
    if not token:
        raise HTTPException(401, "Empty bearer token")

    db.set_tenant(None)
    
    if settings.demo_mode:
        user = db.query(User).filter(User.api_token == token).first()
        if user is None:
            raise HTTPException(401, "Invalid token")
        return user

    # PRODUCTION OIDC JWT VALIDATION
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=settings.auth_provider_audience,
            issuer=f"https://{settings.auth_provider_domain}/"
        )
    except jwt.exceptions.PyJWKClientError:
        raise HTTPException(401, "Unable to fetch JWKS from Identity Provider")
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token has expired")
    except jwt.InvalidIssuerError:
        raise HTTPException(401, "Invalid token issuer")
    except jwt.InvalidAudienceError:
        raise HTTPException(401, "Invalid token audience")
    except jwt.DecodeError:
        raise HTTPException(401, "Malformed or structurally invalid token")
    except jwt.InvalidSignatureError:
        raise HTTPException(401, "Invalid signature")
    except Exception as e:
        raise HTTPException(401, "Token validation failed")
        
    email = payload.get("email")
    if not email:
        raise HTTPException(401, "JWT payload must contain 'email' claim for provisioning")

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(403, f"User {email} is not provisioned for this application")

    return user

def require_permission(permission: str):
    def dependency(user: User = Depends(get_current_user)) -> User:
        user_perms = ROLE_PERMISSIONS.get(user.role, set())
        if permission not in user_perms:
            raise HTTPException(403, f"Role {user.role} lacks permission {permission}")
        return user
    return dependency

def get_tenant_db(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Session:
    db.set_tenant(user.tenant_id)
    return db

def get_system_db(db: Session = Depends(get_db)) -> Session:
    db.set_tenant(None)
    return db
