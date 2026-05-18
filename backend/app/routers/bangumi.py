import httpx
from fastapi import APIRouter, HTTPException, Query
from ..config import BANGUMI_API_BASE
from ..schemas.bangumi import BangumiSearchResult, BangumiSearchResponse, BangumiSubjectResponse

router = APIRouter(tags=["bangumi"])

BANGUMI_HEADERS = {
    "User-Agent": "list-mate/1.0 (personal project)",
}


@router.get("/bangumi/search", response_model=BangumiSearchResponse)
def search_bangumi(
    q: str = Query(min_length=1),
    type: int | None = Query(None, description="1=anime 2=comic 3=game 5=novel"),
    db=None,  # unused, kept for FastAPI DI consistency
):
    body = {"keyword": q}
    if type:
        body["type"] = type

    try:
        resp = httpx.post(
            f"{BANGUMI_API_BASE}/v0/search/subjects",
            json=body,
            headers=BANGUMI_HEADERS,
            timeout=10,
        )
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
        )
        for item in data.get("data", [])
    ]

    return BangumiSearchResponse(results=results, total=data.get("total", len(results)))


@router.get("/bangumi/{bangumi_id}", response_model=BangumiSubjectResponse)
def get_bangumi_subject(bangumi_id: int):
    try:
        resp = httpx.get(
            f"{BANGUMI_API_BASE}/v0/subjects/{bangumi_id}",
            headers=BANGUMI_HEADERS,
            timeout=10,
        )
        resp.raise_for_status()
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Bangumi API 不可用")

    data = resp.json()
    return BangumiSubjectResponse(
        id=data["id"],
        name=data.get("name", ""),
        name_cn=data.get("name_cn", ""),
        summary=data.get("summary", ""),
        image_url=data.get("images", {}).get("medium") if data.get("images") else None,
        type=data.get("type", 0),
        total_episodes=data.get("total_episodes") or data.get("total"),
    )
