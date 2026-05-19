from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.timeline import TimelineEntry
from ..schemas.timeline import TimelineEntryResponse, PaginatedTimeline
from ..utils import record_timeline

router = APIRouter(tags=["timeline"])


@router.get("/timeline", response_model=PaginatedTimeline)
def list_timeline(
    work_id: int | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(30, ge=1, le=200),
    db: Session = Depends(get_db),
):
    query = db.query(TimelineEntry)
    if work_id:
        query = query.filter(TimelineEntry.work_id == work_id)

    total = query.count()
    total_pages = (total + page_size - 1) // page_size if total else 0
    entries = (
        query.order_by(TimelineEntry.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return PaginatedTimeline(
        items=entries,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )
