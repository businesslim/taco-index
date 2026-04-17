"""add influencer tables

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-04-17 00:00:00.000000

"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, Sequence[str], None] = 'c3d4e5f6a7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'influencers',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('handle', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('domain', sa.String(50), nullable=False),
        sa.Column('x_user_id', sa.String(255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('last_fetched_tweet_id', sa.String(255), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('handle'),
        sa.UniqueConstraint('x_user_id'),
    )

    op.create_table(
        'influencer_tweets',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('influencer_id', sa.Integer(), nullable=False),
        sa.Column('tweet_id', sa.String(255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('posted_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            'fetched_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(['influencer_id'], ['influencers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tweet_id'),
    )
    op.create_index('ix_influencer_tweets_posted_at', 'influencer_tweets', ['posted_at'])

    op.create_table(
        'influencer_tweet_scores',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('tweet_id', sa.String(255), nullable=False),
        sa.Column('llm_score', sa.Integer(), nullable=False),
        sa.Column('keyword_score', sa.Integer(), nullable=False),
        sa.Column('final_score', sa.Integer(), nullable=False),
        sa.Column('domain', sa.String(50), nullable=False),
        sa.Column('reasoning', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['tweet_id'], ['influencer_tweets.tweet_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tweet_id'),
    )

    op.create_table(
        'influencer_index',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('influencer_id', sa.Integer(), nullable=False),
        sa.Column('score', sa.Integer(), nullable=False, server_default='50'),
        sa.Column('band', sa.String(50), nullable=False, server_default='Neutral'),
        sa.Column(
            'calculated_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(['influencer_id'], ['influencers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('influencer_id'),
    )

    op.create_table(
        'asset_expert_index',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('asset', sa.String(50), nullable=False),
        sa.Column('score', sa.Integer(), nullable=False, server_default='50'),
        sa.Column('bull_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('bear_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('neutral_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column(
            'calculated_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('asset'),
    )

    op.create_table(
        'weekly_influencer_ranks',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('week_start', sa.Date(), nullable=False),
        sa.Column('influencer_id', sa.Integer(), nullable=False),
        sa.Column('avg_score', sa.Integer(), nullable=False),
        sa.Column('rank_bull', sa.Integer(), nullable=True),
        sa.Column('rank_bear', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['influencer_id'], ['influencers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('week_start', 'influencer_id', name='uq_weekly_rank_week_influencer'),
    )


def downgrade() -> None:
    op.drop_table('weekly_influencer_ranks')
    op.drop_table('asset_expert_index')
    op.drop_table('influencer_index')
    op.drop_table('influencer_tweet_scores')
    op.drop_index('ix_influencer_tweets_posted_at', table_name='influencer_tweets')
    op.drop_table('influencer_tweets')
    op.drop_table('influencers')
