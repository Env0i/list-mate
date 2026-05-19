from __future__ import annotations
from typing import Optional
import enum
from datetime import datetime
from sqlalchemy import Integer, String, Float, Enum, DateTime, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base


class Category(str, enum.Enum):
    ANIME = "anime"
    NOVEL = "novel"
    COMIC = "comic"
    GAME = "game"


class ProgressUnit(str, enum.Enum):
    EP = "ep"
    CHAPTER = "chapter"
    VOLUME = "volume"
    PAGE = "page"
    PERCENT = "percent"


class WorkStatus(str, enum.Enum):
    WISH = "wish"
    WATCHING = "watching"
    COMPLETED = "completed"
    PAUSED = "paused"
    DROPPED = "dropped"


class CoverSource(str, enum.Enum):
    BANGUMI = "bangumi"
    MANUAL = "manual"
    OTHER = "other"


class Work(Base):
    __tablename__ = "works"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[Category] = mapped_column(Enum(Category), nullable=False)
    sub_category: Mapped[str] = mapped_column(String, default="", nullable=False)
    progress_unit: Mapped[ProgressUnit] = mapped_column(Enum(ProgressUnit), nullable=False)
    total: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # 动漫/小说/漫画的直接进度字段
    progress_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    status: Mapped[Optional[WorkStatus]] = mapped_column(Enum(WorkStatus), nullable=True)
    rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    review: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    auto_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_free: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    bangumi_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    cover_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    cover_data: Mapped[Optional[bytes]] = mapped_column(nullable=True)
    cover_source: Mapped[CoverSource] = mapped_column(
        Enum(CoverSource), default=CoverSource.MANUAL, nullable=False
    )
    summary: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    start_date: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    finish_date: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    platform: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    purchase_platform: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    purchase_date: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    purchase_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    playtime_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    replay_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    priority: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    external_links: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    bangumi_data: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    game_profiles = relationship("GameProfile", back_populates="work", cascade="all, delete-orphan")
    work_tags = relationship("WorkTag", back_populates="work", cascade="all, delete-orphan")
