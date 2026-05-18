from datetime import datetime
from pydantic import BaseModel
from typing import Optional

from .profile import ProfileResponse
from .tag import TagResponse


class WorkCreate(BaseModel):
    title: str
    category: str
    sub_category: str = ""
    progress_unit: str
    total: Optional[int] = None
    bangumi_id: Optional[int] = None
    cover_url: Optional[str] = None


class WorkUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    sub_category: Optional[str] = None
    progress_unit: Optional[str] = None
    total: Optional[int] = None
    bangumi_id: Optional[int] = None
    cover_url: Optional[str] = None
    cover_source: Optional[str] = None


class WorkListItem(BaseModel):
    id: int
    title: str
    category: str
    sub_category: str
    progress_unit: str
    total: Optional[int] = None
    cover_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WorkResponse(WorkListItem):
    bangumi_id: Optional[int] = None
    cover_source: str = "manual"
    profiles: list[ProfileResponse] = []
    tags: list[TagResponse] = []


class PaginatedWorks(BaseModel):
    items: list[WorkListItem]
    total: int
    page: int
    page_size: int
    total_pages: int
