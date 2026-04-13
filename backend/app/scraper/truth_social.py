import re
from datetime import datetime, timezone

TRUTH_SOCIAL_ACCOUNT_ID = "107780257626128497"
TRUTH_SOCIAL_API_URL = f"https://truthsocial.com/api/v1/accounts/{TRUTH_SOCIAL_ACCOUNT_ID}/statuses"


def _strip_html(html: str) -> str:
    text = re.sub(r"<br\s*/?>", "\n", html, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    return text.strip()


def parse_feed_entries(entries: list) -> list[dict]:
    """하위 호환성을 위해 유지 (테스트에서 사용)."""
    result = []
    from email.utils import parsedate_to_datetime
    for entry in entries:
        try:
            content = entry.get("summary") or entry.get("description") or entry.get("title") or ""
            tweet_id = entry.get("id") or entry.get("link") or ""
            pub_date = entry.get("published") or ""
            if not tweet_id:
                continue
            try:
                posted_at = parsedate_to_datetime(pub_date) if pub_date else datetime.now(timezone.utc)
            except Exception:
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


def parse_mastodon_statuses(statuses: list) -> list[dict]:
    result = []
    for status in statuses:
        try:
            tweet_id = status.get("id") or status.get("url") or ""
            if not tweet_id:
                continue
            content = _strip_html(status.get("content", ""))
            if not content:
                continue
            created_at = status.get("created_at", "")
            try:
                posted_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            except Exception:
                posted_at = datetime.now(timezone.utc)
            result.append({
                "source": "truth_social",
                "tweet_id": str(tweet_id),
                "content": content,
                "posted_at": posted_at,
                "raw_data": status,
            })
        except Exception:
            continue
    return result


async def fetch_truth_social_posts(limit: int = 20) -> list[dict]:
    """curl_cffi로 Chrome TLS 핑거프린트를 흉내내 Cloudflare를 우회한다."""
    from curl_cffi.requests import AsyncSession

    async with AsyncSession() as session:
        response = await session.get(
            TRUTH_SOCIAL_API_URL,
            params={"limit": limit},
            impersonate="chrome124",
            timeout=30,
        )
        response.raise_for_status()
    return parse_mastodon_statuses(response.json())
