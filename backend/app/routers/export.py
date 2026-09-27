import csv
import io
import json
import os
import shutil
import sqlite3
import tempfile
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse, FileResponse
from sqlalchemy.orm import Session
from starlette.background import BackgroundTask

from sqlalchemy.orm import selectinload
from ..config import DATABASE_PATH
from ..database import engine, get_db
from ..models.work import Work
from ..models.tag import Tag, WorkTag
from ..models.game_profile import GameProfile, GameStatus

router = APIRouter(tags=["export"])


@router.get("/backup")
def backup_database():
    """整库在线备份（含时间线/附件/封面 BLOB 等导出接口不覆盖的数据）。

    WAL 模式下直接拷贝 .db 文件会丢未 checkpoint 的数据，用 SQLite
    在线 backup API 生成一致性快照；响应结束后删除临时文件。"""
    fd, tmp_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    src = sqlite3.connect(DATABASE_PATH)
    dst = sqlite3.connect(tmp_path)
    with dst:
        src.backup(dst)
    dst.close()
    src.close()
    return FileResponse(
        tmp_path,
        media_type="application/octet-stream",
        filename=f"zace-backup-{datetime.now().strftime('%Y%m%d')}.db",
        background=BackgroundTask(os.remove, tmp_path),
    )


REQUIRED_TABLES = ("works", "game_profiles", "timeline_entries", "tags", "work_tags", "attachments")


@router.post("/restore")
def restore_database(file: UploadFile = File(...)):
    """从 .db 备份文件还原数据库（覆盖式）。

    流程：校验上传文件为合法 SQLite 且表结构齐全 → 当前库先自动备份到
    backups/<时间戳>.db → 替换库文件并清理 WAL/SHM → 释放连接池（新请求
    即读新库）。替换是覆盖式的，务必依赖还原前的自动备份兜底。"""
    raw = file.file.read()

    # 1. 必须是 SQLite 文件
    if raw[:16] != b"SQLite format 3\x00":
        raise HTTPException(status_code=400, detail="备份文件不是有效的 SQLite 数据库")

    # 2. 落到临时文件，校验表结构齐全
    fd, tmp_path = tempfile.mkstemp(suffix=".db")
    with os.fdopen(fd, "wb") as f:
        f.write(raw)
    try:
        check = sqlite3.connect(tmp_path)
        tables = {row[0] for row in check.execute(
            "SELECT name FROM sqlite_master WHERE type='table'")}
        check.close()
        missing = [t for t in REQUIRED_TABLES if t not in tables]
        if missing:
            os.remove(tmp_path)
            raise HTTPException(
                status_code=400,
                detail=f"备份缺少必需的数据表: {', '.join(missing)}")
    except HTTPException:
        raise
    except sqlite3.DatabaseError:
        os.remove(tmp_path)
        raise HTTPException(status_code=400, detail="备份文件已损坏，无法读取")

    # 3. 还原前把当前库快照到服务器 backups/ 目录
    backup_dir = os.path.join(os.path.dirname(str(DATABASE_PATH)), "backups")
    os.makedirs(backup_dir, exist_ok=True)
    snapshot = os.path.join(backup_dir, f"pre-restore-{datetime.now().strftime('%Y%m%d-%H%M%S')}.db")
    src = sqlite3.connect(str(DATABASE_PATH))
    keep = sqlite3.connect(snapshot)
    with keep:
        src.backup(keep)
    keep.close()
    src.close()

    # 4. 替换库文件（清掉 WAL/SHM 残留），释放连接池让新请求读新库
    engine.dispose()
    os.replace(tmp_path, str(DATABASE_PATH))
    for suffix in ("-wal", "-shm"):
        side = str(DATABASE_PATH) + suffix
        if os.path.exists(side):
            os.remove(side)

    return {"message": "还原成功，当前数据已自动备份为 " + os.path.basename(snapshot)}


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
        headers={"Content-Disposition": f"attachment; filename=zace-export-{datetime.now().strftime('%Y%m%d')}.json"},
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
        headers={"Content-Disposition": f"attachment; filename=zace-export-{datetime.now().strftime('%Y%m%d')}.csv"},
    )
