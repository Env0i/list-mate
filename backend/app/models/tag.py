from datetime import datetime
from sqlalchemy import Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    color: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    work_tags = relationship("WorkTag", back_populates="tag", cascade="all, delete-orphan")


class WorkTag(Base):
    __tablename__ = "work_tags"

    work_id: Mapped[int] = mapped_column(Integer, ForeignKey("works.id"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(Integer, ForeignKey("tags.id"), primary_key=True)

    work = relationship("Work", back_populates="work_tags")
    tag = relationship("Tag", back_populates="work_tags")
