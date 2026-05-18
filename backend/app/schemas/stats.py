from pydantic import BaseModel


class CategoryCount(BaseModel):
    category: str
    count: int


class StatusCount(BaseModel):
    status: str
    count: int


class RatingBucket(BaseModel):
    rating: int
    count: int


class StatsResponse(BaseModel):
    total_works: int
    category_counts: list[CategoryCount]
    status_counts: list[StatusCount]
    rating_distribution: list[RatingBucket]
