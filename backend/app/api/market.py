import csv
import io
import json
import asyncio
import httpx
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, Query
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


@router.get("/history")
async def get_market_history(
    range: str = Query("7d", pattern="^(1d|7d|30d)$"),
    redis=Depends(get_redis),
):
    cache_key = f"market:history:{range}"
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)

    btc, spx, gold = await asyncio.gather(
        _fetch_btc_history(range),
        _fetch_spx_history(range),
        _fetch_gold_history(range),
    )

    result = {"btc": btc, "spx": spx, "gold": gold}
    ttl = 300 if range == "1d" else 1800
    await redis.set(cache_key, json.dumps(result), ex=ttl)
    return result


def _bucket_key(ts_ms: float, interval: str) -> str:
    dt = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
    if interval == "hourly":
        return dt.strftime("%Y-%m-%dT%H:00:00Z")
    return dt.strftime("%Y-%m-%dT00:00:00Z")


def _aggregate_to_buckets(prices: list[tuple], interval: str) -> list[dict]:
    buckets: dict[str, list[float]] = {}
    for ts_ms, price in prices:
        key = _bucket_key(ts_ms, interval)
        buckets.setdefault(key, []).append(price)
    return [
        {"t": k, "price": round(sum(v) / len(v), 2)}
        for k, v in sorted(buckets.items())
    ]


async def _fetch_btc_history(range: str) -> list:
    days_map = {"1d": 2, "7d": 7, "30d": 30}
    days = days_map[range]
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart",
                params={"vs_currency": "usd", "days": days},
            )
            resp.raise_for_status()
            raw_prices = resp.json().get("prices", [])

        cutoff_ms = (datetime.now(timezone.utc) - timedelta(days=int(range[:-1]))).timestamp() * 1000
        filtered = [(ts, p) for ts, p in raw_prices if ts >= cutoff_ms]
        interval = "hourly" if range == "1d" else "daily"
        return _aggregate_to_buckets(filtered, interval)
    except Exception:
        return []


async def _fetch_spx_history(range: str) -> list:
    import logging
    logger = logging.getLogger(__name__)

    interval_map = {"1d": ("1h", "1d"), "7d": ("1d", "7d"), "30d": ("1d", "1mo")}
    interval, yf_range = interval_map[range]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
    }
    for base_url in [
        "https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC",
        "https://query2.finance.yahoo.com/v8/finance/chart/%5EGSPC",
    ]:
        try:
            async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
                resp = await client.get(
                    base_url,
                    params={"interval": interval, "range": yf_range},
                    headers=headers,
                )
                resp.raise_for_status()
                data = resp.json()
            result_data = data["chart"]["result"][0]
            timestamps = result_data["timestamp"]
            closes = result_data["indicators"]["quote"][0]["close"]
            bucket_interval = "hourly" if range == "1d" else "daily"
            pairs = [(ts * 1000, price) for ts, price in zip(timestamps, closes) if price is not None]
            return _aggregate_to_buckets(pairs, bucket_interval)
        except Exception as e:
            logger.error(f"SPX history fetch failed ({base_url}): {e}")
            continue
    return []


async def _fetch_gold_history(range: str) -> list:
    interval_map = {"1d": ("1h", 24), "7d": ("1day", 7), "30d": ("1day", 30)}
    interval, outputsize = interval_map[range]
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                "https://api.twelvedata.com/time_series",
                params={
                    "symbol": "XAU/USD",
                    "interval": interval,
                    "outputsize": outputsize,
                    "apikey": settings.twelve_data_api_key,
                    "order": "ASC",
                },
            )
            resp.raise_for_status()
            data = resp.json()
        if "code" in data or "values" not in data:
            return []
        return [
            {"t": v["datetime"].replace(" ", "T") + ("Z" if "+" not in v["datetime"] else ""),
             "price": float(v["close"])}
            for v in data["values"]
        ]
    except Exception:
        return []


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
