"""Shared utility functions."""
import json

from sqlalchemy.orm import Session

from .models.timeline import TimelineEntry


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
