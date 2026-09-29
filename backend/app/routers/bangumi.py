from __future__ import annotations
import hashlib
import time
from datetime import datetime

import httpx
from fastapi import APIRouter, HTTPException, Query, Response
from sqlalchemy.orm import Session

from ..bangumi_client import BANGUMI_HEADERS, bangumi_get, cached_json
from ..config import BANGUMI_API_BASE, BASE_DIR
from ..database import get_db
from ..models.work import Work
from ..schemas.bangumi import BangumiSearchResult, BangumiSearchResponse, BangumiSubjectResponse
from fastapi import Depends

router = APIRouter(tags=["bangumi"])

# 图片代理本地缓存目录（30 天）
IMAGE_CACHE_DIR = BASE_DIR / "bangumi_cache"
IMAGE_TTL = 30 * 86400
# 仅允许 Bangumi 图床域名（防 SSRF）
IMAGE_ALLOWED_SUFFIXES = ("bgm.tv", "bangumi.tv", "bgm.tv", "lain.bgm.tv")


def _ttl_by_airdate(subject_data: dict) -> int:
    """分集缓存时长：放送中（无日期或首播在未来）6 小时，完结 7 天（§3.1）。"""
    date = subject_data.get("date")
    if not date:
        return 6 * 3600
    try:
        air = datetime.strptime(date, "%Y-%m-%d")
        if air > datetime.utcnow():
            return 6 * 3600
    except ValueError:
        return 6 * 3600
    return 7 * 86400


@router.get("/bangumi/search", response_model=BangumiSearchResponse)
def search_bangumi(
    q: str = Query(min_length=1),
    type: int | None = Query(None, description="Bangumi 类型：1=书籍(含小说/漫画) 2=动画 3=音乐 4=游戏"),
):
    # 实测：v0 POST 搜索 + filter.type 是唯一正确过滤口径（旧版 GET 会忽略 type），
    # 语义为只读查询；其余 Bangumi 出站请求全部为 GET
    body = {"keyword": q}
    if type:
        body["filter"] = {"type": [type]}

    with httpx.Client(headers=BANGUMI_HEADERS, timeout=10) as client:
        try:
            resp = client.post(f"{BANGUMI_API_BASE}/v0/search/subjects", json=body)
            resp.raise_for_status()
        except httpx.RequestError:
            raise HTTPException(status_code=502, detail="搜索服务不可用")

    data = resp.json()
    results = [
        BangumiSearchResult(
            bangumi_id=item["id"],
            name=item.get("name", ""),
            name_cn=item.get("name_cn", ""),
            summary=item.get("summary", ""),
            image_url=item.get("images", {}).get("medium"),
            type=item.get("type", 0),
            date=item.get("date"),
        )
        for item in data.get("data", [])
    ]

    return BangumiSearchResponse(results=results, total=data.get("total", len(results)))


@router.get("/bangumi/calendar")
def get_calendar(db: Session = Depends(get_db)):
    """每日放送（旧版接口，v0 无此端点），按星期分组；6 小时缓存。"""
    data, stale, fetched_at = cached_json(db, "calendar", f"{BANGUMI_API_BASE}/calendar", 6 * 3600)
    return {"data": data, "stale": stale, "fetched_at": fetched_at}


@router.get("/bangumi/ranking")
def get_ranking(
    db: Session = Depends(get_db),
    type: int = Query(2, description="Bangumi 类型：2=动画 1=书籍 4=游戏"),
    limit: int = Query(10, ge=1, le=50),
):
    """高分榜（v0 sort=rank）；24 小时缓存。"""
    key = f"ranking:{type}:{limit}"
    url = f"{BANGUMI_API_BASE}/v0/subjects?type={type}&sort=rank&limit={limit}"
    data, stale, fetched_at = cached_json(db, key, url, 24 * 3600)
    return {"data": data.get("data", []), "total": data.get("total", 0), "stale": stale, "fetched_at": fetched_at}


@router.get("/bangumi/image")
def proxy_image(url: str = Query(min_length=1)):
    """Bangumi 图床代理 + 本地文件缓存（30 天）；仅允许 bgm.tv 系域名。"""
    host = httpx.URL(url).host or ""
    if not any(host == s or host.endswith("." + s) for s in ("bgm.tv", "bangumi.tv")):
        raise HTTPException(status_code=400, detail="仅支持 Bangumi 图床地址")

    IMAGE_CACHE_DIR.mkdir(exist_ok=True)
    ext = ".jpg"
    lower = url.lower()
    for e in (".png", ".webp", ".gif"):
        if lower.endswith(e):
            ext = e
            break
    path = IMAGE_CACHE_DIR / (hashlib.sha256(url.encode()).hexdigest() + ext)

    if path.exists() and time.time() - path.stat().st_mtime < IMAGE_TTL:
        return Response(content=path.read_bytes(), media_type="image/jpeg")

    try:
        resp = httpx.get(url, headers=BANGUMI_HEADERS, timeout=15, follow_redirects=True)
        resp.raise_for_status()
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Bangumi 不可用")

    path.write_bytes(resp.content)
    return Response(
        content=resp.content,
        media_type=resp.headers.get("content-type", "image/jpeg"),
        headers={"Cache-Control": "public, max-age=2592000"},
    )


@router.get("/bangumi/{bangumi_id}", response_model=BangumiSubjectResponse)
def get_bangumi_subject(bangumi_id: int, db: Session = Depends(get_db)):
    """条目详情（扩展：评分/收藏/标签/infobox/date），24 小时缓存；上游失败回退旧缓存 + stale。"""
    data, stale, fetched_at = cached_json(db, f"subject:{bangumi_id}", f"{BANGUMI_API_BASE}/v0/subjects/{bangumi_id}", 24 * 3600)
    return BangumiSubjectResponse(
        id=data["id"],
        name=data.get("name", ""),
        name_cn=data.get("name_cn", ""),
        summary=data.get("summary", ""),
        image_url=data.get("images", {}).get("medium") if data.get("images") else None,
        type=data.get("type", 0),
        total_episodes=data.get("total_episodes") or data.get("total"),
        date=data.get("date"),
        rating=data.get("rating"),
        collection=data.get("collection"),
        tags=data.get("tags"),
        infobox=data.get("infobox"),
        fetched_at=fetched_at,
        stale=stale,
    )


@router.get("/bangumi/{bangumi_id}/episodes")
def get_bangumi_episodes(
    bangumi_id: int,
    db: Session = Depends(get_db),
    type: int | None = Query(None, description="0=正片 1=SP 2=OP 3=ED；缺省返回全部"),
):
    """分集列表；放送中 6 小时 / 完结 7 天缓存。"""
    subject, _, _ = cached_json(db, f"subject:{bangumi_id}", f"{BANGUMI_API_BASE}/v0/subjects/{bangumi_id}", 24 * 3600)
    ttl = _ttl_by_airdate(subject)

    key = f"episodes:{bangumi_id}:{type if type is not None else 'all'}"
    url = f"{BANGUMI_API_BASE}/v0/episodes?subject_id={bangumi_id}&limit=200"
    if type is not None:
        url += f"&type={type}"
    data, stale, fetched_at = cached_json(db, key, url, ttl)

    episodes = [
        {
            "type": ep.get("type"),
            "sort": ep.get("sort"),
            "name": ep.get("name"),
            "name_cn": ep.get("name_cn"),
            "airdate": ep.get("airdate"),
            "duration": ep.get("duration"),
            "comment": ep.get("comment"),
        }
        for ep in data.get("data", [])
    ]
    return {"data": episodes, "total": data.get("total", len(episodes)), "stale": stale, "fetched_at": fetched_at}


@router.get("/bangumi/{bangumi_id}/relations")
def get_bangumi_relations(bangumi_id: int, db: Session = Depends(get_db)):
    """关联作品；7 天缓存。in_library_work_id 按 works.bangumi_id 回填（已入册印章）。"""
    data, stale, fetched_at = cached_json(db, f"relations:{bangumi_id}", f"{BANGUMI_API_BASE}/v0/subjects/{bangumi_id}/subjects", 7 * 86400)

    rel_ids = [r.get("id") for r in data if isinstance(r, dict) and r.get("id")]
    in_library: dict[int, int] = {}
    if rel_ids:
        rows = db.query(Work.id, Work.bangumi_id).filter(Work.bangumi_id.in_(rel_ids)).all()
        in_library = {w.bangumi_id: w.id for w in rows}

    relations = [
        {
            "id": r.get("id"),
            "relation": r.get("relation"),
            "name": r.get("name"),
            "name_cn": r.get("name_cn"),
            "type": r.get("type"),
            "image_url": (r.get("images") or {}).get("medium"),
            "in_library_work_id": in_library.get(r.get("id")),
        }
        for r in data
        if isinstance(r, dict) and r.get("id")
    ]
    return {"data": relations, "stale": stale, "fetched_at": fetched_at}


@router.get("/bangumi/{bangumi_id}/characters")
def get_bangumi_characters(bangumi_id: int, db: Session = Depends(get_db)):
    """主要角色（含声优）；7 天缓存。"""
    data, stale, fetched_at = cached_json(db, f"characters:{bangumi_id}", f"{BANGUMI_API_BASE}/v0/subjects/{bangumi_id}/characters", 7 * 86400)
    characters = [
        {
            "id": c.get("id"),
            "name": c.get("name"),
            "relation": c.get("relation"),
            "image_url": (c.get("images") or {}).get("medium"),
            "actors": [{"name": a.get("name")} for a in c.get("actors", [])],
        }
        for c in data
        if isinstance(c, dict) and c.get("id")
    ]
    return {"data": characters, "stale": stale, "fetched_at": fetched_at}


@router.get("/bangumi/{bangumi_id}/persons")
def get_bangumi_persons(bangumi_id: int, db: Session = Depends(get_db)):
    """制作人员（前端按主 staff 高亮排序）；7 天缓存。"""
    data, stale, fetched_at = cached_json(db, f"persons:{bangumi_id}", f"{BANGUMI_API_BASE}/v0/subjects/{bangumi_id}/persons", 7 * 86400)
    persons = [
        {
            "id": p.get("id"),
            "name": p.get("name"),
            "relation": p.get("relation"),
            "type": p.get("type"),
            "career": p.get("career"),
        }
        for p in data
        if isinstance(p, dict) and p.get("id")
    ]
    return {"data": persons, "stale": stale, "fetched_at": fetched_at}
