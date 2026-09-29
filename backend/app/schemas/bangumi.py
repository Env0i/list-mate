from __future__ import annotations
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class BangumiSearchResult(BaseModel):
    bangumi_id: int
    name: str
    name_cn: str
    summary: str
    image_url: Optional[str] = None
    type: int
    date: Optional[str] = None


class BangumiSearchResponse(BaseModel):
    results: list[BangumiSearchResult]
    total: int


class BangumiSubjectResponse(BaseModel):
    """条目详情（§3.1 扩展）：评分/收藏/标签/infobox/date + 缓存元数据。"""

    id: int
    name: str
    name_cn: str
    summary: str
    image_url: Optional[str] = None
    type: int
    total_episodes: Optional[int] = None
    date: Optional[str] = None
    rating: Optional[dict[str, Any]] = None       # {score, rank, total, count{1..10}}
    collection: Optional[dict[str, int]] = None   # {wish, doing, collect, on_hold, dropped}
    tags: Optional[list[dict[str, Any]]] = None   # [{name, count}]
    infobox: Optional[list[dict[str, Any]]] = None
    fetched_at: Optional[datetime] = None
    stale: bool = False
