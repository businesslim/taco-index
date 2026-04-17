from collections import defaultdict
from datetime import datetime, timedelta, timezone

WINDOW_HOURS = 72


def _time_weight(posted_at: datetime) -> float:
    now = datetime.now(timezone.utc)
    hours_ago = (now - posted_at).total_seconds() / 3600
    if hours_ago >= WINDOW_HOURS:
        return 0.0
    return (WINDOW_HOURS - hours_ago) / WINDOW_HOURS


def score_to_band(score: int) -> str:
    if score <= 20:
        return "Extreme Bearish"
    elif score <= 40:
        return "Bearish"
    elif score <= 60:
        return "Neutral"
    elif score <= 80:
        return "Bullish"
    else:
        return "Extreme Bullish"


def calculate_influencer_index(scores: list[dict]) -> int:
    weighted_sum = 0.0
    weight_total = 0.0
    for s in scores:
        w = _time_weight(s["posted_at"])
        if w <= 0:
            continue
        weighted_sum += s["final_score"] * w
        weight_total += w
    if weight_total == 0:
        return 50
    return round(weighted_sum / weight_total)


def calculate_asset_expert_indexes(influencer_scores: list[dict]) -> list[dict]:
    groups: dict[str, list[int]] = defaultdict(list)
    for item in influencer_scores:
        groups[item["domain"]].append(item["score"])

    result = []
    for asset in ["crypto", "stock", "gold", "macro"]:
        asset_scores = groups.get(asset, [])
        if not asset_scores:
            continue
        avg = round(sum(asset_scores) / len(asset_scores))
        bull = sum(1 for s in asset_scores if s > 60)
        bear = sum(1 for s in asset_scores if s < 40)
        neutral = len(asset_scores) - bull - bear
        result.append({
            "asset": asset,
            "score": avg,
            "band": score_to_band(avg),
            "bull_count": bull,
            "bear_count": bear,
            "neutral_count": neutral,
            "total_count": len(asset_scores),
        })
    return result


def calculate_weekly_ranks(weekly_scores: list[dict]) -> dict:
    sorted_desc = sorted(weekly_scores, key=lambda x: x["avg_score"], reverse=True)
    sorted_asc = sorted(weekly_scores, key=lambda x: x["avg_score"])
    return {
        "top_bull": sorted_desc[:5],
        "top_bear": sorted_asc[:5],
    }
