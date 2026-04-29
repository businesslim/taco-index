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


PER_POST_HASHTAGS = "#TacoIndex #TrumpTrades #Bitcoin #SP500 #Markets"
DAILY_HASHTAGS = "#TacoIndex #TrumpTrades #Bitcoin #Crypto #SP500 #Markets #Trump"
TRUTH_USER = "realDonaldTrump"
TWEET_LIMIT = 280
TCO_URL_LENGTH = 23  # X auto-shortens URLs to t.co/xxxx (23 chars)


def _truncate(text: str, max_len: int) -> str:
    return text[:max_len] + "…" if len(text) > max_len else text


def _truth_social_url(tweet_id: str) -> str:
    return f"https://truthsocial.com/@{TRUTH_USER}/posts/{tweet_id}"


def _effective_length(text: str, urls: list[str]) -> int:
    """X 트윗 길이 계산 — URL은 t.co로 단축돼 23자로 카운트된다."""
    placeholder = "x" * TCO_URL_LENGTH
    estimated = text
    for url in urls:
        if url:
            estimated = estimated.replace(url, placeholder)
    return len(estimated)


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
    tweet_id = str(post.get("tweet_id", "")).strip()
    truth_url = _truth_social_url(tweet_id) if tweet_id else "https://www.taco-index.com"

    content = post.get("content", "")
    header = f"🌮 TACO: {index_value} ({sentiment}) · Post: {final_score}/100"
    mention_line = f"@{TRUTH_USER} {truth_url}"

    # 길이 한도 안에서 가장 풍부한 후보부터 시도.
    # X는 이모지를 가중치 2로 카운트하므로 raw 길이는 ~270 이하로 보수적으로 잡는다.
    candidates: list[str] = []
    if reasoning:
        candidates.append(
            f"{header}\n\n"
            f'"{_truncate(content, 75)}"\n\n'
            f"💡 {_truncate(reasoning, 55)}\n\n"
            f"{mention_line}\n{PER_POST_HASHTAGS}"
        )
    candidates.append(
        f"{header}\n\n"
        f'"{_truncate(content, 130)}"\n\n'
        f"{mention_line}\n{PER_POST_HASHTAGS}"
    )
    candidates.append(
        f"{header}\n\n"
        f"{mention_line}\n{PER_POST_HASHTAGS}"
    )

    text = next(
        (c for c in candidates if _effective_length(c, [truth_url]) <= TWEET_LIMIT),
        candidates[-1],
    )

    try:
        _client().create_tweet(text=text)
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
        f"👉 https://www.taco-index.com\n\n"
        f"{DAILY_HASHTAGS}"
    )

    try:
        _client().create_tweet(text=text)
        logger.info(f"X daily summary posted: {index_value} ({band_label})")
    except Exception as e:
        logger.error(f"X daily summary failed: {e}")


async def maybe_post_update(band_label: str, index_value: int) -> None:
    """하위 호환성 유지용 — 더 이상 사용하지 않음."""
    pass
