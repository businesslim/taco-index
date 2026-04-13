import re
import feedparser
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

TRUMPSTRUTH_FEED_URL = "https://www.trumpstruth.org/feed"
TRUTH_ORIGINAL_ID_TAG = "truth_originalid"


def _strip_html(html: str) -> str:
    text = re.sub(r"<br\s*/?>", "\n", html, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    return text.strip()


def parse_feed_entries(entries: list) -> list[dict]:
    """하위 호환성을 위해 유지 (테스트에서 사용)."""
    result = []
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
    """Truth Social Mastodon API 응답을 표준화된 딕셔너리 리스트로 변환한다."""
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
    """trumpstruth.org RSS 피드로 Truth Social 포스트를 가져온다."""
    feed = feedparser.parse(TRUMPSTRUTH_FEED_URL)

    result = []
    for entry in feed.entries[:limit]:
        try:
            # truth:originalId 태그에서 Truth Social 원본 ID 추출
            tweet_id = getattr(entry, TRUTH_ORIGINAL_ID_TAG, None) or entry.get("guid", "")
            if not tweet_id:
                continue

            content = _strip_html(entry.get("summary") or entry.get("title") or "")
            if not content:
                continue

            pub_date = entry.get("published", "")
            try:
                posted_at = parsedate_to_datetime(pub_date) if pub_date else datetime.now(timezone.utc)
            except Exception:
                posted_at = datetime.now(timezone.utc)

            result.append({
                "source": "truth_social",
                "tweet_id": str(tweet_id),
                "content": content,
                "posted_at": posted_at,
                "raw_data": dict(entry),
            })
        except Exception:
            continue

    return result
