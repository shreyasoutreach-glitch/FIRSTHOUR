"""Persist uploaded evidence bytes in the database.

Revision ID: 9f7e8b6c5d4a
Revises: c3e2717fbf5f
"""
from alembic import op
import sqlalchemy as sa

revision = "9f7e8b6c5d4a"
down_revision = "c3e2717fbf5f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "evidence_artifacts",
        sa.Column("content_bytes", sa.LargeBinary(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("evidence_artifacts", "content_bytes")
