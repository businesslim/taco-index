from datetime import datetime, date
from pydantic import BaseModel
from typing import Optional


class InfluencerIndexOut(BaseModel):
    handle: str
    name: str
    category: str
    domain: str
    score: int
    band: str
    calculated_at: Optional[datetime]
    latest_tweet: Optional[str] = None

    model_config = {"from_attributes": True}


class AssetExpertIndexOut(BaseModel):
    asset: str
    score: int
    band: str
    bull_count: int
    bear_count: int
    neutral_count: int
    total_count: int
    calculated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class WeeklyRankEntry(BaseModel):
    handle: str
    name: str
    avg_score: int
    rank_bull: Optional[int]
    rank_bear: Optional[int]


class BullBearRatio(BaseModel):
    bull_count: int
    bear_count: int
    neutral_count: int
    total_count: int


class InfluencerSummaryOut(BaseModel):
    asset_indexes: list[AssetExpertIndexOut]
    bull_bear_ratio: BullBearRatio
    weekly_top_bull: list[WeeklyRankEntry]
    weekly_top_bear: list[WeeklyRankEntry]


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
