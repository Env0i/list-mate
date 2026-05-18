import httpx

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response, RedirectResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.work import Work
from ..models.profile import Profile
from ..models.tag import WorkTag
from ..schemas.work import WorkCreate, WorkUpdate, WorkResponse, WorkListItem, PaginatedWorks
from ..schemas.profile import ProfileResponse
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
        query = query.filter(Work.profiles.any(Profile.status == status))
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

    work = Work(**data.model_dump(), cover_data=cover_data)
    db.add(work)
    db.flush()

    profile = Profile(work_id=work.id, name="默认", sort_order=0)
    db.add(profile)
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

    for key, value in update_data.items():
        setattr(work, key, value)

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
        cover_url=work.cover_url,
        bangumi_id=work.bangumi_id,
        cover_source=val(work.cover_source),
        created_at=work.created_at,
        updated_at=work.updated_at,
        profiles=[ProfileResponse.model_validate(p) for p in work.profiles],
        tags=[TagResponse.model_validate(wt.tag) for wt in work.work_tags],
    )
