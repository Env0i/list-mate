from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class ProfileResponse(BaseModel):
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
