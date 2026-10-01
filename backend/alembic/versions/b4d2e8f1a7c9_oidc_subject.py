"""Bind provisioned users to immutable OIDC subject identifiers.

Revision ID: b4d2e8f1a7c9
Revises: 9f7e8b6c5d4a
"""
from alembic import op
import sqlalchemy as sa

revision = "b4d2e8f1a7c9"
down_revision = "9f7e8b6c5d4a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("idp_subject", sa.String(length=255), nullable=True),
    )
    op.create_index("ix_users_idp_subject", "users", ["idp_subject"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_users_idp_subject", table_name="users")
    op.drop_column("users", "idp_subject")
