import csv
import io
import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.work import Work
from ..models.tag import Tag, WorkTag
from ..models.game_profile import GameProfile, GameStatus

router = APIRouter(tags=["export"])


@router.get("/export/json")
def export_json(db: Session = Depends(get_db)):
    works = db.query(Work).order_by(Work.created_at.desc()).all()
    result = []
    for w in works:
        tags = [wt.tag.name for wt in w.work_tags]
        gps = [
            {
                "name": gp.name,
                "status": gp.status.value,
                "progress_type": gp.progress_type.value,
                "progress_value": gp.progress_value,
                "rating": gp.rating,
                "review": gp.review,
                "start_date": gp.start_date,
                "finish_date": gp.finish_date,
                "playtime_hours": gp.playtime_hours,
                "source": gp.source,
                "mods_list": gp.mods_list,
                "notes": gp.notes,
            }
            for gp in w.game_profiles
        ]
        result.append({
            "title": w.title,
            "category": w.category.value if hasattr(w.category, "value") else w.category,
            "sub_category": w.sub_category,
            "status": w.status.value if w.status else None,
            "rating": w.rating,
            "review": w.review,
            "total": w.total,
            "progress_value": w.progress_value,
            "progress_unit": w.progress_unit.value if hasattr(w.progress_unit, "value") else w.progress_unit,
            "summary": w.summary,
            "start_date": w.start_date,
            "finish_date": w.finish_date,
            "platform": w.platform,
            "priority": w.priority,
            "purchase_platform": w.purchase_platform,
            "purchase_price": w.purchase_price,
            "playtime_hours": w.playtime_hours,
            "replay_count": w.replay_count,
            "external_links": w.external_links,
            "tags": tags,
            "game_profiles": gps,
            "created_at": w.created_at.isoformat(),
            "updated_at": w.updated_at.isoformat(),
        })
    return StreamingResponse(
        iter([json.dumps(result, ensure_ascii=False, indent=2)]),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=list-mate-export.json"},
    )


@router.get("/export/csv")
def export_csv(db: Session = Depends(get_db)):
    works = db.query(Work).order_by(Work.created_at.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "标题", "品类", "子分类", "状态", "评分", "评价",
        "总进度", "当前进度", "进度单位", "简介",
        "开始时间", "完成时间", "平台", "优先度",
        "购买平台", "购买价格", "游戏时长", "重刷次数",
        "标签", "创建时间", "更新时间",
    ])
    for w in works:
        tags = ", ".join(wt.tag.name for wt in w.work_tags)
        writer.writerow([
            w.title,
            w.category.value if hasattr(w.category, "value") else w.category,
            w.sub_category,
            w.status.value if w.status else "",
            w.rating,
            w.review or "",
            w.total or "",
            w.progress_value or "",
            w.progress_unit.value if hasattr(w.progress_unit, "value") else w.progress_unit,
            w.summary or "",
            w.start_date or "",
            w.finish_date or "",
            w.platform or "",
            w.priority or "",
            w.purchase_platform or "",
            w.purchase_price or "",
            w.playtime_hours or "",
            w.replay_count or "",
            tags,
            w.created_at.isoformat() if w.created_at else "",
            w.updated_at.isoformat() if w.updated_at else "",
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=list-mate-export.csv"},
    )
