from __future__ import annotations
from datetime import datetime
from sqlalchemy import Integer, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class BangumiCache(Base):
    """Bangumi 只读代理的响应缓存：key 形如 subject:400602、episodes:400602:0。"""

    __tablename__ = "bangumi_cache"

    key: Mapped[str] = mapped_column(String, primary_key=True)
    payload: Mapped[str] = mapped_column(String, nullable=False)  # JSON 串
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    status: Mapped[int] = mapped_column(Integer, default=200, nullable=False)
