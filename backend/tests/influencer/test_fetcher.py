from unittest.mock import patch, MagicMock
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


def test_fetch_tweets_returns_list():
    fetcher = XApiFetcher(bearer_token="test_token")
    with patch.object(fetcher, "_get", return_value=MOCK_TWEET_RESPONSE):
        tweets = fetcher.fetch_tweets(x_user_id="12345", since_id=None)
    assert len(tweets) == 2
    assert tweets[0]["tweet_id"] == "123456"
    assert tweets[0]["content"] == "Bitcoin is going to the moon!"
    assert isinstance(tweets[0]["posted_at"], datetime)


def test_fetch_tweets_with_since_id_passes_param():
    fetcher = XApiFetcher(bearer_token="test_token")
    with patch.object(fetcher, "_get", return_value={"meta": {}}) as mock_get:
        fetcher.fetch_tweets(x_user_id="12345", since_id="999")
    params = mock_get.call_args[0][1]
    assert params.get("since_id") == "999"


def test_fetch_tweets_empty_response_returns_empty_list():
    fetcher = XApiFetcher(bearer_token="test_token")
    with patch.object(fetcher, "_get", return_value={"meta": {}}):
        tweets = fetcher.fetch_tweets(x_user_id="12345", since_id=None)
    assert tweets == []


def test_fetch_tweets_api_error_raises():
    fetcher = XApiFetcher(bearer_token="test_token")
    with patch.object(fetcher, "_get", side_effect=Exception("403 Forbidden")):
        try:
            fetcher.fetch_tweets(x_user_id="12345", since_id=None)
            assert False, "Should have raised"
        except Exception as e:
            assert "403" in str(e)


def test_get_user_id_by_handle():
    fetcher = XApiFetcher(bearer_token="test_token")
    mock_resp = {"data": {"id": "2244994945", "username": "saylor"}}
    with patch.object(fetcher, "_get", return_value=mock_resp):
        user_id = fetcher.get_user_id("saylor")
    assert user_id == "2244994945"


def test_fetch_tweets_no_since_id_omits_param():
    fetcher = XApiFetcher(bearer_token="test_token")
    with patch.object(fetcher, "_get", return_value={"meta": {}}) as mock_get:
        fetcher.fetch_tweets(x_user_id="12345", since_id=None)
    params = mock_get.call_args[0][1]
    assert "since_id" not in params
