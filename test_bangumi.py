"""
Bangumi 只读代理测试（S3）。
前置：后端已在本机 8001 端口运行（python run.py）。
运行：从仓库根目录 `python test_bangumi.py`
覆盖：缓存命中、7 个只读接口、错误码映射、stale 回退（单测段）、图片代理域名校验。
"""
import sys
import time

import httpx

BASE = "http://localhost:8001/api"
client = httpx.Client(base_url=BASE, timeout=30)

results = {"pass": 0, "fail": 0, "tests": []}


def test(name, cond, detail=""):
    results["pass" if cond else "fail"] += 1 if not cond else 0
    if cond:
        results["pass"] += 1
        results["tests"].append(f"PASS {name}")
        print(f"  PASS {name}")
    else:
        results["fail"] += 1
        results["tests"].append(f"FAIL {name} {detail}")
        print(f"  FAIL {name} {detail}")


print("== subject 扩展 + 缓存 ==")
t0 = time.time()
r1 = client.get("/bangumi/400602")
test("subject 200", r1.status_code == 200, r1.text[:120])
d1 = r1.json()
test("subject 字段", all(k in d1 for k in ("rating", "collection", "tags", "infobox", "date", "fetched_at", "stale")), str(list(d1.keys())))
test("subject rating.score", isinstance((d1.get("rating") or {}).get("score"), (int, float)))
test("subject collection", isinstance(d1.get("collection"), dict) and "wish" in d1["collection"])
test("subject 首次非 stale", d1.get("stale") is False)
t1 = time.time() - t0

r2 = client.get("/bangumi/400602")
d2 = r2.json()
test("subject 二次命中缓存(fetched_at 不变)", d2.get("fetched_at") == d1.get("fetched_at"))
print(f"  (首调 {t1:.2f}s 含上游节流；二调应显著更快)")
t2 = time.time()
client.get("/bangumi/400602")
print(f"  (三调 {time.time()-t2:.2f}s)")

print("== episodes ==")
r = client.get("/bangumi/400602/episodes")
test("episodes 200", r.status_code == 200, r.text[:120])
eps = r.json().get("data", [])
test("episodes 非空", len(eps) > 0)
test("episodes 字段", all(k in eps[0] for k in ("type", "sort", "name", "name_cn", "airdate")))
r = client.get("/bangumi/400602/episodes?type=1")
test("episodes?type=1 200", r.status_code == 200 and isinstance(r.json().get("data"), list))

print("== relations / characters / persons ==")
r = client.get("/bangumi/400602/relations")
d = r.json()
test("relations 200", r.status_code == 200)
test("relations 含 in_library_work_id", "in_library_work_id" in (d.get("data") or [{}])[0])
r = client.get("/bangumi/400602/characters")
d = r.json()
test("characters 200 + actors", r.status_code == 200 and "actors" in (d.get("data") or [{}])[0])
r = client.get("/bangumi/400602/persons")
d = r.json()
test("persons 200 + relation", r.status_code == 200 and "relation" in (d.get("data") or [{}])[0])

print("== calendar / ranking ==")
r = client.get("/bangumi/calendar")
d = r.json()
test("calendar 200 按星期", r.status_code == 200 and isinstance(d.get("data"), list) and "weekday" in (d["data"] or [{}])[0])
r = client.get("/bangumi/ranking?type=2&limit=5")
d = r.json()
test("ranking 200", r.status_code == 200 and len(d.get("data", [])) == 5)

print("== 错误码 ==")
r = client.get("/bangumi/999999999")
test("404 条目不存在", r.status_code == 404 and r.json().get("detail") == "条目不存在", r.text[:100])

print("== 图片代理 ==")
r = client.get("/bangumi/image", params={"url": "https://lain.bgm.tv/pic/cover/l/13/c5/400602_ZI8Y9.jpg"})
test("bgm 图 200", r.status_code == 200 and r.headers.get("content-type", "").startswith("image"), r.text[:80])
r2 = client.get("/bangumi/image", params={"url": "https://lain.bgm.tv/pic/cover/l/13/c5/400602_ZI8Y9.jpg"})
test("图片缓存命中", r2.status_code == 200)
r = client.get("/bangumi/image", params={"url": "https://example.com/evil.jpg"})
test("非 bgm 域名拒绝 400", r.status_code == 400, r.text[:80])

print("== search（v0 POST，既有口径）==")
r = client.get("/bangumi/search", params={"q": "芙莉莲", "type": 2})
d = r.json()
test("search 200", r.status_code == 200 and d.get("total", 0) >= 1)
first = (d.get("results") or [{}])[0]
test("search type 过滤生效", first.get("type") == 2, str(first.get("type")))

print("== stale 回退（单测段，不出网）==")
sys.path.insert(0, "backend")
import os
import tempfile

os.environ.setdefault("LIST_MATE_TEST_DB", "1")
tmpdir = tempfile.mkdtemp()
import importlib

# 用临时库重建最小环境
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

test_engine = create_engine(f"sqlite:///{tmpdir}/t.db")
from app.database import Base

import app.models  # noqa

Base.metadata.create_all(test_engine)
TestSession = sessionmaker(bind=test_engine)
db = TestSession()

from fastapi import HTTPException

import app.bangumi_client as bc

calls = {"n": 0}


def fake_upstream(url, **kw):
    calls["n"] += 1
    if calls["n"] == 1:
        class R:
            status_code = 200

            def json(self):
                return {"v": 1}

        return R()
    raise bc.HTTPException(status_code=502, detail="Bangumi 不可用")


real_get = bc.bangumi_get
bc.bangumi_get = fake_upstream
try:
    data, stale, _ = bc.cached_json(db, "t:1", "http://up/1", ttl_seconds=9999)
    test("单测: 首次取数", data == {"v": 1} and stale is False and calls["n"] == 1)
    data, stale, _ = bc.cached_json(db, "t:1", "http://up/1", ttl_seconds=9999)
    test("单测: TTL 内命中不再出网", data == {"v": 1} and calls["n"] == 1)
    # 手动把 fetched_at 拨旧以过期
    from datetime import datetime, timedelta

    row = bc.cache_get(db, "t:1")
    row.fetched_at = datetime.utcnow() - timedelta(days=2)
    db.commit()
    data, stale, _ = bc.cached_json(db, "t:1", "http://up/1", ttl_seconds=9999)
    test("单测: 过期+上游挂 → 旧缓存+stale", data == {"v": 1} and stale is True and calls["n"] == 2)
    # 无缓存 + 上游 404 → 404
    def fake_404(url, **kw):
        raise HTTPException(status_code=404, detail="条目不存在")

    bc.bangumi_get = fake_404
    try:
        bc.cached_json(db, "t:404", "http://up/404", ttl_seconds=60)
        test("单测: 无缓存404抛出", False)
    except HTTPException as e:
        test("单测: 无缓存404抛出", e.status_code == 404)
finally:
    bc.bangumi_get = real_get

print()
print(f"总计: {results['pass']} 通过, {results['fail']} 失败")
sys.exit(1 if results["fail"] else 0)
