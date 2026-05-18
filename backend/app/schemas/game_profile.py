from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class GameProfileCreate(BaseModel):
    name: str = "本体"
    progress_value: Optional[float] = None
    progress_type: Optional[str] = None
    status: Optional[str] = None
    rating: Optional[int] = None
    review: Optional[str] = None
    start_date: Optional[str] = None
    finish_date: Optional[str] = None
    playtime_hours: Optional[float] = None
    source: Optional[str] = None
    mods_list: Optional[str] = None
    notes: Optional[str] = None
    sort_order: int = 0


class GameProfileUpdate(BaseModel):
    name: Optional[str] = None
    progress_value: Optional[float] = None
    progress_type: Optional[str] = None
    status: Optional[str] = None
    rating: Optional[int] = None
    review: Optional[str] = None
    start_date: Optional[str] = None
    finish_date: Optional[str] = None
    playtime_hours: Optional[float] = None
    source: Optional[str] = None
    mods_list: Optional[str] = None
    notes: Optional[str] = None
    sort_order: Optional[int] = None


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
