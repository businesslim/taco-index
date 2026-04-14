from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from datetime import datetime, timedelta, timezone
from app.database import get_db
from app.redis_client import get_redis
from app.models.index import TacoIndexHistory, IndexBand
from app.schemas.index import CurrentIndexResponse, IndexHistoryResponse, IndexHistoryPoint
from app.analyzer.scorer import get_band_label

router = APIRouter(prefix="/api/index", tags=["index"])

BAND_COLORS = {
    "Taco de Habanero": "#FF4444",
    "Taco de Chorizo":  "#FF8C00",
    "Cooking...":       "#FFD700",
    "Taco de Frijoles": "#32CD32",
    "Taco de CHICKEN":  "#008000",
}

@router.get("/current", response_model=CurrentIndexResponse)
async def get_current_index(
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    # Redis 캐시 확인
    cached = await redis.get("taco:current_index")
    if cached and ":" in cached:
        index_value_str, band_label = cached.split(":", 1)
        index_value = int(index_value_str)
        return CurrentIndexResponse(
            index_value=index_value,
            band_label=band_label,
            band_color=BAND_COLORS.get(band_label, "#FFD700"),
            tweet_count=0,
            calculated_at=datetime.now(timezone.utc),
        )

    # DB 폴백
    result = await db.execute(
        select(TacoIndexHistory).order_by(desc(TacoIndexHistory.calculated_at)).limit(1)
    )
    latest = result.scalar_one_or_none()
    if latest is None:
        return CurrentIndexResponse(
            index_value=50,
            band_label="Cooking...",
            band_color=BAND_COLORS["Cooking..."],
            tweet_count=0,
            calculated_at=None,
        )
    return CurrentIndexResponse(
        index_value=latest.index_value,
        band_label=latest.band_label,
        band_color=BAND_COLORS.get(latest.band_label, "#FFD700"),
        tweet_count=latest.tweet_count,
        calculated_at=latest.calculated_at,
    )


@router.get("/history", response_model=IndexHistoryResponse)
async def get_index_history(
    range: str = Query("7d", pattern="^(7d|30d|all)$"),
    db: AsyncSession = Depends(get_db),
):
    query = select(TacoIndexHistory).order_by(desc(TacoIndexHistory.calculated_at))
    if range == "7d":
        cutoff = datetime.now(timezone.utc) - timedelta(days=7)
        query = query.where(TacoIndexHistory.calculated_at >= cutoff)
    elif range == "30d":
        cutoff = datetime.now(timezone.utc) - timedelta(days=30)
        query = query.where(TacoIndexHistory.calculated_at >= cutoff)

    result = await db.execute(query.limit(1000))
    rows = result.scalars().all()

    return IndexHistoryResponse(data=[
        IndexHistoryPoint(
            index_value=r.index_value,
            band_label=r.band_label,
            calculated_at=r.calculated_at,
        ) for r in rows
    ])
