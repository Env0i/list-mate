import enum
from datetime import datetime
from sqlalchemy import Integer, String, Float, Enum, DateTime, Boolean, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base


class GameStatus(str, enum.Enum):
    WISH = "wish"
    PLAYING = "playing"
    COMPLETED = "completed"
    DROPPED = "dropped"
    WAIT_BUY = "wait_buy"
    WAIT_SALE = "wait_sale"


class GameProfile(Base):
    __tablename__ = "game_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    work_id: Mapped[int] = mapped_column(Integer, ForeignKey("works.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, default="本体", nullable=False)
    progress_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[GameStatus] = mapped_column(
        Enum(GameStatus), default=GameStatus.WISH, nullable=False
    )
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    review: Mapped[str | None] = mapped_column(String, nullable=True)
    auto_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    work = relationship("Work", back_populates="game_profiles")
