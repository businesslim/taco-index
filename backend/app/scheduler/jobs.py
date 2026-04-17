import logging
import httpx
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, desc, true
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.redis_client import get_redis
from app.scraper.truth_social import fetch_truth_social_posts
from app.scraper.deduplicator import is_seen, mark_seen
from app.analyzer import (
    compute_keyword_score, analyze_tweet, compute_final_score,
    compute_taco_index, get_band_label, BULLISH_KEYWORDS, BEARISH_KEYWORDS,
)
from app.models.tweet import Tweet, TweetScore
from app.models.index import TacoIndexHistory
from app.models.asset_price import AssetPriceHistory
from app.config import settings

logger = logging.getLogger(__name__)

TACO_INDEX_CACHE_KEY = "taco:current_index"


async def run_pipeline() -> None:
    """스크래핑 → 분석 → 저장 → 인덱스 계산 파이프라인."""
    logger.info("Pipeline started")
    redis = await get_redis()

    # 1. 스크래핑 (실패해도 인덱스 재계산은 계속 진행)
    posts = []
    try:
        posts = await fetch_truth_social_posts()
    except Exception as e:
        logger.error(f"Scraping failed: {e}")

    # 2. 새 트윗 필터링 + 분석 + 저장
    new_count = 0
    async with AsyncSessionLocal() as db:
        for post in posts:
            if await is_seen(redis, post["tweet_id"]):
                continue

            # 키워드 힌트 추출
            lower = post["content"].lower()
            hints = [kw for kw in (BULLISH_KEYWORDS + BEARISH_KEYWORDS) if kw in lower]

            # LLM 분석
            try:
                llm_score, reasoning, market_relevant = analyze_tweet(post["content"], hints)
            except Exception as e:
                logger.error(f"LLM analysis failed for tweet {post['tweet_id']}: {e}")
                llm_score, reasoning, market_relevant = 50, "Analysis unavailable", True

            keyword_score = compute_keyword_score(post["content"])
            final_score = compute_final_score(llm_score, keyword_score)

            tweet = Tweet(
                source=post["source"],
                tweet_id=post["tweet_id"],
                content=post["content"],
                posted_at=post["posted_at"],
                fetched_at=datetime.now(timezone.utc),
                raw_data=post["raw_data"],
            )
            db.add(tweet)
            await db.flush()  # tweet.id 확보

            score = TweetScore(
                tweet_id=tweet.id,
                llm_score=llm_score,
                keyword_score=keyword_score,
                final_score=final_score,
                llm_reasoning=reasoning,
                market_relevant=market_relevant,
                analyzed_at=datetime.now(timezone.utc),
            )
            db.add(score)
            await mark_seen(redis, post["tweet_id"])
            new_count += 1

        await db.commit()
        logger.info(f"Saved {new_count} new tweets")

        # 3. TACO Index 재계산 (새 포스트 없어도 항상 실행)
        band_label, index_value = await recalculate_index(db, redis)

    # 4. 자산 가격 DB 저장 (자체 히스토리 수집)
    await save_asset_prices()

    # 5. 새 포스트가 있을 때만 텔레그램 알림 발송
    if new_count > 0:
        try:
            from app.telegram_bot import notify_subscribers
            await notify_subscribers(band_label, index_value, new_count)
        except Exception as e:
            logger.error(f"Telegram notify failed: {e}")


async def recalculate_index(db: AsyncSession, redis) -> None:
    """최근 72시간 트윗으로 TACO Index를 재계산하고 DB + Redis에 저장."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=72)
    result = await db.execute(
        select(Tweet, TweetScore)
        .join(TweetScore, Tweet.id == TweetScore.tweet_id)
        .where(Tweet.posted_at >= cutoff)
        .where(TweetScore.market_relevant == true())
        .order_by(desc(Tweet.posted_at))
    )
    rows = result.all()

    scored_tweets = [
        {"final_score": score.final_score, "posted_at": tweet.posted_at}
        for tweet, score in rows
    ]

    index_value = compute_taco_index(scored_tweets)
    band_label = get_band_label(index_value)

    history = TacoIndexHistory(
        index_value=index_value,
        band_label=band_label,
        tweet_count=len(scored_tweets),
        calculated_at=datetime.now(timezone.utc),
    )
    db.add(history)
    await db.commit()

    # Redis 캐시 업데이트 (1시간 TTL)
    await redis.set(TACO_INDEX_CACHE_KEY, f"{index_value}:{band_label}", ex=3600)
    logger.info(f"TACO Index updated: {index_value} ({band_label})")
    return band_label, index_value


async def save_asset_prices() -> None:
    """BTC, SPX, Gold 현재가를 DB에 저장한다 (자체 히스토리 수집)."""
    now = datetime.now(timezone.utc)
    prices = []

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            # BTC (CoinGecko simple price)
            try:
                resp = await client.get(
                    "https://api.coingecko.com/api/v3/simple/price",
                    params={"ids": "bitcoin", "vs_currencies": "usd"},
                )
                data = resp.json()
                if "bitcoin" in data and "usd" in data["bitcoin"]:
                    btc_price = data["bitcoin"]["usd"]
                    prices.append(AssetPriceHistory(symbol="BTC", price=btc_price, recorded_at=now))
                else:
                    logger.warning(f"BTC price fetch unexpected response: {data}")
            except Exception as e:
                logger.warning(f"BTC price fetch failed: {e}")

            # SPX (Yahoo Finance)
            try:
                resp = await client.get(
                    "https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC",
                    params={"interval": "1d", "range": "1d"},
                    headers={"User-Agent": "Mozilla/5.0"},
                )
                data = resp.json()
                closes = data["chart"]["result"][0]["indicators"]["quote"][0]["close"]
                spx_price = next((p for p in reversed(closes) if p is not None), None)
                if spx_price is not None:
                    prices.append(AssetPriceHistory(symbol="SPX", price=spx_price, recorded_at=now))
            except Exception as e:
                logger.warning(f"SPX price fetch failed: {e}")

            # Gold (Twelve Data)
            try:
                resp = await client.get(
                    "https://api.twelvedata.com/quote",
                    params={"symbol": "XAU/USD", "apikey": settings.twelve_data_api_key},
                )
                data = resp.json()
                if "close" in data:
                    prices.append(AssetPriceHistory(symbol="GOLD", price=float(data["close"]), recorded_at=now))
            except Exception as e:
                logger.warning(f"Gold price fetch failed: {e}")

    except Exception as e:
        logger.error(f"save_asset_prices failed: {e}")
        return

    if prices:
        async with AsyncSessionLocal() as db:
            for p in prices:
                db.add(p)
            await db.commit()
        logger.info(f"Saved {len(prices)} asset prices")


def start_scheduler():
    """APScheduler를 시작해 파이프라인을 주기적으로 실행한다."""
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from app.influencer.scheduler import run_influencer_pipeline
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        run_pipeline,
        "interval",
        minutes=settings.poll_interval_minutes,
        id="taco_pipeline",
        replace_existing=True,
    )
    scheduler.add_job(
        run_influencer_pipeline,
        "interval",
        minutes=30,
        id="influencer_pipeline",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(f"Scheduler started: polling every {settings.poll_interval_minutes} minutes")
    return scheduler
