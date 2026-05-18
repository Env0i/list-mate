import enum
from datetime import datetime
from sqlalchemy import Integer, String, Enum, DateTime, func
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
    total: Mapped[int | None] = mapped_column(Integer, nullable=True)
    bangumi_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cover_url: Mapped[str | None] = mapped_column(String, nullable=True)
    cover_data: Mapped[bytes | None] = mapped_column(nullable=True)
    cover_source: Mapped[CoverSource] = mapped_column(
        Enum(CoverSource), default=CoverSource.MANUAL, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    profiles = relationship("Profile", back_populates="work", cascade="all, delete-orphan")
    work_tags = relationship("WorkTag", back_populates="work", cascade="all, delete-orphan")
