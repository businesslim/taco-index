import asyncio
import httpx
import feedparser

async def check():
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get('https://truthsocial.com/@realDonaldTrump.rss')
        print('status:', r.status_code)
        print('content length:', len(r.text))
        print('first 500 chars:', r.text[:500])
        feed = feedparser.parse(r.text)
        print('entries:', len(feed.entries))
        if feed.entries:
            e = feed.entries[0]
            print('keys:', list(e.keys()))
            print('id:', e.get('id'))
            print('title:', e.get('title', '')[:80])

asyncio.run(check())
