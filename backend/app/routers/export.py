import csv
import io
import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from sqlalchemy.orm import selectinload
from ..database import get_db
from ..models.work import Work
from ..models.tag import Tag, WorkTag
from ..models.game_profile import GameProfile, GameStatus

router = APIRouter(tags=["export"])


@router.get("/export/json")
def export_json(db: Session = Depends(get_db)):
    works = db.query(Work).options(
        selectinload(Work.game_profiles),
        selectinload(Work.work_tags).selectinload(WorkTag.tag),
    ).order_by(Work.created_at.desc()).all()
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
                "auto_completed": gp.auto_completed,
                "sort_order": gp.sort_order,
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
            "purchase_date": w.purchase_date,
            "purchase_price": w.purchase_price,
            "playtime_hours": w.playtime_hours,
            "replay_count": w.replay_count,
            "external_links": w.external_links,
            "is_free": w.is_free,
            "auto_completed": w.auto_completed,
            "bangumi_id": w.bangumi_id,
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
    works = db.query(Work).options(
        selectinload(Work.work_tags).selectinload(WorkTag.tag),
    ).order_by(Work.created_at.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "标题", "品类", "子分类", "状态", "评分", "评价",
        "总进度", "当前进度", "进度单位", "简介",
        "开始时间", "完成时间", "平台", "优先度",
        "购买平台", "购买价格", "购买时间", "免费", "游戏时长", "重刷次数",
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
            "" if w.total is None else w.total,
            "" if w.progress_value is None else (int(w.progress_value) if float(w.progress_value).is_integer() else w.progress_value),
            w.progress_unit.value if hasattr(w.progress_unit, "value") else w.progress_unit,
            w.summary or "",
            w.start_date or "",
            w.finish_date or "",
            w.platform or "",
            "" if w.priority is None else w.priority,
            w.purchase_platform or "",
            "" if w.purchase_price is None else w.purchase_price,
            w.purchase_date or "",
            "是" if w.is_free else "",
            "" if w.playtime_hours is None else w.playtime_hours,
            "" if w.replay_count is None else w.replay_count,
            tags,
            w.created_at.isoformat() if w.created_at else "",
            w.updated_at.isoformat() if w.updated_at else "",
        ])

    output.seek(0)
    # UTF-8 BOM：无 BOM 时 Excel 直接打开中文 CSV 会乱码
    return StreamingResponse(
        iter(["﻿" + output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=list-mate-export.csv"},
    )
