from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models.work import Work, WorkStatus
from ..models.game_profile import GameProfile
from ..models.timeline import TimelineEntry

router = APIRouter(tags=["stats"])


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    total_works = db.query(Work).count()

    # Category distribution
    cat_rows = (
        db.query(Work.category, func.count(Work.id))
        .group_by(Work.category)
        .all()
    )
    category_counts = [{"category": c, "count": n} for c, n in cat_rows]

    # Status distribution (non-game uses Work.status, game uses GameProfile.status)
    status_counts = []

    # Non-game statuses
    non_game_rows = (
        db.query(Work.status, func.count(Work.id))
        .filter(Work.category != "game", Work.status.isnot(None))
        .group_by(Work.status)
        .all()
    )
    for s, n in non_game_rows:
        status_counts.append({"status": s.value if hasattr(s, "value") else s, "count": n})

    # Game statuses (from GameProfile)
    game_rows = (
        db.query(GameProfile.status, func.count(GameProfile.id))
        .group_by(GameProfile.status)
        .all()
    )
    for s, n in game_rows:
        key = s.value if hasattr(s, "value") else s
        # Merge into existing or append
        found = False
        for sc in status_counts:
            if sc["status"] == key:
                sc["count"] += n
                found = True
                break
        if not found:
            status_counts.append({"status": key, "count": n})

    # Rating distribution (0-10, including null as "unrated")
    # 游戏的评分挂在 GameProfile 上，与 Work 评分合并统计
    rating_rows = (
        db.query(Work.rating, func.count(Work.id))
        .group_by(Work.rating)
        .all()
    )
    rating_map = {}
    for r, n in rating_rows:
        key = r if r is not None else -1
        rating_map[key] = rating_map.get(key, 0) + n
    gp_rating_rows = (
        db.query(GameProfile.rating, func.count(GameProfile.id))
        .group_by(GameProfile.rating)
        .all()
    )
    for r, n in gp_rating_rows:
        key = r if r is not None else -1
        rating_map[key] = rating_map.get(key, 0) + n
    rating_distribution = [{"rating": k, "count": v} for k, v in rating_map.items()]

    # 本周活跃（最近 7 天）：时间线操作数与有更新的作品数
    # created_at/updated_at 均为 UTC（server_default func.now()），与 utcnow 可比
    cutoff = datetime.utcnow() - timedelta(days=7)
    week_ops = db.query(func.count(TimelineEntry.id)).filter(
        TimelineEntry.created_at >= cutoff).scalar()
    week_works = db.query(func.count(Work.id)).filter(
        Work.updated_at >= cutoff).scalar()

    # 月度活跃趋势（最近 6 个月，含当月）：按月聚合时间线操作数
    month_rows = db.query(
        func.strftime("%Y-%m", TimelineEntry.created_at),
        func.count(TimelineEntry.id),
    ).group_by(func.strftime("%Y-%m", TimelineEntry.created_at)).all()
    ops_by_month = {m: n for m, n in month_rows}
    monthly_activity = []
    now = datetime.utcnow()
    for i in range(5, -1, -1):
        ym = (now - timedelta(days=30 * i)).strftime("%Y-%m")
        monthly_activity.append({"month": ym, "operations": ops_by_month.get(ym, 0)})

    return {
        "total_works": total_works,
        "category_counts": category_counts,
        "status_counts": status_counts,
        "rating_distribution": rating_distribution,
        "week_activity": {
            "operations": week_ops or 0,
            "works_updated": week_works or 0,
        },
        "monthly_activity": monthly_activity,
    }
