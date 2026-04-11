import pytest
from app.analyzer.keywords import compute_keyword_score, BULLISH_KEYWORDS, BEARISH_KEYWORDS

def test_bullish_keywords_return_high_score():
    text = "Bitcoin to the moon! Great crypto deal for America. Win win win."
    score = compute_keyword_score(text)
    assert score > 60

def test_bearish_keywords_return_low_score():
    text = "New tariffs on China. Sanctions on crypto exchanges. Ban on digital assets starting now."
    score = compute_keyword_score(text)
    assert score < 40

def test_neutral_text_returns_near_50():
    text = "I had a meeting today. Will announce something tomorrow."
    score = compute_keyword_score(text)
    assert 35 <= score <= 65

def test_score_clamps_to_0_100():
    text = " ".join(["tariff", "ban", "sanction", "war", "fake", "crash"] * 10)
    score = compute_keyword_score(text)
    assert 0 <= score <= 100

def test_empty_text_returns_50():
    score = compute_keyword_score("")
    assert score == 50

def test_bullish_keywords_list_not_empty():
    assert len(BULLISH_KEYWORDS) > 5

def test_bearish_keywords_list_not_empty():
    assert len(BEARISH_KEYWORDS) > 5
