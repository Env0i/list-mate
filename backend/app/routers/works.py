import httpx

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response, RedirectResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.work import Work, WorkStatus
from ..models.game_profile import GameProfile
from ..models.tag import WorkTag
from ..schemas.work import WorkCreate, WorkUpdate, WorkResponse, WorkListItem, PaginatedWorks
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

    return PaginatedWorks(
        items=[WorkListItem.model_validate(w) for w in works],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


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

    work = Work(**data.model_dump(exclude_unset=True), cover_data=cover_data)
    db.add(work)
    db.flush()

    # 游戏作品自动创建一个默认 GameProfile
    if work.category == "game":
        gp = GameProfile(work_id=work.id, name="本体", sort_order=0)
        db.add(gp)

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

    if "cover_url" in update_data and update_data["cover_url"] != work.cover_url:
        try:
            resp = httpx.get(update_data["cover_url"], timeout=10)
            if resp.status_code == 200:
                update_data["cover_data"] = resp.content
        except httpx.RequestError:
            pass

    user_set_status = "status" in update_data
    if user_set_status and update_data["status"] != WorkStatus.COMPLETED.value:
        update_data["auto_completed"] = False

    for key, value in update_data.items():
        setattr(work, key, value)

    # 自动标记完成（仅非游戏作品）
    if not user_set_status and work.category != "game":
        if (
            work.total and work.total > 0
            and work.progress_value is not None
            and work.progress_value >= work.total
            and not work.auto_completed
        ):
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
        created_at=work.created_at,
        updated_at=work.updated_at,
        game_profiles=[GameProfileResponse.model_validate(gp) for gp in work.game_profiles],
        tags=[TagResponse.model_validate(wt.tag) for wt in work.work_tags],
    )
