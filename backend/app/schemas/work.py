from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, field_validator, Field
from typing import Optional

from ..models.work import Category, CoverSource, ProgressUnit, WorkStatus
from ..models.game_profile import GameStatus
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
    rating: Optional[int] = Field(None, ge=0, le=10)
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
    is_free: bool = False

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        valid = {e.value for e in Category}
        if v not in valid:
            raise ValueError(f"无效分类 '{v}'，可选: {', '.join(sorted(valid))}")
        return v

    @field_validator("progress_unit")
    @classmethod
    def validate_progress_unit(cls, v: str) -> str:
        valid = {e.value for e in ProgressUnit}
        if v not in valid:
            raise ValueError(f"无效进度单位 '{v}'，可选: {', '.join(sorted(valid))}")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        valid = {e.value for e in WorkStatus} | {e.value for e in GameStatus}
        if v not in valid:
            raise ValueError(f"无效状态 '{v}'，可选: {', '.join(sorted(valid))}")
        return v


class WorkUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    sub_category: Optional[str] = None
    progress_unit: Optional[str] = None
    total: Optional[int] = None
    progress_value: Optional[float] = None
    status: Optional[str] = None
    rating: Optional[int] = Field(None, ge=0, le=10)
    review: Optional[str] = None
    bangumi_id: Optional[int] = None
    cover_url: Optional[str] = None
    cover_source: Optional[CoverSource] = None
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
    is_free: Optional[bool] = None

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        valid = {e.value for e in Category}
        if v not in valid:
            raise ValueError(f"无效分类 '{v}'，可选: {', '.join(sorted(valid))}")
        return v

    @field_validator("progress_unit")
    @classmethod
    def validate_progress_unit(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        valid = {e.value for e in ProgressUnit}
        if v not in valid:
            raise ValueError(f"无效进度单位 '{v}'，可选: {', '.join(sorted(valid))}")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        valid = {e.value for e in WorkStatus} | {e.value for e in GameStatus}
        if v not in valid:
            raise ValueError(f"无效状态 '{v}'，可选: {', '.join(sorted(valid))}")
        return v


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
    is_free: bool = False
    game_status: str = "wish"
    game_progress_value: Optional[float] = None
    game_profile_id: Optional[int] = None

    model_config = {"from_attributes": True}

    @field_validator("is_free", mode="before")
    @classmethod
    def coerce_is_free(cls, v):
        if v is None:
            return False
        return v


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
