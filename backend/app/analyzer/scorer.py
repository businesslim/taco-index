import math
from datetime import datetime, timezone
from typing import TypedDict

LLM_WEIGHT = 0.7
KEYWORD_WEIGHT = 0.3

HALF_LIFE_HOURS = 12.0  # 12시간마다 가중치가 절반으로 감소

BANDS = [
    (0,  20,  "Taco de Habanero"),
    (21, 40,  "Taco de Chorizo"),
    (41, 60,  "Cooking..."),
    (61, 80,  "Taco de Frijoles"),
    (81, 100, "Taco de CHICKEN"),
]

class ScoredTweet(TypedDict):
    final_score: int
    posted_at: datetime


def compute_final_score(llm_score: int, keyword_score: int) -> int:
    """LLM(70%)과 키워드(30%) 점수를 합산해 0~100으로 반환."""
    raw = llm_score * LLM_WEIGHT + keyword_score * KEYWORD_WEIGHT
    return max(0, min(100, round(raw)))


def compute_taco_index(tweets: list[ScoredTweet]) -> int:
    """최근 72시간 트윗들의 지수 감쇠 가중 평균으로 TACO Index(0~100)를 계산한다.
    최신 트윗일수록 가중치가 높다 (지수 감쇠, half-life=12h).
    """
    if not tweets:
        return 50

    now = datetime.now(timezone.utc)

    total_weight = 0.0
    weighted_sum = 0.0

    for tweet in tweets:
        posted_at = tweet["posted_at"]
        if posted_at.tzinfo is None:
            posted_at = posted_at.replace(tzinfo=timezone.utc)
        hours_ago = (now - posted_at).total_seconds() / 3600
        weight = math.exp(-hours_ago / HALF_LIFE_HOURS)
        weighted_sum += tweet["final_score"] * weight
        total_weight += weight

    if total_weight == 0:
        return 50

    return max(0, min(100, round(weighted_sum / total_weight)))


def get_band_label(score: int) -> str:
    """점수에 해당하는 밴드 레이블을 반환한다."""
    for min_s, max_s, label in BANDS:
        if min_s <= score <= max_s:
            return label
    return "Neutral"
