import json
import httpx
from fastapi import APIRouter
from app.redis_client import get_redis
from app.config import settings

router = APIRouter(prefix="/api/market", tags=["market"])

CACHE_KEY = "market:prices"
CACHE_TTL = 300  # 5 minutes

SYMBOLS = "SPY,QQQ,XAU/USD"

SYMBOL_META = {
    "SPY":     {"label": "S&P 500",    "category": "equities"},
    "QQQ":     {"label": "NASDAQ 100", "category": "equities"},
    "XAU/USD": {"label": "Gold",       "category": "commodities"},
}


@router.get("/prices")
async def get_market_prices():
    redis = await get_redis()

    cached = await redis.get(CACHE_KEY)
    if cached:
        return json.loads(cached)

    result = await _fetch_from_twelve_data()
    await redis.set(CACHE_KEY, json.dumps(result), ex=CACHE_TTL)
    return result


async def _fetch_from_twelve_data() -> dict:
    url = (
        f"https://api.twelvedata.com/quote"
        f"?symbol={SYMBOLS}&apikey={settings.twelve_data_api_key}"
    )
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
    except Exception:
        return {"equities": [], "commodities": []}

    equities = []
    commodities = []

    for symbol, meta in SYMBOL_META.items():
        quote = data.get(symbol, {})
        if not quote or "code" in quote:
            continue
        try:
            item = {
                "symbol": symbol,
                "label": meta["label"],
                "price": float(quote["close"]),
                "change_percent": float(quote["percent_change"]),
            }
        except (KeyError, ValueError, TypeError):
            continue

        if meta["category"] == "equities":
            equities.append(item)
        else:
            commodities.append(item)

    return {"equities": equities, "commodities": commodities}
