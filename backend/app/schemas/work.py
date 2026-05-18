from datetime import datetime
from pydantic import BaseModel
from typing import Optional

from .game_profile import GameProfileResponse
from .tag import TagResponse


class WorkCreate(BaseModel):
    title: str
    category: str
    sub_category: str = ""
    progress_unit: str
    total: Optional[int] = None
    progress_value: Optional[float] = None
    status: Optional[str] = None
    rating: Optional[int] = None
    review: Optional[str] = None
    bangumi_id: Optional[int] = None
    cover_url: Optional[str] = None
    summary: Optional[str] = None
    start_date: Optional[str] = None
    finish_date: Optional[str] = None
    platform: Optional[str] = None
    purchase_platform: Optional[str] = None
    purchase_date: Optional[str] = None
    purchase_price: Optional[float] = None
    playtime_hours: Optional[float] = None
    replay_count: Optional[int] = None
    priority: Optional[int] = None
    external_links: Optional[str] = None
    bangumi_data: Optional[str] = None
    tag_ids: list[int] = []


class WorkUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    sub_category: Optional[str] = None
    progress_unit: Optional[str] = None
    total: Optional[int] = None
    progress_value: Optional[float] = None
    status: Optional[str] = None
    rating: Optional[int] = None
    review: Optional[str] = None
    bangumi_id: Optional[int] = None
    cover_url: Optional[str] = None
    cover_source: Optional[str] = None
    summary: Optional[str] = None
    start_date: Optional[str] = None
    finish_date: Optional[str] = None
    platform: Optional[str] = None
    purchase_platform: Optional[str] = None
    purchase_date: Optional[str] = None
    purchase_price: Optional[float] = None
    playtime_hours: Optional[float] = None
    replay_count: Optional[int] = None
    priority: Optional[int] = None
    external_links: Optional[str] = None
    tag_ids: Optional[list[int]] = None


class WorkListItem(BaseModel):
    id: int
    title: str
    category: str
    sub_category: str
    progress_unit: str
    total: Optional[int] = None
    progress_value: Optional[float] = None
    status: Optional[str] = None
    rating: Optional[int] = None
    auto_completed: bool = False
    cover_url: Optional[str] = None
    summary: Optional[str] = None
    start_date: Optional[str] = None
    finish_date: Optional[str] = None
    platform: Optional[str] = None
    purchase_platform: Optional[str] = None
    purchase_price: Optional[float] = None
    playtime_hours: Optional[float] = None
    replay_count: Optional[int] = None
    priority: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    tag_ids: list[int] = []

    model_config = {"from_attributes": True}


class WorkResponse(WorkListItem):
    bangumi_id: Optional[int] = None
    cover_source: str = "manual"
    review: Optional[str] = None
    purchase_date: Optional[str] = None
    external_links: Optional[str] = None
    bangumi_data: Optional[str] = None
    game_profiles: list[GameProfileResponse] = []
    tags: list[TagResponse] = []


class PaginatedWorks(BaseModel):
    items: list[WorkListItem]
    total: int
    page: int
    page_size: int
    total_pages: int
