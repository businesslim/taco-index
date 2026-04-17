import logging
from collections import defaultdict
from datetime import datetime, timedelta, date, timezone
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.influencer.models import (
    Influencer, InfluencerTweet, InfluencerTweetScore,
    InfluencerIndex, AssetExpertIndex, WeeklyInfluencerRank,
)
from app.influencer.fetcher import XApiFetcher
from app.influencer.scorer import score_influencer_post
from app.influencer.calculator import (
    calculate_influencer_index,
    calculate_asset_expert_indexes,
    calculate_weekly_ranks,
    score_to_band,
)

logger = logging.getLogger(__name__)


async def run_influencer_pipeline() -> None:
    """30분마다 실행. 각 인플루언서는 독립적으로 처리."""
    logger.info("Influencer pipeline started")
    fetcher = XApiFetcher()

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Influencer).where(Influencer.is_active == True)
        )
        influencers = result.scalars().all()
        logger.info(f"Processing {len(influencers)} influencers")

        for inf in influencers:
            try:
                await _process_influencer(db, fetcher, inf)
            except Exception as e:
                logger.error(f"Failed to process @{inf.handle}: {e}")
                await db.rollback()
                continue

        await _update_asset_expert_indexes(db)
        await _update_weekly_ranks(db)
        await db.commit()
        logger.info("Influencer pipeline completed")


async def _process_influencer(db: AsyncSession, fetcher: XApiFetcher, inf: Influencer) -> None:
    if not inf.x_user_id:
        return

    tweets = fetcher.fetch_tweets(x_user_id=inf.x_user_id, since_id=inf.last_fetched_tweet_id)
    if not tweets:
        return

    newest_id = None
    for t in tweets:
        # Skip if already exists
        existing = await db.execute(
            select(InfluencerTweet).where(InfluencerTweet.tweet_id == t["tweet_id"])
        )
        if existing.scalar_one_or_none():
            continue

        tweet_row = InfluencerTweet(
            influencer_id=inf.id,
            tweet_id=t["tweet_id"],
            content=t["content"],
            posted_at=t["posted_at"],
        )
        db.add(tweet_row)
        await db.flush()

        scores = score_influencer_post(t["content"], inf.domain)
        score_row = InfluencerTweetScore(
            tweet_id=t["tweet_id"],
            llm_score=scores["llm_score"],
            keyword_score=scores["keyword_score"],
            final_score=scores["final_score"],
            domain=inf.domain,
            reasoning=scores["reasoning"],
        )
        db.add(score_row)
        newest_id = t["tweet_id"]

    if newest_id:
        inf.last_fetched_tweet_id = newest_id

    # Recalculate InfluencerIndex (72h window)
    cutoff = datetime.now(timezone.utc) - timedelta(hours=72)
    scores_result = await db.execute(
        select(InfluencerTweetScore, InfluencerTweet)
        .join(InfluencerTweet, InfluencerTweetScore.tweet_id == InfluencerTweet.tweet_id)
        .where(
            and_(
                InfluencerTweet.influencer_id == inf.id,
                InfluencerTweet.posted_at >= cutoff,
            )
        )
    )
    rows = scores_result.all()
    score_data = [
        {"final_score": score.final_score, "posted_at": tweet.posted_at}
        for score, tweet in rows
    ]

    new_score = calculate_influencer_index(score_data)
    band = score_to_band(new_score)

    idx_result = await db.execute(
        select(InfluencerIndex).where(InfluencerIndex.influencer_id == inf.id)
    )
    idx = idx_result.scalar_one_or_none()
    if idx:
        idx.score = new_score
        idx.band = band
        idx.calculated_at = datetime.now(timezone.utc)
    else:
        db.add(InfluencerIndex(influencer_id=inf.id, score=new_score, band=band))


async def _update_asset_expert_indexes(db: AsyncSession) -> None:
    result = await db.execute(
        select(InfluencerIndex, Influencer)
        .join(Influencer, InfluencerIndex.influencer_id == Influencer.id)
    )
    rows = result.all()
    influencer_scores = [
        {"domain": inf.domain, "score": idx.score}
        for idx, inf in rows
    ]
    asset_results = calculate_asset_expert_indexes(influencer_scores)
    now = datetime.now(timezone.utc)

    for r in asset_results:
        existing_result = await db.execute(
            select(AssetExpertIndex).where(AssetExpertIndex.asset == r["asset"])
        )
        existing = existing_result.scalar_one_or_none()
        if existing:
            existing.score = r["score"]
            existing.bull_count = r["bull_count"]
            existing.bear_count = r["bear_count"]
            existing.neutral_count = r["neutral_count"]
            existing.total_count = r["total_count"]
            existing.calculated_at = now
        else:
            db.add(AssetExpertIndex(
                asset=r["asset"],
                score=r["score"],
                bull_count=r["bull_count"],
                bear_count=r["bear_count"],
                neutral_count=r["neutral_count"],
                total_count=r["total_count"],
            ))


async def _update_weekly_ranks(db: AsyncSession) -> None:
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    week_start = date.today() - timedelta(days=date.today().weekday())

    scores_result = await db.execute(
        select(InfluencerTweetScore, InfluencerTweet, Influencer)
        .join(InfluencerTweet, InfluencerTweetScore.tweet_id == InfluencerTweet.tweet_id)
        .join(Influencer, InfluencerTweet.influencer_id == Influencer.id)
        .where(InfluencerTweet.posted_at >= cutoff)
    )
    rows = scores_result.all()

    grouped: dict[int, list[int]] = defaultdict(list)
    inf_meta: dict[int, Influencer] = {}
    for score, tweet, inf in rows:
        grouped[inf.id].append(score.final_score)
        inf_meta[inf.id] = inf

    weekly_scores = [
        {
            "influencer_id": inf_id,
            "handle": inf_meta[inf_id].handle,
            "name": inf_meta[inf_id].name,
            "avg_score": round(sum(scores) / len(scores)),
        }
        for inf_id, scores in grouped.items()
    ]
    ranks = calculate_weekly_ranks(weekly_scores)

    for rank_pos, item in enumerate(ranks["top_bull"], 1):
        existing_result = await db.execute(
            select(WeeklyInfluencerRank).where(
                and_(
                    WeeklyInfluencerRank.week_start == week_start,
                    WeeklyInfluencerRank.influencer_id == item["influencer_id"],
                )
            )
        )
        existing = existing_result.scalar_one_or_none()
        if existing:
            existing.rank_bull = rank_pos
            existing.avg_score = item["avg_score"]
        else:
            db.add(WeeklyInfluencerRank(
                week_start=week_start,
                influencer_id=item["influencer_id"],
                avg_score=item["avg_score"],
                rank_bull=rank_pos,
            ))

    for rank_pos, item in enumerate(ranks["top_bear"], 1):
        existing_result = await db.execute(
            select(WeeklyInfluencerRank).where(
                and_(
                    WeeklyInfluencerRank.week_start == week_start,
                    WeeklyInfluencerRank.influencer_id == item["influencer_id"],
                )
            )
        )
        existing = existing_result.scalar_one_or_none()
        if existing:
            existing.rank_bear = rank_pos
        else:
            db.add(WeeklyInfluencerRank(
                week_start=week_start,
                influencer_id=item["influencer_id"],
                avg_score=item["avg_score"],
                rank_bear=rank_pos,
            ))
