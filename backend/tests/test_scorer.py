import pytest
from datetime import datetime, timedelta, timezone
from app.analyzer.scorer import compute_final_score, compute_taco_index, get_band_label

def test_final_score_weights():
    # LLM 0.85, keyword 0.15
    score = compute_final_score(llm_score=80, keyword_score=40)
    assert score == 74  # round(80*0.85 + 40*0.15) = round(68+6) = 74

def test_final_score_clamps_high():
    assert compute_final_score(110, 110) == 100

def test_final_score_clamps_low():
    assert compute_final_score(-10, -10) == 0

def test_taco_index_recent_tweet_dominates():
    now = datetime.now(timezone.utc)
    tweets = [
        {"final_score": 90, "posted_at": now - timedelta(hours=1)},
        {"final_score": 10, "posted_at": now - timedelta(hours=71)},
    ]
    index = compute_taco_index(tweets)
    assert index > 60  # 최신 bullish 트윗이 지배

def test_taco_index_empty_returns_50():
    assert compute_taco_index([]) == 50

def test_taco_index_single_tweet():
    now = datetime.now(timezone.utc)
    tweets = [{"final_score": 75, "posted_at": now - timedelta(hours=5)}]
    index = compute_taco_index(tweets)
    assert 60 <= index <= 90

def test_get_band_label_extreme_bearish():
    assert get_band_label(10) == "Taco de Habanero"

def test_get_band_label_bearish():
    assert get_band_label(30) == "Taco de Chorizo"

def test_get_band_label_neutral():
    assert get_band_label(50) == "Cooking..."

def test_get_band_label_bullish():
    assert get_band_label(70) == "Taco de Frijoles"

def test_get_band_label_extreme_bullish():
    assert get_band_label(90) == "Taco de CHICKEN"
