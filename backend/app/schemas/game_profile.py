from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class GameProfileCreate(BaseModel):
    name: str = "本体"
    progress_value: Optional[float] = None
    status: Optional[str] = None
    rating: Optional[int] = None
    review: Optional[str] = None
    sort_order: int = 0


class GameProfileUpdate(BaseModel):
    name: Optional[str] = None
    progress_value: Optional[float] = None
    status: Optional[str] = None
    rating: Optional[int] = None
    review: Optional[str] = None
    sort_order: Optional[int] = None


class GameProfileResponse(BaseModel):
    id: int
    work_id: int
    name: str
    progress_value: Optional[float] = None
    status: str
    rating: Optional[int] = None
    review: Optional[str] = None
    auto_completed: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
