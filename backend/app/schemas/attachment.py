from datetime import datetime
from pydantic import BaseModel


class AttachmentResponse(BaseModel):
    id: int
    game_profile_id: int
    label: str
    file_name: str
    file_size: int
    created_at: datetime

    model_config = {"from_attributes": True}


class AttachmentUploadResponse(BaseModel):
    id: int
    label: str
    file_name: str
    file_size: int
