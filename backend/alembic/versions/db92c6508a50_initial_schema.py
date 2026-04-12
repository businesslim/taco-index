"""initial schema

Revision ID: db92c6508a50
Revises:
Create Date: 2026-04-11 14:22:50.614755

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'db92c6508a50'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # IF NOT EXISTS로 처리 — 부분 적용된 DB에서도 안전하게 실행됨
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
        CREATE TABLE IF NOT EXISTS tweets (
            id UUID PRIMARY KEY,
            source VARCHAR(50) NOT NULL,
            tweet_id VARCHAR(255) NOT NULL,
            content TEXT NOT NULL,
            posted_at TIMESTAMPTZ NOT NULL,
            fetched_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            raw_data JSONB NOT NULL,
            CONSTRAINT uq_tweets_tweet_id UNIQUE (tweet_id)
        )
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_tweets_tweet_id ON tweets (tweet_id)
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS tweet_scores (
            id UUID PRIMARY KEY,
            tweet_id UUID NOT NULL,
            llm_score INTEGER NOT NULL,
            keyword_score INTEGER NOT NULL,
            final_score INTEGER NOT NULL,
            llm_reasoning TEXT NOT NULL,
            analyzed_at TIMESTAMPTZ NOT NULL,
            CONSTRAINT uq_tweet_scores_tweet_id UNIQUE (tweet_id),
            CONSTRAINT fk_tweet_scores_tweet_id FOREIGN KEY (tweet_id)
                REFERENCES tweets(id) ON DELETE CASCADE
        )
    """)
    # 밴드 데이터 삽입 — 이미 있으면 스킵
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
    op.execute("DELETE FROM index_bands")
    op.execute("DROP TABLE IF EXISTS tweet_scores")
    op.execute("DROP INDEX IF EXISTS ix_tweets_tweet_id")
    op.execute("DROP TABLE IF EXISTS tweets")
    op.execute("DROP INDEX IF EXISTS ix_taco_index_history_calculated_at")
    op.execute("DROP TABLE IF EXISTS taco_index_history")
    op.execute("DROP TABLE IF EXISTS index_bands")
