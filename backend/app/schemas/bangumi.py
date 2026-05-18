from pydantic import BaseModel
from typing import Optional


class BangumiSearchResult(BaseModel):
    bangumi_id: int
    name: str
    name_cn: str
    summary: str
    image_url: Optional[str] = None
    type: int


class BangumiSearchResponse(BaseModel):
    results: list[BangumiSearchResult]
    total: int


class BangumiSubjectResponse(BaseModel):
    id: int
    name: str
    name_cn: str
    summary: str
    image_url: Optional[str] = None
    type: int
    total_episodes: Optional[int] = None
