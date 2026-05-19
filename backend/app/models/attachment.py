from datetime import datetime
from sqlalchemy import Integer, String, DateTime, ForeignKey, LargeBinary, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base


class Attachment(Base):
    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    game_profile_id: Mapped[int] = mapped_column(Integer, ForeignKey("game_profiles.id"), nullable=False)
    label: Mapped[str] = mapped_column(String, default="")
    file_name: Mapped[str] = mapped_column(String, nullable=False)
    file_type: Mapped[str] = mapped_column(String, nullable=False)
    file_data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    game_profile = relationship("GameProfile", back_populates="attachments")
