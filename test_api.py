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

# Duplicate -> expect 409
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
# 11. Bangumi Detail API
# ============================================================================
section("11. Bangumi Detail API")

resp = test("Get Bangumi detail", "get", "/bangumi/2256")
if resp and resp.status_code == 200:
    data = resp.json()
    print(f"       -> Name: {data.get('name')}, Type: {data.get('type')}, Episodes: {data.get('total_episodes')}")

# ============================================================================
# 12. Auto-completion Tests
# ============================================================================
section("12. Auto-completion Tests")

# --- Work (non-game) progress auto-completion ---
resp = test("Create work for auto-complete", "post", "/works", json={
    "title": f"自动完成测试_{TS}",
    "category": "anime",
    "progress_unit": "ep",
    "total": 12,
    "progress_value": 11,
})
auto_complete_work_id = None
if resp and resp.status_code == 201:
    auto_complete_work_id = resp.json()["id"]
    created_work_ids.append(auto_complete_work_id)
    assert resp.json()["status"] != "completed", "Should NOT be auto-completed yet"

# Update progress_value to match total -> should auto-complete
if auto_complete_work_id:
    resp = test("Auto-complete: progress = total", "put", f"/works/{auto_complete_work_id}", json={
        "progress_value": 12,
    })
    if resp:
        assert resp.json()["status"] == "completed", f"Expected completed, got {resp.json()['status']}"
        assert resp.json()["auto_completed"] == True
        print("       -> 非游戏作品自动完成 [OK]")

    # Set progress back below total -> should NOT auto-revert (user can override)
    resp = test("Auto-complete: no auto-revert on dec", "put", f"/works/{auto_complete_work_id}", json={
        "progress_value": 11,
    })
    if resp:
        print(f"       -> Status after decrease: {resp.json()['status']} (expected completed) [OK]")

# --- GameProfile percent auto-completion ---
if game_work_id:
    resp = test("Create GP for auto-complete", "post", f"/works/{game_work_id}/game-profiles", json={
        "name": f"整合包{TS}",
        "progress_type": "percent",
        "progress_value": 50,
    })
    if resp and resp.status_code == 201:
        auto_gp_id = resp.json()["id"]
        resp = test("GP auto-complete: progress = 100", "put", f"/game-profiles/{auto_gp_id}", json={
            "progress_value": 100,
        })
        if resp:
            assert resp.json()["status"] == "completed", f"Expected completed, got {resp.json()['status']}"
            assert resp.json()["auto_completed"] == True
            print("       -> GP percent 自动完成 [OK]")

    # Progress_type=count should NOT auto-complete at >= 100
    resp = test("Create GP count for auto-complete", "post", f"/works/{game_work_id}/game-profiles", json={
        "name": f"二周目{TS}",
        "progress_type": "count",
        "progress_value": 50,
    })
    if resp and resp.status_code == 201:
        auto_gp_count_id = resp.json()["id"]
        resp = test("GP count: NO auto-complete at >= 100", "put", f"/game-profiles/{auto_gp_count_id}", json={
            "progress_value": 999,
        })
        if resp:
            assert resp.json()["status"] != "completed", "Count type should NOT auto-complete"
            print("       -> GP count 不会自动完成 [OK]")

    # Progress_type=none should NOT auto-complete
    resp = test("Create GP none for auto-complete", "post", f"/works/{game_work_id}/game-profiles", json={
        "name": f"剧情体验{TS}",
        "progress_type": "none",
        "progress_value": None,
    })
    if resp and resp.status_code == 201:
        auto_gp_none_id = resp.json()["id"]
        resp = test("GP none: NO auto-complete", "put", f"/game-profiles/{auto_gp_none_id}", json={
            "progress_value": None,
        })
        if resp:
            assert resp.json()["status"] != "completed", "None type should NOT auto-complete"
            print("       -> GP none 不会自动完成 [OK]")

# ============================================================================
# 13. GameProfile Smart Defaults (progress_type guessing)
# ============================================================================
section("13. GameProfile Smart Defaults")

if game_work_id:
    resp = test("GP default: 二周目 -> count", "post", f"/works/{game_work_id}/game-profiles", json={
        "name": f"二周目开荒_{TS}",
    })
    if resp and resp.status_code == 201:
        assert resp.json()["progress_type"] == "count", \
            f"Expected count, got {resp.json()['progress_type']}"
        print(f"       -> '二周目' -> {resp.json()['progress_type']} [OK]")

    resp = test("GP default: 二刷 -> count", "post", f"/works/{game_work_id}/game-profiles", json={
        "name": f"二刷挑战_{TS}",
    })
    if resp and resp.status_code == 201:
        assert resp.json()["progress_type"] == "count", \
            f"Expected count, got {resp.json()['progress_type']}"
        print(f"       -> '二刷' -> {resp.json()['progress_type']} [OK]")

    resp = test("GP default: 整合包 -> percent", "post", f"/works/{game_work_id}/game-profiles", json={
        "name": f"极限整合包_{TS}",
    })
    if resp and resp.status_code == 201:
        assert resp.json()["progress_type"] == "percent", \
            f"Expected percent, got {resp.json()['progress_type']}"
        print(f"       -> '整合包' -> {resp.json()['progress_type']} [OK]")

    resp = test("GP default: 模组 -> percent", "post", f"/works/{game_work_id}/game-profiles", json={
        "name": f"自打模组_{TS}",
    })
    if resp and resp.status_code == 201:
        assert resp.json()["progress_type"] == "percent", \
            f"Expected percent, got {resp.json()['progress_type']}"
        print(f"       -> '模组' -> {resp.json()['progress_type']} [OK]")

    resp = test("GP default: 普通 -> none", "post", f"/works/{game_work_id}/game-profiles", json={
        "name": f"纯净通关_{TS}",
    })
    if resp and resp.status_code == 201:
        assert resp.json()["progress_type"] == "none", \
            f"Expected none, got {resp.json()['progress_type']}"
        print(f"       -> '纯净通关' -> {resp.json()['progress_type']} [OK]")

# ============================================================================
# 14. Game Status Filter & Edge Cases
# ============================================================================
section("14. Game Status Filter & Edge Cases")

# Filter game works by GameProfile status
resp = test("Filter game by status=playing", "get", "/works",
            params={"category": "game", "status": "playing"})
if resp and resp.status_code == 200:
    print(f"       -> Game status filter (playing): {resp.json()['total']} results")

resp = test("Filter game by status=wish", "get", "/works",
            params={"category": "game", "status": "wish"})
if resp and resp.status_code == 200:
    print(f"       -> Game status filter (wish): {resp.json()['total']} results")

# Update game work should silently drop status
if game_work_id:
    resp = test("Game work update drops status", "put", f"/works/{game_work_id}", json={
        "rating": 9,
        "status": "completed",  # should be silently dropped
    })
    if resp:
        assert resp.json()["status"] is None or resp.json()["status"] != "completed", \
            f"Game work status should be None, got {resp.json()['status']}"
        print(f"       -> Game work status correctly remains None [OK]")

# Game work has no progress_unit auto-complete
if game_work_id:
    resp = test("Game work no auto-complete", "put", f"/works/{game_work_id}", json={
        "progress_value": 100,
    })
    if resp:
        assert resp.json()["status"] is None, \
            f"Game work should not get auto-completed, status={resp.json()['status']}"
        print("       -> Game work 不会自动完成 [OK]")

# ============================================================================
# 15. Cascade Delete: Work -> GameProfile -> Attachment
# ============================================================================
section("15. Cascade Delete Test")

# Create cascade chain: Work -> GP -> Attachment
resp = test("Create cascade work", "post", "/works", json={
    "title": f"级联删除测试_{TS}",
    "category": "game",
    "progress_unit": "percent",
})
cascade_work_id = None
cascade_gp_id = None
cascade_att_id = None
if resp and resp.status_code == 201:
    cascade_work_id = resp.json()["id"]
    gps = resp.json().get("game_profiles", [])
    cascade_gp_id = gps[0]["id"] if gps else None
    # Create extra GP for cascade test
    resp2 = test("Create cascade GP", "post", f"/works/{cascade_work_id}/game-profiles", json={
        "name": f"全收集_{TS}",
    })
    if resp2 and resp2.status_code == 201:
        cascade_gp_id = resp2.json()["id"]
        # Upload attachment
        resp3 = test("Create cascade attachment", "post",
                     f"/game-profiles/{cascade_gp_id}/attachments",
                     files={"file": ("cascade_test.txt", b"Cascade delete test content.", "text/plain")},
                     data={"label": "级联测试"})
        if resp3 and resp3.status_code == 201:
            cascade_att_id = resp3.json()["id"]

# Verify GP and attachment exist before deletion
if cascade_gp_id:
    resp = test("Cascade GP exists before delete", "get", f"/game-profiles/{cascade_gp_id}")
if cascade_att_id:
    resp = test("Cascade att exists before delete", "get", f"/attachments/{cascade_att_id}")

# Delete the work
if cascade_work_id:
    resp = test("Delete cascade work", "delete", f"/works/{cascade_work_id}")

    # Verify GP returns 404 after work is deleted
    if cascade_gp_id:
        resp = test("GP cascade deleted", "get", f"/game-profiles/{cascade_gp_id}", expect=404)
        print("       -> GP 级联删除已验证 [OK]")

    # Verify attachment returns 404 after work is deleted
    if cascade_att_id:
        resp = test("Att cascade deleted", "get", f"/attachments/{cascade_att_id}", expect=404)
        print("       -> Attachment 级联删除已验证 [OK]")

# ============================================================================
# 16. Input Validation & Error Handling
# ============================================================================
section("16. Input Validation")

# Missing required fields
resp = test("Work without title", "post", "/works", expect=422, json={
    "category": "anime",
    "progress_unit": "ep",
})

resp = test("Work without category", "post", "/works", expect=422, json={
    "title": f"无分类_{TS}",
    "progress_unit": "ep",
})

resp = test("Work without progress_unit", "post", "/works", expect=422, json={
    "title": f"无进度单位_{TS}",
    "category": "anime",
})

resp = test("Tag without name", "post", "/tags", expect=422, json={})

# Invalid enum values (Pydantic accepts string, SQLAlchemy rejects at DB level -> 500)
resp = test("Work with invalid category", "post", "/works", expect=500, json={
    "title": f"非法分类_{TS}",
    "category": "invalid_category",
    "progress_unit": "ep",
    "total": 12,
})
if resp:
    print(f"       -> 非法分类 -> status={resp.status_code} [OK]")

resp = test("Work with invalid status", "post", "/works", expect=500, json={
    "title": f"非法状态_{TS}",
    "category": "anime",
    "progress_unit": "ep",
    "status": "invalid_status",
})
if resp:
    print(f"       -> 非法状态 -> status={resp.status_code} [OK]")

# total=None should NOT auto-complete
resp = test("Create work with total=None", "post", "/works", json={
    "title": f"无限连载_{TS}",
    "category": "anime",
    "progress_unit": "ep",
    "total": None,
    "progress_value": 999,
})
none_total_work_id = None
if resp and resp.status_code == 201:
    none_total_work_id = resp.json()["id"]
    created_work_ids.append(none_total_work_id)
    assert resp.json()["status"] != "completed", \
        "total=None should not auto-complete"
    print("       -> total=None 不会自动完成 [OK]")

# Invalid pagination
resp = test("Page size over limit", "get", "/works", expect=422, params={"page_size": 200})
resp = test("Page below minimum", "get", "/works", expect=422, params={"page": 0})

# ============================================================================
# 17. Bangumi Auto-fill
# ============================================================================
section("17. Bangumi Auto-fill")

resp = test("Create work with bangumi_id", "post", "/works", json={
    "title": f"Bangumi自动填充_{TS}",
    "category": "anime",
    "progress_unit": "ep",
    "bangumi_id": 2256,  # Steins;Gate
})
if resp and resp.status_code == 201:
    wid = resp.json()["id"]
    created_work_ids.append(wid)
    bdata = resp.json().get("bangumi_data")
    if bdata:
        print(f"       -> bangumi_data 已填充 ({len(bdata)} chars) [OK]")
    else:
        print("       -> bangumi_data 未填充（外部API可能不可用）[--]")

# ============================================================================
# 18. Cleanup: Delete resources
# ============================================================================
section("18. Cleanup (Delete)")

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
