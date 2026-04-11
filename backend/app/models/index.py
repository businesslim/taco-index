import uuid
from datetime import datetime
from sqlalchemy import String, Text, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class TacoIndexHistory(Base):
    __tablename__ = "taco_index_history"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    index_value: Mapped[int] = mapped_column(Integer)   # 0~100
    band_label: Mapped[str] = mapped_column(String(50))
    tweet_count: Mapped[int] = mapped_column(Integer)
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


class IndexBand(Base):
    __tablename__ = "index_bands"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    label: Mapped[str] = mapped_column(String(50), unique=True)
    min_score: Mapped[int] = mapped_column(Integer)
    max_score: Mapped[int] = mapped_column(Integer)
    color: Mapped[str] = mapped_column(String(7))       # HEX e.g. "#FF4444"
    description: Mapped[str] = mapped_column(Text)
