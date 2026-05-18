from datetime import datetime
from pydantic import BaseModel


class TimelineEntryResponse(BaseModel):
    id: int
    work_id: int
    game_profile_id: int | None = None
    action_type: str
    old_value: str | None = None
    new_value: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class PaginatedTimeline(BaseModel):
    items: list[TimelineEntryResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
