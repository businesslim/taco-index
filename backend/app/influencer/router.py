from datetime import date, timedelta, datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.influencer.models import (
    Influencer, InfluencerTweet, InfluencerIndex,
    AssetExpertIndex, WeeklyInfluencerRank,
)
from app.influencer.schemas import (
    InfluencerIndexOut, InfluencerSummaryOut,
    AssetExpertIndexOut, BullBearRatio, WeeklyRankEntry,
)
from app.influencer.calculator import score_to_band

router = APIRouter(prefix="/influencer", tags=["influencer"])


@router.get("/summary", response_model=InfluencerSummaryOut)
async def get_summary(db: AsyncSession = Depends(get_db)):
    # Asset Expert Indexes
    asset_result = await db.execute(select(AssetExpertIndex))
    asset_rows = asset_result.scalars().all()
    asset_indexes = [
        AssetExpertIndexOut(
            asset=r.asset,
            score=r.score,
            band=score_to_band(r.score),
            bull_count=r.bull_count,
            bear_count=r.bear_count,
            neutral_count=r.neutral_count,
            total_count=r.total_count,
            calculated_at=r.calculated_at,
        )
        for r in asset_rows
    ]

    # Bull-Bear Ratio
    all_result = await db.execute(select(InfluencerIndex))
    all_indexes = all_result.scalars().all()
    bull = sum(1 for i in all_indexes if i.score > 60)
    bear = sum(1 for i in all_indexes if i.score <= 40)
    neutral = len(all_indexes) - bull - bear
    bull_bear = BullBearRatio(
        bull_count=bull, bear_count=bear,
        neutral_count=neutral, total_count=len(all_indexes),
    )

    # Weekly Rank
    week_start = date.today() - timedelta(days=date.today().weekday())
    rank_result = await db.execute(
        select(WeeklyInfluencerRank, Influencer)
        .join(Influencer, WeeklyInfluencerRank.influencer_id == Influencer.id)
        .where(WeeklyInfluencerRank.week_start == week_start)
    )
    rank_rows = rank_result.all()

    top_bull = sorted(
        [(r, inf) for r, inf in rank_rows if r.rank_bull is not None],
        key=lambda x: x[0].rank_bull,
    )[:5]
    top_bear = sorted(
        [(r, inf) for r, inf in rank_rows if r.rank_bear is not None],
        key=lambda x: x[0].rank_bear,
    )[:5]

    return InfluencerSummaryOut(
        asset_indexes=asset_indexes,
        bull_bear_ratio=bull_bear,
        weekly_top_bull=[
            WeeklyRankEntry(handle=inf.handle, name=inf.name,
                           avg_score=r.avg_score, rank_bull=r.rank_bull, rank_bear=r.rank_bear)
            for r, inf in top_bull
        ],
        weekly_top_bear=[
            WeeklyRankEntry(handle=inf.handle, name=inf.name,
                           avg_score=r.avg_score, rank_bull=r.rank_bull, rank_bear=r.rank_bear)
            for r, inf in top_bear
        ],
    )


@router.get("", response_model=list[InfluencerIndexOut])
async def get_influencers(
    category: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    q = select(InfluencerIndex, Influencer).join(
        Influencer, InfluencerIndex.influencer_id == Influencer.id
    )
    if category:
        q = q.where(Influencer.category == category)
    result = await db.execute(q)
    rows = result.all()

    out = []
    for idx, inf in rows:
        tweet_result = await db.execute(
            select(InfluencerTweet)
            .where(InfluencerTweet.influencer_id == inf.id)
            .order_by(InfluencerTweet.posted_at.desc())
            .limit(1)
        )
        tweet = tweet_result.scalar_one_or_none()
        out.append(InfluencerIndexOut(
            handle=inf.handle,
            name=inf.name,
            category=inf.category,
            domain=inf.domain,
            score=idx.score,
            band=idx.band,
            calculated_at=idx.calculated_at,
            latest_tweet=tweet.content if tweet else None,
        ))
    return out


@router.get("/{handle}", response_model=InfluencerIndexOut)
async def get_influencer(handle: str, db: AsyncSession = Depends(get_db)):
    inf_result = await db.execute(
        select(Influencer).where(Influencer.handle == handle)
    )
    inf = inf_result.scalar_one_or_none()
    if not inf:
        raise HTTPException(status_code=404, detail="Influencer not found")

    idx_result = await db.execute(
        select(InfluencerIndex).where(InfluencerIndex.influencer_id == inf.id)
    )
    idx = idx_result.scalar_one_or_none()

    tweet_result = await db.execute(
        select(InfluencerTweet)
        .where(InfluencerTweet.influencer_id == inf.id)
        .order_by(InfluencerTweet.posted_at.desc())
        .limit(1)
    )
    tweet = tweet_result.scalar_one_or_none()

    return InfluencerIndexOut(
        handle=inf.handle,
        name=inf.name,
        category=inf.category,
        domain=inf.domain,
        score=idx.score if idx else 50,
        band=idx.band if idx else "Neutral",
        calculated_at=idx.calculated_at if idx else None,
        latest_tweet=tweet.content if tweet else None,
    )
