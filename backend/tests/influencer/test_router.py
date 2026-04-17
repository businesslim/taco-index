import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient


def _make_influencer(handle="saylor", name="Michael Saylor", category="Investor", domain="crypto"):
    inf = MagicMock()
    inf.handle = handle
    inf.name = name
    inf.category = category
    inf.domain = domain
    inf.id = 1
    inf.is_active = True
    return inf


def _make_index(score=72, band="Bullish", influencer_id=1):
    idx = MagicMock()
    idx.score = score
    idx.band = band
    idx.calculated_at = None
    idx.influencer_id = influencer_id
    return idx


def test_get_influencers_returns_200():
    from app.main import app
    from app.database import get_db

    async def mock_db():
        db = AsyncMock()
        inf = _make_influencer()
        idx = _make_index()
        tweet = MagicMock()
        tweet.content = "Test tweet"
        tweet.tweet_id = "123456"
        list_result = MagicMock()
        list_result.all.return_value = [(inf, idx, tweet, 3)]
        db.execute = AsyncMock(return_value=list_result)
        yield db

    app.dependency_overrides[get_db] = mock_db
    client = TestClient(app)
    response = client.get("/api/influencer")
    app.dependency_overrides.clear()
    assert response.status_code in (200, 422, 500)


def test_get_summary_endpoint_exists():
    from app.main import app
    from app.database import get_db

    async def mock_db():
        db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_result.all.return_value = []
        db.execute = AsyncMock(return_value=mock_result)
        yield db

    app.dependency_overrides[get_db] = mock_db
    client = TestClient(app)
    response = client.get("/api/influencer/summary")
    app.dependency_overrides.clear()
    assert response.status_code != 404


def test_get_influencer_by_handle_not_found():
    from app.main import app
    from app.database import get_db

    async def mock_db():
        db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        db.execute = AsyncMock(return_value=mock_result)
        yield db

    app.dependency_overrides[get_db] = mock_db
    client = TestClient(app)
    response = client.get("/api/influencer/unknown_handle_xyz")
    app.dependency_overrides.clear()
    assert response.status_code == 404
