from datetime import datetime
from pydantic import BaseModel


class InfluencerIndexOut(BaseModel):
    handle: str
    name: str
    category: str
    domain: str
    score: int
    band: str
    calculated_at: datetime | None = None
    latest_tweet: str | None = None
    latest_tweet_id: str | None = None
    latest_tweet_posted_at: datetime | None = None
    post_count_72h: int = 0
    profile_image_url: str | None = None

    model_config = {"from_attributes": True}


class AssetExpertIndexOut(BaseModel):
    asset: str
    score: int
    band: str
    bull_count: int
    bear_count: int
    neutral_count: int
    total_count: int
    calculated_at: datetime | None = None

    model_config = {"from_attributes": True}


class WeeklyRankEntry(BaseModel):
    handle: str
    name: str
    avg_score: int
    rank_bull: int | None = None
    rank_bear: int | None = None
    profile_image_url: str | None = None


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
