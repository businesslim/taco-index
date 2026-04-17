import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timezone
from app.influencer.fetcher import XApiFetcher


MOCK_TWEET_RESPONSE = {
    "data": [
        {
            "id": "123456",
            "text": "Bitcoin is going to the moon!",
            "created_at": "2026-04-17T10:00:00.000Z",
        },
        {
            "id": "123455",
            "text": "Markets looking strong today.",
            "created_at": "2026-04-17T09:00:00.000Z",
        },
    ],
    "meta": {"newest_id": "123456", "oldest_id": "123455"},
}


@pytest.mark.asyncio
async def test_fetch_tweets_returns_list():
    fetcher = XApiFetcher(bearer_token="test_token")
    with patch.object(fetcher, "_get", new=AsyncMock(return_value=MOCK_TWEET_RESPONSE)):
        tweets = await fetcher.fetch_tweets(x_user_id="12345", since_id=None)
    assert len(tweets) == 2
    assert tweets[0]["tweet_id"] == "123456"
    assert tweets[0]["content"] == "Bitcoin is going to the moon!"
    assert isinstance(tweets[0]["posted_at"], datetime)


@pytest.mark.asyncio
async def test_fetch_tweets_with_since_id_passes_param():
    fetcher = XApiFetcher(bearer_token="test_token")
    mock_get = AsyncMock(return_value={"meta": {}})
    with patch.object(fetcher, "_get", new=mock_get):
        await fetcher.fetch_tweets(x_user_id="12345", since_id="999")
    params = mock_get.call_args[0][1]
    assert params.get("since_id") == "999"


@pytest.mark.asyncio
async def test_fetch_tweets_empty_response_returns_empty_list():
    fetcher = XApiFetcher(bearer_token="test_token")
    with patch.object(fetcher, "_get", new=AsyncMock(return_value={"meta": {}})):
        tweets = await fetcher.fetch_tweets(x_user_id="12345", since_id=None)
    assert tweets == []


@pytest.mark.asyncio
async def test_fetch_tweets_api_error_raises():
    fetcher = XApiFetcher(bearer_token="test_token")
    mock_get = AsyncMock(side_effect=Exception("403 Forbidden"))
    with patch.object(fetcher, "_get", new=mock_get):
        with pytest.raises(Exception, match="403"):
            await fetcher.fetch_tweets(x_user_id="12345", since_id=None)


@pytest.mark.asyncio
async def test_get_user_id_by_handle():
    fetcher = XApiFetcher(bearer_token="test_token")
    mock_resp = {"data": {"id": "2244994945", "username": "saylor"}}
    mock_get = AsyncMock(return_value=mock_resp)
    with patch.object(fetcher, "_get", new=mock_get):
        user_id = await fetcher.get_user_id("saylor")
    assert user_id == "2244994945"


@pytest.mark.asyncio
async def test_fetch_tweets_no_since_id_omits_param():
    fetcher = XApiFetcher(bearer_token="test_token")
    mock_get = AsyncMock(return_value={"meta": {}})
    with patch.object(fetcher, "_get", new=mock_get):
        await fetcher.fetch_tweets(x_user_id="12345", since_id=None)
    params = mock_get.call_args[0][1]
    assert "since_id" not in params
