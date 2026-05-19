import httpx

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import Response, RedirectResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.work import Work, WorkStatus
from ..models.game_profile import GameProfile
from ..models.tag import Tag, WorkTag
from ..schemas.work import WorkCreate, WorkUpdate, WorkResponse, WorkListItem, PaginatedWorks
from .timeline import record_timeline
from ..schemas.game_profile import GameProfileResponse
from ..schemas.tag import TagResponse

router = APIRouter(tags=["works"])


@router.get("/works", response_model=PaginatedWorks)
def list_works(
    category: str | None = Query(None, description="anime/novel/comic/game"),
    status: str | None = Query(None, description="wish/watching/completed/paused/dropped"),
    tag_id: int | None = None,
    q: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Work)

    if category:
        query = query.filter(Work.category == category)

    if status:
        # 游戏的状态在 GameProfile 上，其他品类在 Work 上
        if category == "game":
            query = query.filter(Work.game_profiles.any(GameProfile.status == status))
        else:
            query = query.filter(Work.status == status)

    if tag_id:
        query = query.filter(Work.work_tags.any(WorkTag.tag_id == tag_id))
    if q:
        query = query.filter(Work.title.contains(q))

    total = query.count()
    total_pages = (total + page_size - 1) // page_size if total else 0
    works = (
        query.order_by(Work.updated_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    items = []
    for w in works:
        item_data = {k: v for k, v in WorkListItem.model_validate(w).model_dump().items()}
        item_data["tag_ids"] = [wt.tag_id for wt in w.work_tags]
        items.append(WorkListItem(**item_data))

    return PaginatedWorks(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


BANGUMI_HEADERS = {
    "User-Agent": "list-mate/1.0 (personal project)",
}


def _fetch_bangumi_subject(bangumi_id: int) -> str | None:
    """Fetch Bangumi subject detail and return JSON string of relevant metadata."""
    import json
    try:
        resp = httpx.get(
            f"https://api.bgm.tv/v0/subjects/{bangumi_id}",
            headers=BANGUMI_HEADERS,
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        return json.dumps({
            "date": data.get("date"),
            "platform": data.get("platform"),
            "total_episodes": data.get("total_episodes"),
            "volumes": data.get("volumes"),
            "score": data.get("rating", {}).get("score"),
            "infobox": data.get("infobox", []),
            "tags": [t["name"] for t in data.get("tags", [])[:20]],
        }, ensure_ascii=False)
    except httpx.RequestError:
        return None


@router.post("/works", response_model=WorkResponse, status_code=201)
def create_work(data: WorkCreate, db: Session = Depends(get_db)):
    cover_data = None

    if data.cover_url:
        try:
            resp = httpx.get(data.cover_url, timeout=10)
            if resp.status_code == 200:
                cover_data = resp.content
        except httpx.RequestError:
            pass

    create_data = data.model_dump()
    tag_ids = create_data.pop("tag_ids", [])
    is_game = create_data.get("category") == "game"

    # 游戏作品的状态只存在 GameProfile 上，不在 Work 表上
    if is_game:
        game_status = create_data.pop("status", None)

    create_data = {k: v for k, v in create_data.items() if v is not None}

    # Auto-fetch Bangumi subject data
    if data.bangumi_id and not getattr(data, 'bangumi_data', None):
        bd = _fetch_bangumi_subject(data.bangumi_id)
        if bd:
            create_data["bangumi_data"] = bd

    work = Work(**create_data, cover_data=cover_data)
    db.add(work)
    db.flush()

    # 游戏作品自动创建一个默认 GameProfile
    if is_game:
        gp = GameProfile(work_id=work.id, name="本体", sort_order=0)
        if game_status:
            gp.status = GameStatus(game_status)
        db.add(gp)

    # Tag associations
    for tid in tag_ids:
        tag = db.query(Tag).get(tid)
        if tag:
            db.add(WorkTag(work_id=work.id, tag_id=tid))

    cat_val = work.category.value if hasattr(work.category, "value") else work.category
    record_timeline(db, work.id, "created", new_value={"title": work.title, "category": cat_val})

    db.commit()
    db.refresh(work)
    return _work_to_response(work)


@router.get("/works/{work_id}", response_model=WorkResponse)
def get_work(work_id: int, db: Session = Depends(get_db)):
    work = db.query(Work).get(work_id)
    if not work:
        raise HTTPException(status_code=404, detail="作品不存在")
    return _work_to_response(work)


@router.put("/works/{work_id}", response_model=WorkResponse)
def update_work(work_id: int, data: WorkUpdate, db: Session = Depends(get_db)):
    work = db.query(Work).get(work_id)
    if not work:
        raise HTTPException(status_code=404, detail="作品不存在")

    update_data = data.model_dump(exclude_unset=True)

    # 游戏作品的状态只存在 GameProfile 上
    if work.category == "game" and "status" in update_data:
        status_val = update_data.pop("status")
        gp = db.query(GameProfile).filter(GameProfile.work_id == work.id).order_by(GameProfile.sort_order, GameProfile.id).first()
        if gp:
            gp.status = GameStatus(status_val)

    if "cover_url" in update_data and update_data["cover_url"] != work.cover_url:
        try:
            resp = httpx.get(update_data["cover_url"], timeout=10)
            if resp.status_code == 200:
                update_data["cover_data"] = resp.content
        except httpx.RequestError:
            pass

    tag_ids = update_data.pop("tag_ids", None)
    user_set_status = "status" in update_data
    if user_set_status and update_data["status"] != WorkStatus.COMPLETED.value:
        update_data["auto_completed"] = False

    # Record timeline for changed fields (before applying)
    if "status" in update_data and update_data["status"] != (work.status.value if work.status else None):
        record_timeline(db, work.id, "status_change",
                        old_value=work.status.value if work.status else None,
                        new_value=update_data["status"])
    if "rating" in update_data and update_data["rating"] != work.rating:
        record_timeline(db, work.id, "rating_change",
                        old_value=work.rating, new_value=update_data["rating"])
    if "review" in update_data and update_data["review"] != work.review:
        record_timeline(db, work.id, "review_change",
                        old_value=work.review, new_value=update_data["review"])
    if "progress_value" in update_data and update_data["progress_value"] != work.progress_value:
        record_timeline(db, work.id, "progress_update",
                        old_value=work.progress_value, new_value=update_data["progress_value"])

    for key, value in update_data.items():
        setattr(work, key, value)

    # Sync tags if provided
    if tag_ids is not None:
        db.query(WorkTag).filter(WorkTag.work_id == work.id).delete()
        for tid in tag_ids:
            tag = db.query(Tag).get(tid)
            if tag:
                db.add(WorkTag(work_id=work.id, tag_id=tid))

    # 自动标记完成（仅非游戏作品）
    if not user_set_status and work.category != "game":
        if (
            work.total and work.total > 0
            and work.progress_value is not None
            and work.progress_value >= work.total
            and not work.auto_completed
        ):
            record_timeline(db, work.id, "status_change",
                            old_value=work.status.value if work.status else None,
                            new_value=WorkStatus.COMPLETED.value)
            work.status = WorkStatus.COMPLETED
            work.auto_completed = True

    db.commit()
    db.refresh(work)
    return _work_to_response(work)


@router.delete("/works/{work_id}", status_code=204)
def delete_work(work_id: int, db: Session = Depends(get_db)):
    work = db.query(Work).get(work_id)
    if not work:
        raise HTTPException(status_code=404, detail="作品不存在")
    db.delete(work)
    db.commit()


@router.post("/works/{work_id}/cover", status_code=200)
def upload_work_cover(work_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    work = db.query(Work).get(work_id)
    if not work:
        raise HTTPException(status_code=404, detail="作品不存在")
    work.cover_data = file.file.read()
    work.cover_source = "manual"
    db.commit()
    return {"message": "封面上传成功"}


@router.get("/works/{work_id}/cover")
def get_work_cover(work_id: int, db: Session = Depends(get_db)):
    work = db.query(Work).get(work_id)
    if not work:
        raise HTTPException(status_code=404, detail="作品不存在")
    if work.cover_data:
        return Response(content=work.cover_data, media_type="image/jpeg")
    if work.cover_url:
        return RedirectResponse(url=work.cover_url)
    raise HTTPException(status_code=404, detail="无封面")


def _work_to_response(work: Work) -> WorkResponse:
    def val(v):
        return v.value if hasattr(v, "value") else v

    return WorkResponse(
        id=work.id,
        title=work.title,
        category=val(work.category),
        sub_category=work.sub_category,
        progress_unit=val(work.progress_unit),
        total=work.total,
        progress_value=work.progress_value,
        status=val(work.status) if work.status else None,
        rating=work.rating,
        review=work.review,
        auto_completed=work.auto_completed,
        cover_url=work.cover_url,
        bangumi_id=work.bangumi_id,
        cover_source=val(work.cover_source),
        summary=work.summary,
        start_date=work.start_date,
        finish_date=work.finish_date,
        platform=work.platform,
        purchase_platform=work.purchase_platform,
        purchase_date=work.purchase_date,
        purchase_price=work.purchase_price,
        playtime_hours=work.playtime_hours,
        replay_count=work.replay_count,
        priority=work.priority,
        external_links=work.external_links,
        bangumi_data=work.bangumi_data,
        created_at=work.created_at,
        updated_at=work.updated_at,
        game_profiles=[GameProfileResponse.model_validate(gp) for gp in work.game_profiles],
        tags=[TagResponse.model_validate(wt.tag) for wt in work.work_tags],
    )
