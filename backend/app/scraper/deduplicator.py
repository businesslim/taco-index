import redis.asyncio as aioredis

SEEN_TWEETS_KEY = "taco:seen_tweet_ids"

async def is_seen(redis: aioredis.Redis, tweet_id: str) -> bool:
    """Redis Set에 tweet_id가 있으면 True(이미 처리됨)를 반환한다."""
    return bool(await redis.sismember(SEEN_TWEETS_KEY, tweet_id))

async def mark_seen(redis: aioredis.Redis, tweet_id: str) -> None:
    """tweet_id를 Redis Set에 추가한다."""
    await redis.sadd(SEEN_TWEETS_KEY, tweet_id)
