"""
TACO Index X Bot

밴드 전환 또는 극단값(≥80 / ≤20) 진입 시 자동 포스팅.
2시간 이내 중복 포스팅 방지 (Redis 기반).
"""

import logging
from datetime import datetime, timezone
import tweepy
from app.config import settings
from app.redis_client import get_redis

logger = logging.getLogger(__name__)

X_LAST_BAND_KEY = "x:last_band"
X_LAST_POSTED_KEY = "x:last_posted_at"
MIN_POST_INTERVAL_SECONDS = 7200  # 2시간

BAND_LABEL = {
    "Taco de Habanero": "Extreme Bearish 🌶️",
    "Taco de Chorizo":  "Bearish 🥩",
    "Cooking...":       "Neutral ⏳",
    "Taco de Frijoles": "Bullish 🌮",
    "Taco de CHICKEN":  "Extreme Bullish 🏆",
}


def _client() -> tweepy.Client:
    return tweepy.Client(
        consumer_key=settings.x_api_key,
        consumer_secret=settings.x_api_secret,
        access_token=settings.x_access_token,
        access_token_secret=settings.x_access_token_secret,
    )


async def _can_post(redis) -> bool:
    last = await redis.get(X_LAST_POSTED_KEY)
    if not last:
        return True
    return (datetime.now(timezone.utc).timestamp() - float(last)) >= MIN_POST_INTERVAL_SECONDS


async def _mark_posted(redis, band_label: str) -> None:
    await redis.set(X_LAST_BAND_KEY, band_label)
    await redis.set(X_LAST_POSTED_KEY, str(datetime.now(timezone.utc).timestamp()))


async def maybe_post_update(band_label: str, index_value: int) -> None:
    """밴드 전환 또는 극단값 진입 시 X에 포스팅."""
    if not settings.x_api_key:
        return

    redis = await get_redis()

    if not await _can_post(redis):
        return

    last_band = await redis.get(X_LAST_BAND_KEY)
    band_changed = last_band != band_label
    is_extreme = index_value >= 80 or index_value <= 20

    if not band_changed and not is_extreme:
        return

    sentiment = BAND_LABEL.get(band_label, band_label)

    if band_changed and last_band:
        old_sentiment = BAND_LABEL.get(last_band, last_band)
        text = (
            f"🔄 TACO Index flipped: {old_sentiment} → {sentiment}\n\n"
            f"Score: {index_value} / 100\n\n"
            f"Trump's Truth Social activity is signaling a shift.\n"
            f"👉 taco-index.com\n\n"
            f"#Bitcoin #TrumpTrades #Crypto"
        )
    else:
        text = (
            f"🚨 TACO Index: {index_value} — {sentiment}\n\n"
            f"Extreme signal from Trump's Truth Social.\n"
            f"👉 taco-index.com\n\n"
            f"#Bitcoin #TrumpTrades #Crypto"
        )

    try:
        _client().create_tweet(text=text)
        await _mark_posted(redis, band_label)
        logger.info(f"X posted: {index_value} ({band_label})")
    except Exception as e:
        logger.error(f"X post failed: {e}")


async def post_daily_summary(band_label: str, index_value: int, tweet_count: int) -> None:
    """일일 요약 포스팅 (스케줄러에서 직접 호출)."""
    if not settings.x_api_key:
        return

    sentiment = BAND_LABEL.get(band_label, band_label)
    today = datetime.now(timezone.utc).strftime("%b %d")

    text = (
        f"📊 TACO Index Daily — {today}\n\n"
        f"Closing: {index_value} ({sentiment})\n"
        f"Posts analyzed: {tweet_count}\n\n"
        f"👉 taco-index.com\n\n"
        f"#Bitcoin #TrumpTrades #Crypto"
    )

    try:
        _client().create_tweet(text=text)
        logger.info(f"X daily summary posted: {index_value} ({band_label})")
    except Exception as e:
        logger.error(f"X daily summary failed: {e}")
