import asyncio
import httpx

NITTER_INSTANCES = [
    "https://nitter.poast.org",
    "https://nitter.privacydev.net",
    "https://nitter.1d4.us",
    "https://nitter.kavin.rocks",
    "https://nitter.net",
]

HANDLE = "realDonaldTrump"

async def check():
    async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
        for base in NITTER_INSTANCES:
            url = f"{base}/{HANDLE}/rss"
            try:
                r = await client.get(url)
                is_rss = "<rss" in r.text[:300] or "<feed" in r.text[:300]
                print(f"{url}")
                print(f"  status: {r.status_code}, is_rss: {is_rss}")
                if is_rss:
                    print(f"  ✅ WORKING! First entry snippet:")
                    import feedparser
                    feed = feedparser.parse(r.text)
                    print(f"  entries: {len(feed.entries)}")
                    if feed.entries:
                        print(f"  latest: {feed.entries[0].get('title', '')[:100]}")
                    break
            except Exception as e:
                print(f"  error: {e}")

asyncio.run(check())
