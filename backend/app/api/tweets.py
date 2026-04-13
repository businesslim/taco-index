from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.database import get_db
from app.models.tweet import Tweet, TweetScore
from app.schemas.tweet import RecentTweetsResponse, TweetWithScore
from app.analyzer.scorer import get_band_label

router = APIRouter(prefix="/api/tweets", tags=["tweets"])

BAND_COLORS = {
    "Extreme Bearish": "#FF4444",
    "Bearish": "#FF8C00",
    "Neutral": "#FFD700",
    "Bullish": "#32CD32",
    "Extreme Bullish": "#008000",
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
