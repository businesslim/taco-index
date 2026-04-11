import feedparser
import httpx
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

TRUTH_SOCIAL_RSS_URL = "https://truthsocial.com/@realDonaldTrump.rss"

def parse_feed_entries(entries: list) -> list[dict]:
    """feedparser 엔트리 목록을 파싱해 표준화된 딕셔너리 리스트로 반환한다."""
    result = []
    for entry in entries:
        try:
            content = entry.get("summary") or entry.get("description") or entry.get("title") or ""
            tweet_id = entry.get("id") or entry.get("link") or ""
            pub_date = entry.get("published") or ""

            if not tweet_id:
                continue

            if pub_date:
                try:
                    posted_at = parsedate_to_datetime(pub_date)
                except Exception:
                    posted_at = datetime.now(timezone.utc)
            else:
                posted_at = datetime.now(timezone.utc)

            result.append({
                "source": "truth_social",
                "tweet_id": tweet_id,
                "content": content,
                "posted_at": posted_at,
                "raw_data": dict(entry),
            })
        except Exception:
            continue
    return result


async def fetch_truth_social_posts() -> list[dict]:
    """Truth Social RSS를 가져와 파싱된 게시물 목록을 반환한다."""
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(TRUTH_SOCIAL_RSS_URL)
        response.raise_for_status()
    feed = feedparser.parse(response.text)
    return parse_feed_entries(feed.entries)
