"""ensure missing tables

Revision ID: a1b2c3d4e5f6
Revises: db92c6508a50
Create Date: 2026-04-12 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'db92c6508a50'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 초기 마이그레이션이 부분 적용된 경우를 대비해 누락될 수 있는 테이블을 보장
    op.execute("""
        CREATE TABLE IF NOT EXISTS taco_index_history (
            id UUID PRIMARY KEY,
            index_value INTEGER NOT NULL,
            band_label VARCHAR(50) NOT NULL,
            tweet_count INTEGER NOT NULL,
            calculated_at TIMESTAMPTZ NOT NULL
        )
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_taco_index_history_calculated_at
        ON taco_index_history (calculated_at)
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS index_bands (
            id UUID PRIMARY KEY,
            label VARCHAR(50) NOT NULL,
            min_score INTEGER NOT NULL,
            max_score INTEGER NOT NULL,
            color VARCHAR(7) NOT NULL,
            description TEXT NOT NULL,
            CONSTRAINT uq_index_bands_label UNIQUE (label)
        )
    """)
    op.execute("""
        INSERT INTO index_bands (id, label, min_score, max_score, color, description)
        SELECT gen_random_uuid(), v.label, v.min_score, v.max_score, v.color, v.description
        FROM (VALUES
            ('Extreme Bearish', 0,  20,  '#FF4444', 'Trump이 시장에 극도로 부정적인 발언 중'),
            ('Bearish',         21, 40,  '#FF8C00', 'Trump 발언이 시장에 부정적'),
            ('Neutral',         41, 60,  '#FFD700', 'Trump 발언이 시장에 중립적'),
            ('Bullish',         61, 80,  '#32CD32', 'Trump 발언이 시장에 긍정적'),
            ('Extreme Bullish', 81, 100, '#008000', 'Trump이 시장에 극도로 긍정적인 발언 중')
        ) AS v(label, min_score, max_score, color, description)
        WHERE NOT EXISTS (SELECT 1 FROM index_bands WHERE index_bands.label = v.label)
    """)


def downgrade() -> None:
    pass
