import asyncio
import httpx

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}

URLS = [
    "https://truthsocial.com/@realDonaldTrump.rss",
    "https://truthsocial.com/users/realDonaldTrump.rss",
    "https://truthsocial.com/@realDonaldTrump/feed",
]

async def check():
    async with httpx.AsyncClient(timeout=30, headers=HEADERS, follow_redirects=True) as client:
        for url in URLS:
            try:
                r = await client.get(url)
                content_type = r.headers.get("content-type", "")
                is_rss = "<rss" in r.text[:200] or "<feed" in r.text[:200]
                print(f"{url}")
                print(f"  status: {r.status_code}, type: {content_type[:50]}, is_rss: {is_rss}")
                if is_rss:
                    print(f"  ✅ RSS found! first 300: {r.text[:300]}")
                    break
            except Exception as e:
                print(f"  error: {e}")

asyncio.run(check())
