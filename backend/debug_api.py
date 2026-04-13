import asyncio
import httpx

# Truth Social is Mastodon-based — public API endpoints
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "application/json",
}

async def check():
    async with httpx.AsyncClient(timeout=30, headers=HEADERS, follow_redirects=True) as client:

        # 1. Search for Trump's account ID via Mastodon API
        print("=== Searching account ===")
        r = await client.get("https://truthsocial.com/api/v1/accounts/lookup?acct=realDonaldTrump")
        print(f"status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            account_id = data.get("id")
            username = data.get("username")
            print(f"account_id: {account_id}, username: {username}")

            # 2. Get statuses
            print("\n=== Fetching statuses ===")
            r2 = await client.get(f"https://truthsocial.com/api/v1/accounts/{account_id}/statuses?limit=5")
            print(f"status: {r2.status_code}")
            if r2.status_code == 200:
                statuses = r2.json()
                print(f"posts found: {len(statuses)}")
                for s in statuses[:2]:
                    import re
                    content = re.sub('<[^>]+>', '', s.get('content', ''))[:100]
                    print(f"  [{s.get('created_at','')}] {content}")
        else:
            print(r.text[:200])

asyncio.run(check())
