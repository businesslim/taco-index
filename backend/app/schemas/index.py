from pydantic import BaseModel
from datetime import datetime

class BandSchema(BaseModel):
    label: str
    min_score: int
    max_score: int
    color: str
    description: str
    model_config = {"from_attributes": True}

class CurrentIndexResponse(BaseModel):
    index_value: int
    band_label: str
    band_color: str
    tweet_count: int
    calculated_at: datetime | None
    last_post_at: datetime | None = None

class IndexHistoryPoint(BaseModel):
    index_value: int
    band_label: str
    calculated_at: datetime

class IndexHistoryResponse(BaseModel):
    data: list[IndexHistoryPoint]
