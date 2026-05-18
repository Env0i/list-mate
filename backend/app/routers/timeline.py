import json

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.timeline import TimelineEntry
from ..schemas.timeline import TimelineEntryResponse, PaginatedTimeline

router = APIRouter(tags=["timeline"])


def record_timeline(
    db: Session,
    work_id: int,
    action_type: str,
    old_value=None,
    new_value=None,
    game_profile_id: int | None = None,
):
    """Record a timeline entry. old/new values are serialized to JSON strings."""
    entry = TimelineEntry(
        work_id=work_id,
        game_profile_id=game_profile_id,
        action_type=action_type,
        old_value=json.dumps(old_value, ensure_ascii=False) if old_value is not None else None,
        new_value=json.dumps(new_value, ensure_ascii=False) if new_value is not None else None,
    )
    db.add(entry)


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
