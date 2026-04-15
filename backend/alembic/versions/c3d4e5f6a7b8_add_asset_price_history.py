"""add asset price history

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-04-15 00:00:00.000000

"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op


revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, Sequence[str], None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS asset_price_history (
            id SERIAL PRIMARY KEY,
            symbol VARCHAR(20) NOT NULL,
            price DOUBLE PRECISION NOT NULL,
            recorded_at TIMESTAMPTZ NOT NULL
        )
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_asset_price_history_symbol
        ON asset_price_history (symbol)
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_asset_price_history_recorded_at
        ON asset_price_history (recorded_at)
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS asset_price_history")
