import uuid
from datetime import datetime
from sqlalchemy import String, Text, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Tweet(Base):
    __tablename__ = "tweets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source: Mapped[str] = mapped_column(String(50))   # 'truth_social' | 'x'
    tweet_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    content: Mapped[str] = mapped_column(Text)
    posted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    raw_data: Mapped[dict] = mapped_column(JSONB)

    score: Mapped["TweetScore"] = relationship("TweetScore", back_populates="tweet", uselist=False)


class TweetScore(Base):
    __tablename__ = "tweet_scores"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tweet_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tweets.id"))
    llm_score: Mapped[int] = mapped_column(Integer)
    keyword_score: Mapped[int] = mapped_column(Integer)
    final_score: Mapped[int] = mapped_column(Integer)
    llm_reasoning: Mapped[str] = mapped_column(Text)
    analyzed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    tweet: Mapped["Tweet"] = relationship("Tweet", back_populates="score")
