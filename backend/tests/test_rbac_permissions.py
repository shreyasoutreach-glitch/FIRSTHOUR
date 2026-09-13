"""
RBAC tests: the permission matrix itself, and the specific property the
enterprise brief calls out by name -- a role that can investigate/recommend
must never automatically be able to approve or execute.
"""
from __future__ import annotations

from app.core.authz import PERMISSIONS, ROLE_PERMISSIONS, ROLES


def test_every_role_has_a_permission_set_defined():
    for role in ROLES:
        assert role in ROLE_PERMISSIONS


def test_analyst_has_view_only():
    assert ROLE_PERMISSIONS["ANALYST"] == {"VIEW"}


def test_only_administrator_has_execute():
    for role, perms in ROLE_PERMISSIONS.items():
        if role == "ADMINISTRATOR":
            assert "EXECUTE" in perms
        else:
            assert "EXECUTE" not in perms


def test_investigator_cannot_approve_or_execute():
    """The exact property named in the brief: a user who can investigate
    (and recommend) must not automatically be able to approve or execute."""
    perms = ROLE_PERMISSIONS["INVESTIGATOR"]
    assert "INVESTIGATE" in perms
    assert "RECOMMEND" in perms
    assert "APPROVE" not in perms
    assert "EXECUTE" not in perms


def test_approver_cannot_execute():
    perms = ROLE_PERMISSIONS["APPROVER"]
    assert "APPROVE" in perms
    assert "EXECUTE" not in perms


def test_finance_operator_cannot_recommend_approve_or_execute():
    perms = ROLE_PERMISSIONS["FINANCE_OPERATOR"]
    assert perms == {"VIEW", "INVESTIGATE"}


def test_administrator_has_every_permission():
    assert ROLE_PERMISSIONS["ADMINISTRATOR"] == set(PERMISSIONS)


def test_permission_hierarchy_is_monotonic_in_role_power():
    """Each role's permission set should be a superset progression roughly
    matching ANALYST < FINANCE_OPERATOR < INVESTIGATOR/APPROVER < ADMINISTRATOR
    -- specifically, VIEW is in every role's set (nobody has less than view)."""
    for role in ROLES:
        assert "VIEW" in ROLE_PERMISSIONS[role]
