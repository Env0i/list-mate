"""
Comprehensive API test script for list-mate.
Tests all 25 API endpoints across all routers.
"""
import json
import sys
import time
from pathlib import Path

import httpx

BASE = "http://localhost:8001/api"
client = httpx.Client(base_url=BASE, timeout=15)

# Use a unique prefix to avoid conflicts with existing data
TS = str(int(time.time()))[-4:]

results = {"pass": 0, "fail": 0, "tests": []}

created_work_ids = []
created_game_profile_id = None
created_attachment_ids = []
created_tag_ids = []
game_work_id = None


def test(name, method, path, expect=None, **kwargs):
    """Run a single test case.
    expect: optional expected status code (e.g. 409, 404) — won't count as failure.
    """
    global created_work_ids, created_game_profile_id, created_attachment_ids, created_tag_ids, game_work_id

    try:
        fn = getattr(client, method)
        resp = fn(path, **kwargs)

        if expect:
            ok = resp.status_code == expect
        else:
            ok = 200 <= resp.status_code < 300

        detail = ""
        if resp.status_code >= 400:
            try:
                detail = resp.json().get("detail", resp.text[:200])
            except Exception:
                detail = resp.text[:200]

        if ok:
            results["pass"] += 1
            label = "PASS"
            icon = "[OK]"
        else:
            results["fail"] += 1
            label = "FAIL"
            icon = "[XX]"

        results["tests"].append({
            "name": name,
            "method": method.upper(),
            "path": path,
            "status_code": resp.status_code,
            "expected": expect,
            "status": label,
            "detail": detail,
        })

        if ok:
            print(f"  {icon} {label} [{resp.status_code}] {method.upper()} {path}")
        else:
            expect_str = f" (expected {expect})" if expect else ""
            print(f"  {icon} {label} [{resp.status_code}]{expect_str} {method.upper()} {path} {detail}")

        return resp
    except Exception as e:
        results["fail"] += 1
        results["tests"].append({
            "name": name,
            "method": method.upper(),
            "path": path,
            "status_code": 0,
            "status": "FAIL",
            "detail": str(e),
        })
        print(f"  [XX] FAIL {method.upper()} {path} -> ERROR: {e}")
        return None


def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


# ============================================================================
# 1. Tags CRUD
# ============================================================================
section("1. Tags CRUD (/api/tags)")

resp = test("List tags", "get", "/tags")
existing_tags = {t["name"]: t["id"] for t in (resp.json() if resp and resp.status_code == 200 else [])}

tag_name1 = f"tag_a_{TS}"
tag_name2 = f"tag_b_{TS}"

resp = test("Create tag #1", "post", "/tags", json={"name": tag_name1, "color": "#00B85A"})
if resp and resp.status_code == 201:
    created_tag_ids.append(resp.json()["id"])
elif resp and resp.status_code == 409 and tag_name1 in existing_tags:
    created_tag_ids.append(existing_tags[tag_name1])

resp = test("Create tag #2", "post", "/tags", json={"name": tag_name2, "color": "#3b82f6"})
if resp and resp.status_code == 201:
    created_tag_ids.append(resp.json()["id"])
elif resp and resp.status_code == 409 and tag_name2 in existing_tags:
    created_tag_ids.append(existing_tags[tag_name2])

# Duplicate → expect 409
resp = test("Create duplicate tag", "post", "/tags", expect=409,
            json={"name": tag_name1, "color": "#FFB800"})

resp = test("List tags", "get", "/tags")

if created_tag_ids:
    resp = test("Update tag", "put", f"/tags/{created_tag_ids[0]}",
                json={"name": f"tag_a_{TS}_updated", "color": "#FF6B6B"})

resp = test("List tags after update", "get", "/tags")

# ============================================================================
# 2. Works CRUD
# ============================================================================
section("2. Works CRUD (/api/works)")

resp = test("List works", "get", "/works")

resp = test("Create work (anime)", "post", "/works", json={
    "title": "测试番剧",
    "category": "anime",
    "progress_unit": "ep",
    "status": "watching",
    "total": 12,
    "progress_value": 3,
    "rating": 8,
    "review": "很不错！",
    "tag_ids": created_tag_ids,
})
if resp and resp.status_code == 201:
    created_work_ids.append(resp.json()["id"])

resp = test("Create work (novel)", "post", "/works", json={
    "title": "测试小说",
    "category": "novel",
    "progress_unit": "chapter",
    "status": "wish",
    "total": 300,
})
if resp and resp.status_code == 201:
    created_work_ids.append(resp.json()["id"])

resp = test("Create work (comic)", "post", "/works", json={
    "title": "测试漫画",
    "category": "comic",
    "progress_unit": "volume",
    "status": "completed",
    "rating": 9,
})
if resp and resp.status_code == 201:
    created_work_ids.append(resp.json()["id"])

resp = test("Create work (game)", "post", "/works", json={
    "title": "测试游戏",
    "category": "game",
    "progress_unit": "percent",
    "status": "playing",
    "purchase_platform": "Steam",
    "purchase_price": 198.0,
})
if resp and resp.status_code == 201:
    game_work_id = resp.json()["id"]
    created_work_ids.append(game_work_id)
    profiles = resp.json().get("game_profiles", [])
    if profiles:
        created_game_profile_id = profiles[0]["id"]

# ============================================================================
# 3. Work Detail / Update / Cover
# ============================================================================
section("3. Work Detail & Update")

anime_work_id = created_work_ids[0] if created_work_ids else None
if anime_work_id:
    resp = test("Get work detail", "get", f"/works/{anime_work_id}")
    if resp:
        assert resp.json()["title"] == "测试番剧"

    resp = test("Update work", "put", f"/works/{anime_work_id}", json={
        "rating": 9,
        "progress_value": 6,
        "review": "越来越好看了！",
    })

    resp = test("Verify update", "get", f"/works/{anime_work_id}")
    if resp:
        assert resp.json()["rating"] == 9
        assert resp.json()["progress_value"] == 6

    # Cover upload
    fake_png = b'\x89PNG\r\n\x1a\n' + b'\x00' * 20
    resp = test("Upload cover", "post", f"/works/{anime_work_id}/cover",
                files={"file": ("cover.png", fake_png, "image/png")})

    resp = test("Get cover", "get", f"/works/{anime_work_id}/cover")

# 404 cases
resp = test("Get cover 404", "get", "/works/99999/cover", expect=404)
resp = test("Upload cover 404", "post", "/works/99999/cover", expect=404,
            files={"file": ("test.png", b"data", "image/png")})
resp = test("Get work 404", "get", "/works/99999", expect=404)
resp = test("Update work 404", "put", "/works/99999", expect=404, json={"title": "nope"})

# ============================================================================
# 4. List Works with Filters
# ============================================================================
section("4. List Works with Filters")

resp = test("List all works", "get", "/works")
if resp:
    assert resp.json()["total"] >= 0  # may have user data

resp = test("Filter by category", "get", "/works", params={"category": "anime"})
if resp:
    assert resp.json()["total"] >= 1

resp = test("Filter by status", "get", "/works", params={"category": "anime", "status": "watching"})
if resp:
    assert resp.json()["total"] >= 1

resp = test("Search by title", "get", "/works", params={"q": "测试"})

resp = test("Pagination", "get", "/works", params={"page": 1, "page_size": 2})
if resp:
    assert len(resp.json()["items"]) <= 2

# ============================================================================
# 5. GameProfile CRUD
# ============================================================================
section("5. GameProfile CRUD")

# Create additional GameProfile
if game_work_id:
    resp = test("Create GameProfile", "post", f"/works/{game_work_id}/game-profiles", json={
        "name": "二刷（纯近战）",
        "status": "playing",
        "progress_value": 30,
        "progress_type": "percent",
        "rating": 7,
        "review": "近战太爽了",
        "start_date": "2026-03-01",
        "notes": "只用近战武器通关",
    })
    if resp and resp.status_code == 201:
        created_game_profile_id = resp.json()["id"]

if created_game_profile_id:
    resp = test("Get GameProfile", "get", f"/game-profiles/{created_game_profile_id}")
    if resp:
        assert resp.json()["name"] in ["二刷（纯近战）", "本体"]

    resp = test("Update GameProfile", "put", f"/game-profiles/{created_game_profile_id}", json={
        "rating": 9,
        "progress_value": 60,
        "review": "越来越熟练了",
        "playtime_hours": 45.5,
    })
    if resp:
        assert resp.json()["rating"] == 9

# Error cases
if anime_work_id:
    resp = test("GP on non-game work", "post", f"/works/{anime_work_id}/game-profiles", expect=400,
                json={"name": "不应该能创建"})

resp = test("GP on 404 work", "post", "/works/99999/game-profiles", expect=404, json={"name": "Test"})
resp = test("Get GP 404", "get", "/game-profiles/99999", expect=404)
resp = test("Update GP 404", "put", "/game-profiles/99999", expect=404, json={"name": "nope"})
resp = test("Delete GP 404", "delete", "/game-profiles/99999", expect=404)

# ============================================================================
# 6. Bangumi API
# ============================================================================
section("6. Bangumi API")

resp = test("Search Bangumi", "get", "/bangumi/search", params={"q": "Steins;Gate", "type": 1})
if resp and resp.status_code == 200:
    print(f"       -> Found {resp.json()['total']} results")

# ============================================================================
# 7. Stats API
# ============================================================================
section("7. Stats API")

resp = test("Get stats", "get", "/stats")
if resp:
    data = resp.json()
    print(f"       -> total_works: {data['total_works']}")
    print(f"       -> categories: {[c['category']+':'+str(c['count']) for c in data['category_counts']]}")
    print(f"       -> statuses: {[s['status']+':'+str(s['count']) for s in data['status_counts']]}")
    print(f"       -> ratings: {[str(r['rating'])+':'+str(r['count']) for r in data['rating_distribution']]}")

# ============================================================================
# 8. Timeline API
# ============================================================================
section("8. Timeline API")

resp = test("List timeline", "get", "/timeline")
if resp:
    print(f"       -> Total entries: {resp.json()['total']}")

resp = test("Timeline pagination", "get", "/timeline", params={"page_size": 5})

if anime_work_id:
    resp = test("Timeline by work", "get", "/timeline", params={"work_id": anime_work_id})

# ============================================================================
# 9. Attachments CRUD
# ============================================================================
section("9. Attachments CRUD")

if created_game_profile_id:
    resp = test("List attachments", "get", f"/game-profiles/{created_game_profile_id}/attachments")

    resp = test("Upload attachment", "post", f"/game-profiles/{created_game_profile_id}/attachments",
                files={"file": ("test.txt", b"Hello World! Test attachment.", "text/plain")},
                data={"label": "测试文件"})
    if resp and resp.status_code == 201:
        created_attachment_ids.append(resp.json()["id"])

    resp = test("Upload attachment #2", "post", f"/game-profiles/{created_game_profile_id}/attachments",
                files={"file": ("data.json", json.dumps({"key": "value"}), "application/json")},
                data={"label": "JSON 数据"})
    if resp and resp.status_code == 201:
        created_attachment_ids.append(resp.json()["id"])

    resp = test("List attachments", "get", f"/game-profiles/{created_game_profile_id}/attachments")
    if resp:
        print(f"       -> {len(resp.json())} attachments")

    if created_attachment_ids:
        resp = test("Download attachment", "get", f"/attachments/{created_attachment_ids[0]}")
        if resp:
            print(f"       -> Content: {resp.text[:50]}...")

    # 404 cases
    resp = test("List attachments 404", "get", "/game-profiles/99999/attachments", expect=404)
    resp = test("Upload attachment 404", "post", "/game-profiles/99999/attachments", expect=404,
                files={"file": ("test.txt", b"data", "text/plain")})
    resp = test("Download attachment 404", "get", "/attachments/99999", expect=404)
    resp = test("Delete attachment 404", "delete", "/attachments/99999", expect=404)

# ============================================================================
# 10. Data Export
# ============================================================================
section("10. Data Export")

resp = test("Export JSON", "get", "/export/json")
if resp:
    try:
        exported = json.loads(resp.text)
        print(f"       -> {len(exported)} works exported")
    except json.JSONDecodeError:
        print(f"       -> Response is {len(resp.content)} bytes (raw)")

resp = test("Export CSV", "get", "/export/csv")
if resp:
    lines = resp.text.strip().split("\n")
    print(f"       -> {len(lines)} lines (1 header + {len(lines)-1} data)")

# ============================================================================
# 11. Cleanup: Delete resources
# ============================================================================
section("11. Cleanup (Delete)")

for aid in created_attachment_ids:
    resp = test(f"Delete attachment #{aid}", "delete", f"/attachments/{aid}")

for tid in created_tag_ids:
    resp = test(f"Delete tag #{tid}", "delete", f"/tags/{tid}")

for wid in created_work_ids:
    resp = test(f"Delete work #{wid}", "delete", f"/works/{wid}")

# 404 delete cases
resp = test("Delete work 404", "delete", "/works/99999", expect=404)
resp = test("Delete tag 404", "delete", "/tags/99999", expect=404)

# ============================================================================
# Summary
# ============================================================================
section("SUMMARY")
total = results["pass"] + results["fail"]
print(f"  Total tests: {total}")
print(f"  Passed:      {results['pass']}")
print(f"  Failed:      {results['fail']}")
print(f"  Pass rate:   {results['pass']/total*100:.1f}%")

if results["fail"] > 0:
    print(f"\n  Failed tests:")
    for t in results["tests"]:
        if t["status"] == "FAIL":
            print(f"    - [{t['method']} {t['path']}] ({t.get('status_code','?')}) {t['name']}")
            if t.get("detail"):
                print(f"      Detail: {t['detail']}")

report_path = Path("d:/Develop/Project/github/list-mate/api_test_report.json")
report_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n  Report saved to: {report_path}")

sys.exit(0 if results["fail"] == 0 else 1)
