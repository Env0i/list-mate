from pydantic import BaseModel
from typing import Optional


class TagCreate(BaseModel):
    name: str
    color: str = "#5bc0de"


class TagUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None


class TagResponse(BaseModel):
    id: int
    name: str
    color: str

    model_config = {"from_attributes": True}
