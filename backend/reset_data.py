import asyncio
import redis.asyncio as aioredis

async def reset():
    r = aioredis.from_url('redis://localhost:6379/0', decode_responses=True)
    await r.delete('taco:seen_tweet_ids')
    await r.delete('taco:current_index')
    await r.aclose()
    print('Redis cleared')

asyncio.run(reset())
