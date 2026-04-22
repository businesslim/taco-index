"""
TACO Index X Bot

트럼프가 market-relevant 포스트를 올릴 때마다 X에 자동 포스팅.
일일 요약은 스케줄러에서 직접 호출.
"""

import logging
from datetime import datetime, timezone
import tweepy
from app.config import settings
from app.redis_client import get_redis

logger = logging.getLogger(__name__)

X_LAST_POSTED_KEY = "x:last_posted_at"
MIN_POST_INTERVAL_SECONDS = 300  # 동일 포스트 중복 방지용 5분 쿨다운

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


def _truncate(text: str, max_len: int) -> str:
    return text[:max_len] + "…" if len(text) > max_len else text


async def post_for_trump_post(
    post: dict,
    final_score: int,
    reasoning: str,
    index_value: int,
    band_label: str,
) -> None:
    """트럼프 market-relevant 포스트마다 X에 트윗."""
    if not settings.x_api_key:
        return

    sentiment = BAND_LABEL.get(band_label, band_label)
    content = post.get("content", "")
    content_preview = _truncate(content, 100)
    reasoning_preview = _truncate(reasoning, 90) if reasoning else ""

    text = (
        f"🌮 TACO: {index_value} ({sentiment}) · Post: {final_score}/100\n\n"
        f'"{content_preview}"\n\n'
        f"{reasoning_preview}\n\n"
        f"👉 taco-index.com #TrumpTrades"
    )

    # 280자 초과 시 reasoning 제거
    if len(text) > 280:
        text = (
            f"🌮 TACO: {index_value} ({sentiment}) · Post: {final_score}/100\n\n"
            f'"{content_preview}"\n\n'
            f"👉 taco-index.com #TrumpTrades"
        )

    try:
        _client().create_tweet(text=text[:280])
        await _mark_posted()
        logger.info(f"X posted for trump post: score={final_score}, index={index_value}")
    except Exception as e:
        logger.error(f"X post failed: {e}")


async def _mark_posted() -> None:
    redis = await get_redis()
    await redis.set(X_LAST_POSTED_KEY, str(datetime.now(timezone.utc).timestamp()))


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


async def maybe_post_update(band_label: str, index_value: int) -> None:
    """하위 호환성 유지용 — 더 이상 사용하지 않음."""
    pass
