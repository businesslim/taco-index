from datetime import datetime, timedelta, timezone
from app.influencer.calculator import (
    calculate_influencer_index,
    calculate_asset_expert_indexes,
    calculate_weekly_ranks,
    score_to_band,
)


def _score(final_score: int, hours_ago: float) -> dict:
    return {
        "final_score": final_score,
        "posted_at": datetime.now(timezone.utc) - timedelta(hours=hours_ago),
    }


def test_recent_tweets_weighted_higher():
    scores = [
        _score(90, hours_ago=1),   # recent → high weight
        _score(10, hours_ago=71),  # old → low weight
    ]
    result = calculate_influencer_index(scores)
    assert result > 50


def test_empty_scores_returns_50():
    assert calculate_influencer_index([]) == 50


def test_older_than_72h_excluded():
    scores = [_score(100, hours_ago=73)]
    assert calculate_influencer_index(scores) == 50


def test_asset_expert_indexes_groups_by_domain():
    data = [
        {"domain": "crypto", "score": 80},
        {"domain": "crypto", "score": 60},
        {"domain": "stock", "score": 40},
    ]
    result = calculate_asset_expert_indexes(data)
    crypto = next(r for r in result if r["asset"] == "crypto")
    assert crypto["score"] == 70
    assert crypto["total_count"] == 2


def test_bull_bear_classification():
    data = [
        {"domain": "crypto", "score": 75},   # Bullish
        {"domain": "crypto", "score": 25},   # Bearish
        {"domain": "stock", "score": 50},    # Neutral
    ]
    result = calculate_asset_expert_indexes(data)
    crypto = next(r for r in result if r["asset"] == "crypto")
    assert crypto["bull_count"] == 1
    assert crypto["bear_count"] == 1
    assert crypto["neutral_count"] == 0


def test_weekly_ranks_top5_bull_and_bear():
    scores = [
        {"influencer_id": i, "handle": f"user{i}", "name": f"User{i}", "avg_score": i * 10}
        for i in range(1, 11)
    ]
    result = calculate_weekly_ranks(scores)
    assert len(result["top_bull"]) == 5
    assert len(result["top_bear"]) == 5
    assert result["top_bull"][0]["avg_score"] == 100
    assert result["top_bear"][0]["avg_score"] == 10


def test_score_to_band():
    assert score_to_band(10) == "Extreme Bearish"
    assert score_to_band(30) == "Bearish"
    assert score_to_band(50) == "Neutral"
    assert score_to_band(70) == "Bullish"
    assert score_to_band(90) == "Extreme Bullish"
