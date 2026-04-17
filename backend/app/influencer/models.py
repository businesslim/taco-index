from datetime import datetime, date
from typing import Optional
from sqlalchemy import String, Text, Integer, Boolean, ForeignKey, DateTime, Date, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Influencer(Base):
    __tablename__ = "influencers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    handle: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # "Investor" | "CEO" | "BigTech" | "Economist" | "Institution"
    domain: Mapped[str] = mapped_column(String(50), nullable=False)  # "crypto" | "stock" | "macro" | "gold"
    x_user_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    last_fetched_tweet_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    tweets: Mapped[list["InfluencerTweet"]] = relationship(
        "InfluencerTweet", back_populates="influencer", cascade="all, delete-orphan"
    )
    index: Mapped[Optional["InfluencerIndex"]] = relationship(
        "InfluencerIndex", back_populates="influencer", uselist=False, cascade="all, delete-orphan"
    )
    weekly_ranks: Mapped[list["WeeklyInfluencerRank"]] = relationship(
        "WeeklyInfluencerRank", back_populates="influencer", cascade="all, delete-orphan"
    )


class InfluencerTweet(Base):
    __tablename__ = "influencer_tweets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    influencer_id: Mapped[int] = mapped_column(Integer, ForeignKey("influencers.id", ondelete="CASCADE"), nullable=False)
    tweet_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    posted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    influencer: Mapped["Influencer"] = relationship("Influencer", back_populates="tweets")
    score: Mapped[Optional["InfluencerTweetScore"]] = relationship(
        "InfluencerTweetScore", back_populates="tweet", uselist=False, cascade="all, delete-orphan"
    )


class InfluencerTweetScore(Base):
    __tablename__ = "influencer_tweet_scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tweet_id: Mapped[str] = mapped_column(String(255), ForeignKey("influencer_tweets.tweet_id", ondelete="CASCADE"), unique=True, nullable=False)
    llm_score: Mapped[int] = mapped_column(Integer, nullable=False)
    keyword_score: Mapped[int] = mapped_column(Integer, nullable=False)
    final_score: Mapped[int] = mapped_column(Integer, nullable=False)
    domain: Mapped[str] = mapped_column(String(50), nullable=False)
    reasoning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    tweet: Mapped["InfluencerTweet"] = relationship("InfluencerTweet", back_populates="score")


class InfluencerIndex(Base):
    __tablename__ = "influencer_indexes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    influencer_id: Mapped[int] = mapped_column(Integer, ForeignKey("influencers.id", ondelete="CASCADE"), unique=True, nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False, default=50, server_default="50")
    band: Mapped[str] = mapped_column(String(50), nullable=False, default="Neutral", server_default="Neutral")
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    influencer: Mapped["Influencer"] = relationship("Influencer", back_populates="index")


class AssetExpertIndex(Base):
    __tablename__ = "asset_expert_indexes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    asset: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)  # "crypto" | "stock" | "gold" | "macro"
    score: Mapped[int] = mapped_column(Integer, nullable=False, default=50, server_default="50")
    bull_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    bear_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    neutral_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    total_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class WeeklyInfluencerRank(Base):
    __tablename__ = "weekly_influencer_ranks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    week_start: Mapped[date] = mapped_column(Date, nullable=False)
    influencer_id: Mapped[int] = mapped_column(Integer, ForeignKey("influencers.id", ondelete="CASCADE"), nullable=False)
    avg_score: Mapped[int] = mapped_column(Integer, nullable=False)
    rank_bull: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    rank_bear: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    influencer: Mapped["Influencer"] = relationship("Influencer", back_populates="weekly_ranks")
