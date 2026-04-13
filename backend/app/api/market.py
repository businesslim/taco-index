import json
import asyncio
import httpx
from fastapi import APIRouter
from app.redis_client import get_redis
from app.config import settings

router = APIRouter(prefix="/api/market", tags=["market"])

CACHE_KEY = "market:prices"
CACHE_TTL = 300  # 5 minutes

FINNHUB_INDICES = [
    {"symbol": "^GSPC", "label": "S&P 500"},
    {"symbol": "^NDX",  "label": "NASDAQ 100"},
]


@router.get("/prices")
async def get_market_prices():
    redis = await get_redis()

    cached = await redis.get(CACHE_KEY)
    if cached:
        return json.loads(cached)

    equities, commodities = await asyncio.gather(
        _fetch_equities_finnhub(),
        _fetch_gold_twelve_data(),
    )

    result = {"equities": equities, "commodities": commodities}
    await redis.set(CACHE_KEY, json.dumps(result), ex=CACHE_TTL)
    return result


async def _fetch_equities_finnhub() -> list:
    results = []
    async with httpx.AsyncClient(timeout=10) as client:
        for idx in FINNHUB_INDICES:
            try:
                resp = await client.get(
                    "https://finnhub.io/api/v1/quote",
                    params={"symbol": idx["symbol"], "token": settings.finnhub_api_key},
                )
                resp.raise_for_status()
                data = resp.json()
                results.append({
                    "symbol": idx["symbol"],
                    "label": idx["label"],
                    "price": float(data["c"]),
                    "change_percent": float(data["dp"]),
                })
            except Exception:
                continue
    return results


async def _fetch_gold_twelve_data() -> list:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                "https://api.twelvedata.com/quote",
                params={"symbol": "XAU/USD", "apikey": settings.twelve_data_api_key},
            )
            resp.raise_for_status()
            data = resp.json()
        if "code" in data:
            return []
        return [{
            "symbol": "XAU/USD",
            "label": "Gold",
            "price": float(data["close"]),
            "change_percent": float(data["percent_change"]),
        }]
    except Exception:
        return []
