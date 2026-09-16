from __future__ import annotations
import pytest
import jwt
from fastapi import HTTPException
from unittest.mock import MagicMock, patch
from app.core.authz import get_current_user
from app.models.entities import User
from app.core.config import get_settings

settings = get_settings()

class MockDB:
    def set_tenant(self, tenant):
        pass
    def query(self, model):
        return self
    def filter(self, condition):
        self.cond = condition
        return self
    def first(self):
        # We need to simulate User.email == email
        email = self.cond.right.value
        if email == "admin@firsthour.local":
            return User(id="u1", email=email, role="ADMINISTRATOR", tenant_id="t1")
        return None

def test_jwt_validation():
    db = MockDB()

    # Test missing token
    with pytest.raises(HTTPException) as exc:
        get_current_user("", db)
    assert exc.value.status_code == 401
    
    with pytest.raises(HTTPException) as exc:
        get_current_user("Bearer ", db)
    assert exc.value.status_code == 401

    # Temporarily set demo_mode = False for tests
    settings.demo_mode = False
    
    with patch('app.core.authz.jwks_client') as mock_jwks, patch('jwt.decode') as mock_decode:
        # Invalid signature
        mock_decode.side_effect = jwt.InvalidSignatureError()
        with pytest.raises(HTTPException) as exc:
            get_current_user("Bearer fake", db)
        assert exc.value.status_code == 401

        # Expired
        mock_decode.side_effect = jwt.ExpiredSignatureError()
        with pytest.raises(HTTPException) as exc:
            get_current_user("Bearer fake", db)
        assert exc.value.status_code == 401

        # Wrong Issuer
        mock_decode.side_effect = jwt.InvalidIssuerError()
        with pytest.raises(HTTPException) as exc:
            get_current_user("Bearer fake", db)
        assert exc.value.status_code == 401

        # Valid token, no email
        mock_decode.side_effect = None
        mock_decode.return_value = {"sub": "id123"}
        with pytest.raises(HTTPException) as exc:
            get_current_user("Bearer valid", db)
        assert exc.value.status_code == 401

        # Valid token, unknown email (fail safe provisioning)
        mock_decode.return_value = {"sub": "id123", "email": "unknown@firsthour.local"}
        with pytest.raises(HTTPException) as exc:
            get_current_user("Bearer valid", db)
        assert exc.value.status_code == 403

        # Valid token, known user
        mock_decode.return_value = {"sub": "id123", "email": "admin@firsthour.local"}
        user = get_current_user("Bearer valid", db)
        assert user.role == "ADMINISTRATOR"
        assert user.tenant_id == "t1"
