from datetime import datetime
from sqlalchemy import Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base


class TimelineEntry(Base):
    __tablename__ = "timeline_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    work_id: Mapped[int] = mapped_column(Integer, ForeignKey("works.id"), nullable=False)
    game_profile_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("game_profiles.id"), nullable=True)
    action_type: Mapped[str] = mapped_column(String, nullable=False)
    old_value: Mapped[str | None] = mapped_column(String, nullable=True)
    new_value: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    work = relationship("Work")
    game_profile = relationship("GameProfile")
