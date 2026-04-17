import httpx
from datetime import datetime
from app.config import settings


class XApiFetcher:
    BASE_URL = "https://api.twitter.com/2"

    def __init__(self, bearer_token: str | None = None):
        self.bearer_token = bearer_token or settings.x_bearer_token
        self.headers = {"Authorization": f"Bearer {self.bearer_token}"}

    async def _get(self, path: str, params: dict) -> dict:
        url = f"{self.BASE_URL}{path}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, params=params, timeout=10)
        response.raise_for_status()
        return response.json()

    async def get_user_id(self, handle: str) -> str:
        data = await self._get(f"/users/by/username/{handle}", {})
        if "data" not in data:
            raise ValueError(f"User not found or API error for handle: {handle}")
        return data["data"]["id"]

    async def fetch_tweets(self, x_user_id: str, since_id: str | None) -> list[dict]:
        params: dict = {
            "max_results": 100,
            "tweet.fields": "created_at",
        }
        if since_id:
            params["since_id"] = since_id

        data = await self._get(f"/users/{x_user_id}/tweets", params)

        if "data" not in data:
            return []

        return [
            {
                "tweet_id": t["id"],
                "content": t["text"],
                "posted_at": datetime.fromisoformat(
                    t["created_at"].replace("Z", "+00:00")
                ),
            }
            for t in data["data"]
        ]
