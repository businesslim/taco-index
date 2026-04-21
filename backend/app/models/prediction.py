import uuid
import enum
from datetime import datetime
from sqlalchemy import String, DateTime, Float, Enum, ForeignKey, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class AssetEnum(str, enum.Enum):
    BTC = "BTC"
    SPX = "SPX"
    GOLD = "GOLD"


class TimeframeEnum(str, enum.Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"


class DirectionEnum(str, enum.Enum):
    bullish = "bullish"
    bearish = "bearish"


class ResultEnum(str, enum.Enum):
    correct = "correct"
    incorrect = "incorrect"
    pending = "pending"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str | None] = mapped_column(String(255))
    image: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    prediction_count: Mapped[int] = mapped_column(Integer, default=0)
    correct_count: Mapped[int] = mapped_column(Integer, default=0)

    predictions: Mapped[list["Prediction"]] = relationship("Prediction", back_populates="user")


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    asset: Mapped[AssetEnum] = mapped_column(Enum(AssetEnum))
    timeframe: Mapped[TimeframeEnum] = mapped_column(Enum(TimeframeEnum))
    direction: Mapped[DirectionEnum] = mapped_column(Enum(DirectionEnum))
    price_at_prediction: Mapped[float] = mapped_column(Float)
    predicted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    evaluates_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    result: Mapped[ResultEnum] = mapped_column(Enum(ResultEnum), default=ResultEnum.pending)
    evaluated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="predictions")
