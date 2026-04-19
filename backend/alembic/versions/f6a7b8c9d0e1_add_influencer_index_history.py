"""add influencer_index_history table

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-04-18

"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

revision: str = 'f6a7b8c9d0e1'
down_revision: Union[str, Sequence[str], None] = 'e5f6a7b8c9d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "influencer_index_history",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("influencer_id", sa.Integer(), sa.ForeignKey("influencers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("band", sa.String(50), nullable=False),
        sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_influencer_index_history_influencer_id", "influencer_index_history", ["influencer_id"])
    op.create_index("ix_influencer_index_history_calculated_at", "influencer_index_history", ["calculated_at"])


def downgrade() -> None:
    op.drop_table("influencer_index_history")
