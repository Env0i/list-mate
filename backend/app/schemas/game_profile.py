from datetime import datetime
from pydantic import BaseModel, field_validator, Field
from typing import Optional

from ..models.game_profile import GameStatus, ProgressType


class GameProfileCreate(BaseModel):
    name: str = "本体"
    progress_value: Optional[float] = None
    progress_type: Optional[str] = None
    status: Optional[str] = None
    rating: Optional[int] = Field(None, ge=0, le=10)
    review: Optional[str] = None
    start_date: Optional[str] = None
    finish_date: Optional[str] = None
    playtime_hours: Optional[float] = None
    source: Optional[str] = None
    mods_list: Optional[str] = None
    notes: Optional[str] = None
    sort_order: int = 0

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        valid = {e.value for e in GameStatus}
        if v not in valid:
            raise ValueError(f"无效游戏状态 '{v}'，可选: {', '.join(sorted(valid))}")
        return v

    @field_validator("progress_type")
    @classmethod
    def validate_progress_type(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        valid = {e.value for e in ProgressType}
        if v not in valid:
            raise ValueError(f"无效进度类型 '{v}'，可选: {', '.join(sorted(valid))}")
        return v


class GameProfileUpdate(BaseModel):
    name: Optional[str] = None
    progress_value: Optional[float] = None
    progress_type: Optional[str] = None
    status: Optional[str] = None
    rating: Optional[int] = Field(None, ge=0, le=10)
    review: Optional[str] = None
    start_date: Optional[str] = None
    finish_date: Optional[str] = None
    playtime_hours: Optional[float] = None
    source: Optional[str] = None
    mods_list: Optional[str] = None
    notes: Optional[str] = None
    sort_order: Optional[int] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        valid = {e.value for e in GameStatus}
        if v not in valid:
            raise ValueError(f"无效游戏状态 '{v}'，可选: {', '.join(sorted(valid))}")
        return v

    @field_validator("progress_type")
    @classmethod
    def validate_progress_type(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        valid = {e.value for e in ProgressType}
        if v not in valid:
            raise ValueError(f"无效进度类型 '{v}'，可选: {', '.join(sorted(valid))}")
        return v


class GameProfileResponse(BaseModel):
    id: int
    work_id: int
    name: str
    progress_value: Optional[float] = None
    progress_type: str
    status: str
    rating: Optional[int] = None
    review: Optional[str] = None
    start_date: Optional[str] = None
    finish_date: Optional[str] = None
    playtime_hours: Optional[float] = None
    source: Optional[str] = None
    mods_list: Optional[str] = None
    notes: Optional[str] = None
    auto_completed: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
