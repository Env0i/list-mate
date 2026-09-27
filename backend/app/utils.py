"""Shared utility functions."""
from __future__ import annotations
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
    """Record a timeline entry. old/new values are serialized to JSON strings.

    变更类记录新旧值相同时跳过（如手动标记完成后再触发自动完成规则，
    避免 completed→completed 的垃圾条目）；created 记录不适用此规则。
    """
    if action_type != "created" and old_value == new_value:
        return None
    entry = TimelineEntry(
        work_id=work_id,
        game_profile_id=game_profile_id,
        action_type=action_type,
        old_value=json.dumps(old_value, ensure_ascii=False) if old_value is not None else None,
        new_value=json.dumps(new_value, ensure_ascii=False) if new_value is not None else None,
    )
    db.add(entry)
