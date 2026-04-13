import re
import asyncio
from datetime import datetime, timezone
from app.config import settings


def _strip_html(html: str) -> str:
    """HTML 태그를 제거하고 순수 텍스트를 반환한다."""
    text = re.sub(r"<br\s*/?>", "\n", html, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    return text.strip()


def parse_mastodon_statuses(statuses: list) -> list[dict]:
    """Truth Social 상태 목록을 표준화된 딕셔너리 리스트로 변환한다."""
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


def parse_feed_entries(entries: list) -> list[dict]:
    """feedparser 엔트리 목록을 파싱해 표준화된 딕셔너리 리스트로 반환한다.
    하위 호환성을 위해 유지 (테스트에서 사용).
    """
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


async def fetch_truth_social_posts(limit: int = 20) -> list[dict]:
    """truthbrush를 사용해 Truth Social 게시물을 가져온다."""
    from truthbrush.api import Api

    def _fetch() -> list:
        api = Api(
            username=settings.truthsocial_username,
            password=settings.truthsocial_password,
        )
        statuses = []
        for status in api.pull_statuses("realDonaldTrump", replies=False):
            statuses.append(status)
            if len(statuses) >= limit:
                break
        return statuses

    statuses = await asyncio.get_event_loop().run_in_executor(None, _fetch)
    return parse_mastodon_statuses(statuses)
