import csv
import io
import json
import asyncio
import httpx
from fastapi import APIRouter
from app.redis_client import get_redis
from app.config import settings

router = APIRouter(prefix="/api/market", tags=["market"])

CACHE_KEY = "market:prices"
CACHE_TTL = 300  # 5 minutes

STOOQ_INDICES = [
    {"symbol": "^SPX", "label": "S&P 500"},
    {"symbol": "^NDX", "label": "NASDAQ 100"},
]


@router.get("/prices")
async def get_market_prices():
    redis = await get_redis()

    cached = await redis.get(CACHE_KEY)
    if cached:
        return json.loads(cached)

    equities, commodities = await asyncio.gather(
        _fetch_equities_stooq(),
        _fetch_gold_twelve_data(),
    )

    result = {"equities": equities, "commodities": commodities}
    await redis.set(CACHE_KEY, json.dumps(result), ex=CACHE_TTL)
    return result


async def _fetch_equities_stooq() -> list:
    results = []
    async with httpx.AsyncClient(timeout=10) as client:
        for idx in STOOQ_INDICES:
            try:
                resp = await client.get(
                    "https://stooq.com/q/l/",
                    params={"s": idx["symbol"], "f": "sd2t2ohlcv", "h": "", "e": "csv"},
                )
                resp.raise_for_status()
                reader = csv.DictReader(io.StringIO(resp.text))
                row = next(reader, None)
                if not row or row.get("Close") in (None, "N/D", ""):
                    continue
                close = float(row["Close"])
                open_ = float(row["Open"])
                change_percent = ((close - open_) / open_ * 100) if open_ else 0.0
                results.append({
                    "symbol": idx["symbol"],
                    "label": idx["label"],
                    "price": close,
                    "change_percent": round(change_percent, 2),
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
