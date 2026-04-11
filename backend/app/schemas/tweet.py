from pydantic import BaseModel
from datetime import datetime

class TweetWithScore(BaseModel):
    tweet_id: str
    source: str
    content: str
    posted_at: datetime
    final_score: int
    band_label: str
    band_color: str
    llm_reasoning: str

class RecentTweetsResponse(BaseModel):
    data: list[TweetWithScore]
