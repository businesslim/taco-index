"""add users and predictions tables

Revision ID: g7h8i9j0k1l2
Revises: f6a7b8c9d0e1
Create Date: 2026-04-22

"""
from typing import Sequence, Union
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

revision: str = "g7h8i9j0k1l2"
down_revision: Union[str, None] = "f6a7b8c9d0e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("image", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("prediction_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("correct_count", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "predictions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("asset", sa.Enum("BTC", "SPX", "GOLD", name="assetenum"), nullable=False),
        sa.Column("timeframe", sa.Enum("daily", "weekly", "monthly", name="timeframeenum"), nullable=False),
        sa.Column("direction", sa.Enum("bullish", "bearish", name="directionenum"), nullable=False),
        sa.Column("price_at_prediction", sa.Float(), nullable=False),
        sa.Column("predicted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("evaluates_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("result", sa.Enum("correct", "incorrect", "pending", name="resultenum"), nullable=False, server_default="pending"),
        sa.Column("evaluated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_predictions_user_id", "predictions", ["user_id"])
    op.create_index("ix_predictions_evaluates_at", "predictions", ["evaluates_at"])


def downgrade() -> None:
    op.drop_table("predictions")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS assetenum")
    op.execute("DROP TYPE IF EXISTS timeframeenum")
    op.execute("DROP TYPE IF EXISTS directionenum")
    op.execute("DROP TYPE IF EXISTS resultenum")
