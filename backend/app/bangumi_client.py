from __future__ import annotations
import json
import threading
import time
from datetime import datetime

import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session

from .config import BANGUMI_API_BASE
from .models.bangumi_cache import BangumiCache

# 出站请求统一约束：只发 GET、UA 保留、全局节流 ≥1 req/s（硬约束）
BANGUMI_HEADERS = {
    "User-Agent": "list-mate/1.0 (personal project)",
}
MIN_INTERVAL = 1.0

_throttle_lock = threading.Lock()
_last_request_at = 0.0


def bangumi_get(url: str, *, timeout: float = 10.0) -> httpx.Response:
    """节流的出站 GET：全局令牌间隔 ≥1 秒；错误映射见 _map_upstream_error。"""
    global _last_request_at
    with _throttle_lock:
        wait = MIN_INTERVAL - (time.monotonic() - _last_request_at)
        if wait > 0:
            time.sleep(wait)
        _last_request_at = time.monotonic()
    try:
        resp = httpx.get(url, headers=BANGUMI_HEADERS, timeout=timeout, follow_redirects=True)
    except httpx.TimeoutException as e:
        raise _map_upstream_error(e)
    except httpx.RequestError as e:
        raise _map_upstream_error(e)
    if resp.status_code != 200:
        raise _map_upstream_error(None, status_code=resp.status_code)
    return resp


def _map_upstream_error(exc: Exception | None = None, *, status_code: int | None = None) -> HTTPException:
    """§3.3 错误码：超时 504 / 限流 429 / 不存在 404 / 其他 502。"""
    if status_code == 404:
        return HTTPException(status_code=404, detail="条目不存在")
    if status_code in (429, 403):
        return HTTPException(status_code=429, detail="请求过于频繁", headers={"Retry-After": "5"})
    if status_code is not None:
        return HTTPException(status_code=502, detail="Bangumi 不可用")
    if isinstance(exc, httpx.TimeoutException):
        return HTTPException(status_code=504, detail="Bangumi 响应超时")
    return HTTPException(status_code=502, detail="Bangumi 不可用")


# ---------- 缓存 ----------

def _age_seconds(fetched_at: datetime) -> float:
    # fetched_at 为 naive UTC（SQLite CURRENT_TIMESTAMP），与 utcnow 直接作差
    return (datetime.utcnow() - fetched_at).total_seconds()


def cache_get(db: Session, key: str) -> BangumiCache | None:
    return db.get(BangumiCache, key)


def cache_put(db: Session, key: str, payload, status_code: int = 200) -> datetime:
    row = db.get(BangumiCache, key)
    payload_str = json.dumps(payload, ensure_ascii=False)
    now = datetime.utcnow()
    if row is None:
        db.add(BangumiCache(key=key, payload=payload_str, status=status_code, fetched_at=now))
    else:
        row.payload = payload_str
        row.status = status_code
        row.fetched_at = now
    db.commit()
    return now


def cached_json(db: Session, key: str, url: str, ttl_seconds: int):
    """缓存优先的 JSON 取数：命中未过期直接返回；过期/缺失时请求上游，
    上游失败则回退旧缓存并标记 stale（§3.2）。返回 (data, stale, fetched_at)。"""
    row = cache_get(db, key)
    if row is not None and _age_seconds(row.fetched_at) < ttl_seconds:
        return json.loads(row.payload), False, row.fetched_at
    try:
        resp = bangumi_get(url)
        data = resp.json()
        fetched_at = cache_put(db, key, data)
        return data, False, fetched_at
    except HTTPException:
        if row is not None:
            # 上游失败但有过期缓存：返回旧数据 + stale 标记
            return json.loads(row.payload), True, row.fetched_at
        raise
