from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, or_
from app.database import get_db
from app.models.tweet import Tweet, TweetScore
from app.schemas.tweet import RecentTweetsResponse, TweetWithScore
from app.analyzer.scorer import get_band_label

router = APIRouter(prefix="/api/tweets", tags=["tweets"])

BAND_COLORS = {
    "Taco de Habanero": "#FF4444",
    "Taco de Chorizo":  "#FF8C00",
    "Cooking...":       "#FFD700",
    "Taco de Frijoles": "#32CD32",
    "Taco de CHICKEN":  "#008000",
}

@router.get("/recent", response_model=RecentTweetsResponse)
async def get_recent_tweets(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Tweet, TweetScore)
        .join(TweetScore, Tweet.id == TweetScore.tweet_id)
        .order_by(desc(Tweet.posted_at))
        .limit(limit)
    )
    rows = result.all()

    data = []
    for tweet, score in rows:
        band_label = get_band_label(score.final_score)
        data.append(TweetWithScore(
            tweet_id=tweet.tweet_id,
            source=tweet.source,
            content=tweet.content,
            posted_at=tweet.posted_at,
            final_score=score.final_score,
            band_label=band_label,
            band_color=BAND_COLORS.get(band_label, "#FFD700"),
            llm_reasoning=score.llm_reasoning,
            market_relevant=score.market_relevant,
        ))

    return RecentTweetsResponse(data=data)


@router.get("/notable", response_model=RecentTweetsResponse)
async def get_notable_tweets(
    range: str = Query("7d", pattern="^(1d|7d|30d)$"),
    db: AsyncSession = Depends(get_db),
):
    """점수가 40 이하이거나 60 이상인 market-relevant 포스트를 반환한다."""
    days_map = {"1d": 1, "7d": 7, "30d": 30}
    cutoff = datetime.now(timezone.utc) - timedelta(days=days_map[range])

    result = await db.execute(
        select(Tweet, TweetScore)
        .join(TweetScore, Tweet.id == TweetScore.tweet_id)
        .where(Tweet.posted_at >= cutoff)
        .where(or_(TweetScore.final_score <= 40, TweetScore.final_score >= 60))
        .where(TweetScore.market_relevant == True)
        .order_by(Tweet.posted_at)
    )
    rows = result.all()

    data = []
    for tweet, score in rows:
        band_label = get_band_label(score.final_score)
        data.append(TweetWithScore(
            tweet_id=tweet.tweet_id,
            source=tweet.source,
            content=tweet.content,
            posted_at=tweet.posted_at,
            final_score=score.final_score,
            band_label=band_label,
            band_color=BAND_COLORS.get(band_label, "#FFD700"),
            llm_reasoning=score.llm_reasoning,
            market_relevant=score.market_relevant,
        ))

    return RecentTweetsResponse(data=data)
