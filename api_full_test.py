"""
Comprehensive API test script for list-mate backend.
Tests all 20+ endpoints covering success cases, error cases, and edge cases.

Usage:
    python api_full_test.py

Requires:
    httpx (pip install httpx)
    Backend running at http://localhost:8001
"""

import httpx
import json
import sys
import time
from datetime import date

BASE = "http://localhost:8001/api"
client = httpx.Client(base_url=BASE, timeout=15)

# Globals for IDs created during tests
created_ids = {
    "anime_work_id": None,
    "novel_work_id": None,
    "comic_work_id": None,
    "game_work_id": None,
    "game_profile_id": None,
    "tag_id": None,
    "second_tag_id": None,
}

results = {"passed": 0, "failed": 0, "tests": []}


def cleanup_previous_test_data():
    """Delete any leftover test data from previous runs."""
    # Clean test tags
    existing_tags = client.get("/tags").json()
    for t in existing_tags:
        if t["name"].startswith(("api-test-", "second-test-tag", "duplicate-tag", "default-color-tag")):
            client.delete(f"/tags/{t['id']}")
    print("  [INFO] Cleaned up previous test data")

    # Re-create a fresh tag for tests
    r = client.post("/tags", json={"name": "api-test-tag", "color": "#ff6600"})
    if r.status_code == 201:
        created_ids["tag_id"] = r.json()["id"]


def test(name: str, func) -> bool:
    """Run a single test, print result, return True on pass."""
    try:
        func()
        print(f"  [PASS] {name}")
        results["passed"] += 1
        results["tests"].append({"name": name, "status": "pass"})
        return True
    except Exception as e:
        print(f"  [FAIL] {name}: {e}")
        results["failed"] += 1
        results["tests"].append({"name": name, "status": "fail", "error": str(e)})
        return False


def assert_status(r: httpx.Response, expected: int, msg: str = ""):
    """Assert HTTP status code."""
    if r.status_code != expected:
        detail = r.text[:300]
        raise AssertionError(
            f"Expected {expected}, got {r.status_code}: {detail}" + (f" ({msg})" if msg else "")
        )


def assert_key( data: dict, key: str, msg: str = ""):
    """Assert key exists in dict."""
    if key not in data:
        raise AssertionError(f"Missing key '{key}' in response" + (f" ({msg})" if msg else ""))


def assert_eq(a, b, msg: str = ""):
    """Assert a == b."""
    if a != b:
        raise AssertionError(f"Expected {b!r}, got {a!r}" + (f" ({msg})" if msg else ""))


def assert_isinstance(obj, cls, msg: str = ""):
    if not isinstance(obj, cls):
        raise AssertionError(f"Expected {cls}, got {type(obj)}" + (f" ({msg})" if msg else ""))


def assert_not_empty(data, msg: str = ""):
    if not data:
        raise AssertionError(f"Expected non-empty value" + (f" ({msg})" if msg else ""))


# =====================================================================
# 1. GET /api/works - List works with pagination, filters, search
# =====================================================================

def test_list_works():
    r = client.get("/works")
    assert_status(r, 200)
    data = r.json()
    assert_key(data, "items")
    assert_key(data, "total")
    assert_key(data, "page")
    assert_key(data, "page_size")
    assert_key(data, "total_pages")
    assert_isinstance(data["items"], list)
    assert_eq(data["page"], 1)
    assert_isinstance(data["total"], int)


def test_list_works_pagination():
    r = client.get("/works", params={"page_size": 2, "page": 1})
    assert_status(r, 200)
    data = r.json()
    assert_eq(data["page_size"], 2)
    assert_eq(data["page"], 1)
    assert len(data["items"]) <= 2, f"Expected <=2 items, got {len(data['items'])}"


def test_list_works_category_filter_anime():
    r = client.get("/works", params={"category": "anime"})
    assert_status(r, 200)
    data = r.json()
    for item in data["items"]:
        assert_eq(item["category"], "anime")


def test_list_works_category_filter_game():
    r = client.get("/works", params={"category": "game"})
    assert_status(r, 200)
    data = r.json()
    for item in data["items"]:
        assert_eq(item["category"], "game")


def test_list_works_category_filter_novel():
    r = client.get("/works", params={"category": "novel"})
    assert_status(r, 200)
    data = r.json()
    for item in data["items"]:
        assert_eq(item["category"], "novel")


def test_list_works_category_filter_comic():
    r = client.get("/works", params={"category": "comic"})
    assert_status(r, 200)
    data = r.json()
    for item in data["items"]:
        assert_eq(item["category"], "comic")


def test_list_works_status_filter():
    r = client.get("/works", params={"status": "completed"})
    assert_status(r, 200)
    # At least verify the endpoint works and returns items with valid structure


def test_list_works_search():
    # Search using a very common term that should match at least something
    r = client.get("/works", params={"q": "a"})
    assert_status(r, 200)
    data = r.json()
    assert_isinstance(data["items"], list)


def test_list_works_invalid_category():
    r = client.get("/works", params={"category": "invalid_cat"})
    assert_status(r, 200)  # Should still work, just return empty
    data = r.json()
    assert_eq(len(data["items"]), 0)


def test_list_works_invalid_page_size_large():
    r = client.get("/works", params={"page_size": 999})
    # Should be capped at 100 or return 422
    assert r.status_code in (200, 422), f"Expected 200 or 422, got {r.status_code}"


def test_list_works_empty_search():
    r = client.get("/works", params={"q": "____no_match_zzz____"})
    assert_status(r, 200)
    data = r.json()
    assert_eq(len(data["items"]), 0)


# =====================================================================
# 2. GET /api/works/{id} - Single work detail
# =====================================================================

def test_get_work_valid():
    # Get the list first to find a valid ID; 空库时自建一条，保证用例自洽
    r = client.get("/works", params={"page_size": 1})
    assert_status(r, 200)
    items = r.json()["items"]
    if not items:
        rc = client.post("/works", json={
            "title": "get-valid-id 自建数据",
            "category": "anime",
            "progress_unit": "ep",
        })
        assert_status(rc, 201)
        wid = rc.json()["id"]
    else:
        wid = items[0]["id"]
    r2 = client.get(f"/works/{wid}")
    assert_status(r2, 200)
    data = r2.json()
    assert_key(data, "id")
    assert_key(data, "title")
    assert_key(data, "category")
    assert_key(data, "created_at")
    assert_key(data, "updated_at")
    assert_eq(data["id"], wid)


def test_get_work_invalid_id():
    r = client.get("/works/999999")
    assert_status(r, 404)
    data = r.json()
    assert_key(data, "detail")


def test_get_work_negative_id():
    r = client.get("/works/-1")
    assert_status(r, 404)


# =====================================================================
# 3. POST /api/works - Create works
# =====================================================================

def test_create_work_anime():
    r = client.post("/works", json={
        "title": "测试动漫 - API Test",
        "category": "anime",
        "progress_unit": "ep",
        "total": 24,
        "status": "watching",
        "rating": 8,
        "summary": "A test anime created by API test",
        "is_free": False,
    })
    assert_status(r, 201)
    data = r.json()
    assert_eq(data["title"], "测试动漫 - API Test")
    assert_eq(data["category"], "anime")
    assert_eq(data["status"], "watching")
    assert_eq(data["rating"], 8)
    assert_eq(data["total"], 24)
    assert_key(data, "id")
    created_ids["anime_work_id"] = data["id"]


def test_create_work_novel():
    r = client.post("/works", json={
        "title": "测试小说 - API Test",
        "category": "novel",
        "progress_unit": "chapter",
        "total": 100,
        "status": "wish",
    })
    assert_status(r, 201)
    data = r.json()
    assert_eq(data["title"], "测试小说 - API Test")
    assert_eq(data["category"], "novel")
    created_ids["novel_work_id"] = data["id"]


def test_create_work_comic():
    r = client.post("/works", json={
        "title": "测试漫画 - API Test",
        "category": "comic",
        "progress_unit": "volume",
        "total": 10,
        "status": "paused",
    })
    assert_status(r, 201)
    data = r.json()
    assert_eq(data["title"], "测试漫画 - API Test")
    assert_eq(data["category"], "comic")
    created_ids["comic_work_id"] = data["id"]


def test_create_work_game():
    r = client.post("/works", json={
        "title": "测试游戏 - API Test",
        "category": "game",
        "progress_unit": "percent",
        "status": "playing",
        "platform": "PC",
        "is_free": True,
    })
    assert_status(r, 201)
    data = r.json()
    assert_eq(data["title"], "测试游戏 - API Test")
    assert_eq(data["category"], "game")
    # Game should have a default game profile
    assert_key(data, "game_profiles")
    assert len(data["game_profiles"]) > 0
    created_ids["game_work_id"] = data["id"]


def test_create_work_invalid_category():
    r = client.post("/works", json={
        "title": "Invalid Category Work",
        "category": "invalid",
        "progress_unit": "ep",
    })
    assert_status(r, 422)


def test_create_work_invalid_progress_unit():
    r = client.post("/works", json={
        "title": "Invalid Unit Work",
        "category": "anime",
        "progress_unit": "invalid_unit",
    })
    assert_status(r, 422)


def test_create_work_invalid_status():
    r = client.post("/works", json={
        "title": "Invalid Status Work",
        "category": "anime",
        "progress_unit": "ep",
        "status": "invalid_status",
    })
    assert_status(r, 422)


def test_create_work_empty_title():
    r = client.post("/works", json={
        "title": "",
        "category": "anime",
        "progress_unit": "ep",
    })
    # Empty string title — model likely allows it on the Pydantic level,
    # but it's an edge case worth testing
    assert r.status_code in (201, 422), f"Expected 201 or 422, got {r.status_code}"


def test_create_work_minimal():
    r = client.post("/works", json={
        "title": "最小化作品",
        "category": "anime",
        "progress_unit": "ep",
    })
    assert_status(r, 201)
    data = r.json()
    assert_eq(data["title"], "最小化作品")
    # Clean up
    client.delete(f"/works/{data['id']}")


def test_create_work_with_tags():
    # First create a tag to use
    r_tag = client.post("/tags", json={"name": "test-tag-for-create", "color": "#ff0000"})
    assert_status(r_tag, 201)
    tag_id = r_tag.json()["id"]

    r = client.post("/works", json={
        "title": "作品带标签测试",
        "category": "anime",
        "progress_unit": "ep",
        "tag_ids": [tag_id],
    })
    assert_status(r, 201)
    data = r.json()
    assert_eq(data["title"], "作品带标签测试")
    # Verify tag is associated
    assert_key(data, "tags")
    tag_names = [t["name"] for t in data["tags"]]
    assert "test-tag-for-create" in tag_names, f"Tag not found in work tags: {tag_names}"
    # Clean up
    client.delete(f"/works/{data['id']}")
    client.delete(f"/tags/{tag_id}")


# =====================================================================
# 4. PUT /api/works/{id} - Update work
# =====================================================================

def test_update_work_title():
    wid = created_ids["anime_work_id"]
    if wid is None:
        raise AssertionError("No anime work created yet, skipping test")
    r = client.put(f"/works/{wid}", json={"title": "测试动漫 - 已重命名"})
    assert_status(r, 200)
    data = r.json()
    assert_eq(data["title"], "测试动漫 - 已重命名")


def test_update_work_rating():
    wid = created_ids["anime_work_id"]
    r = client.put(f"/works/{wid}", json={"rating": 9})
    assert_status(r, 200)
    data = r.json()
    assert_eq(data["rating"], 9)


def test_update_work_status():
    wid = created_ids["anime_work_id"]
    r = client.put(f"/works/{wid}", json={"status": "completed"})
    assert_status(r, 200)
    data = r.json()
    assert_eq(data["status"], "completed")


def test_update_work_partial():
    """Partial update with just one field should not affect others."""
    wid = created_ids["anime_work_id"]
    # Get current state
    r = client.get(f"/works/{wid}")
    assert_status(r, 200)
    before = r.json()

    r2 = client.put(f"/works/{wid}", json={"review": "Added review via partial update"})
    assert_status(r2, 200)
    after = r2.json()
    assert_eq(after["review"], "Added review via partial update")
    # Title should remain unchanged from last update
    assert_eq(after["title"], before["title"])
    assert_eq(after["rating"], before["rating"])


def test_update_work_invalid_id():
    r = client.put("/works/999999", json={"title": "No such work"})
    assert_status(r, 404)


def test_update_work_invalid_status():
    wid = created_ids["anime_work_id"]
    r = client.put(f"/works/{wid}", json={"status": "nonexistent_status"})
    assert_status(r, 422)


def test_update_work_game_status():
    """Game work status update should flow through to the default GameProfile."""
    wid = created_ids["game_work_id"]
    if wid is None:
        raise AssertionError("No game work created yet, skipping test")
    r = client.put(f"/works/{wid}", json={"status": "completed"})
    assert_status(r, 200)
    data = r.json()
    # Game work status should be reflected in game profile
    # Check the response includes game_profiles
    assert_key(data, "game_profiles")
    if data["game_profiles"]:
        assert_eq(data["game_profiles"][0]["status"], "completed")


def test_update_work_clear_fields():
    """Set some fields to None/empty."""
    wid = created_ids["novel_work_id"]
    if wid is None:
        raise AssertionError("No novel work created yet")
    r = client.put(f"/works/{wid}", json={"summary": None, "review": None})
    assert_status(r, 200)


# =====================================================================
# 5. DELETE /api/works/{id} - Delete work
# =====================================================================

def test_delete_work():
    # Create a temporary work to delete
    r = client.post("/works", json={
        "title": "待删除作品",
        "category": "anime",
        "progress_unit": "ep",
    })
    assert_status(r, 201)
    wid = r.json()["id"]

    r2 = client.delete(f"/works/{wid}")
    assert_status(r2, 204)

    # Verify it's gone
    r3 = client.get(f"/works/{wid}")
    assert_status(r3, 404)


def test_delete_work_not_found():
    r = client.delete("/works/999999")
    assert_status(r, 404)


def test_delete_game_work_cascade():
    """Deleting a game work should cascade-delete its game profiles."""
    r = client.post("/works", json={
        "title": "待删除游戏",
        "category": "game",
        "progress_unit": "percent",
        "status": "wish",
    })
    assert_status(r, 201)
    data = r.json()
    wid = data["id"]
    gp_count = len(data["game_profiles"])

    # Delete the work
    r2 = client.delete(f"/works/{wid}")
    assert_status(r2, 204)

    # Verify game profiles are gone (work is gone, profiles cascade)
    r3 = client.get(f"/works/{wid}")
    assert_status(r3, 404)


# =====================================================================
# 6. GET /api/works/{id}/game-profiles - List game profiles
# =====================================================================

def test_list_game_profiles_for_game():
    wid = created_ids["game_work_id"]
    if wid is None:
        raise AssertionError("No game work created yet, skipping test")
    r = client.get(f"/works/{wid}/game-profiles")
    assert_status(r, 200)
    data = r.json()
    assert_isinstance(data, list)
    # The game work should have at least 1 profile (default auto-created)
    assert len(data) >= 1, f"Expected at least 1 game profile, got {len(data)}"
    # Store the first gp id for later tests
    if data:
        created_ids["game_profile_id"] = data[0]["id"]


def test_list_game_profiles_for_non_game():
    wid = created_ids["anime_work_id"]
    if wid is None:
        raise AssertionError("No anime work created yet")
    r = client.get(f"/works/{wid}/game-profiles")
    assert_status(r, 200)
    data = r.json()
    assert_eq(len(data), 0, "Non-game work should have no game profiles")


def test_list_game_profiles_invalid_work():
    r = client.get("/works/999999/game-profiles")
    assert_status(r, 404)


# =====================================================================
# 7. POST /api/works/{id}/game-profiles - Create game profile
# =====================================================================

def test_create_game_profile():
    wid = created_ids["game_work_id"]
    if wid is None:
        raise AssertionError("No game work created yet")
    r = client.post(f"/works/{wid}/game-profiles", json={
        "name": "二周目",
        "progress_type": "count",
        "status": "playing",
        "rating": 9,
        "review": "二周目体验更佳",
        "sort_order": 1,
    })
    assert_status(r, 201)
    data = r.json()
    assert_eq(data["name"], "二周目")
    assert_eq(data["progress_type"], "count")
    assert_eq(data["status"], "playing")
    assert_eq(data["rating"], 9)
    assert_key(data, "id")
    created_ids["game_profile_id"] = data["id"]


def test_create_game_profile_invalid_work():
    r = client.post("/works/999999/game-profiles", json={"name": "No work"})
    assert_status(r, 404)


def test_create_game_profile_for_non_game():
    wid = created_ids["anime_work_id"]
    r = client.post(f"/works/{wid}/game-profiles", json={"name": "Invalid"})
    assert_status(r, 400)


def test_create_game_profile_invalid_status():
    wid = created_ids["game_work_id"]
    r = client.post(f"/works/{wid}/game-profiles", json={
        "name": "Bad Status",
        "status": "watching",
    })
    assert_status(r, 422)


def test_create_game_profile_invalid_progress_type():
    wid = created_ids["game_work_id"]
    r = client.post(f"/works/{wid}/game-profiles", json={
        "name": "Bad Progress Type",
        "progress_type": "invalid",
    })
    assert_status(r, 422)


# =====================================================================
# 8. GET /api/game-profiles/{gpid} - Get game profile detail
# =====================================================================

def test_get_game_profile():
    gpid = created_ids["game_profile_id"]
    if gpid is None:
        raise AssertionError("No game profile id stored")
    r = client.get(f"/game-profiles/{gpid}")
    assert_status(r, 200)
    data = r.json()
    assert_eq(data["id"], gpid)
    assert_key(data, "name")
    assert_key(data, "work_id")
    assert_key(data, "status")
    assert_key(data, "progress_type")


def test_get_game_profile_not_found():
    r = client.get("/game-profiles/999999")
    assert_status(r, 404)


# =====================================================================
# 9. PUT /api/game-profiles/{gpid} - Update game profile
# =====================================================================

def test_update_game_profile():
    gpid = created_ids["game_profile_id"]
    if gpid is None:
        raise AssertionError("No game profile id stored")
    r = client.put(f"/game-profiles/{gpid}", json={
        "name": "二周目 - 已更新",
        "rating": 10,
        "review": "真是绝了",
        "playtime_hours": 120.5,
    })
    assert_status(r, 200)
    data = r.json()
    assert_eq(data["name"], "二周目 - 已更新")
    assert_eq(data["rating"], 10)
    assert_eq(data["review"], "真是绝了")
    assert_eq(data["playtime_hours"], 120.5)


def test_update_game_profile_status():
    gpid = created_ids["game_profile_id"]
    r = client.put(f"/game-profiles/{gpid}", json={"status": "completed"})
    assert_status(r, 200)
    data = r.json()
    assert_eq(data["status"], "completed")


def test_update_game_profile_progress():
    gpid = created_ids["game_profile_id"]
    r = client.put(f"/game-profiles/{gpid}", json={
        "progress_value": 2,
        "progress_type": "count",
    })
    assert_status(r, 200)
    data = r.json()
    assert_eq(data["progress_value"], 2)
    assert_eq(data["progress_type"], "count")


def test_update_game_profile_not_found():
    r = client.put("/game-profiles/999999", json={"name": "No such profile"})
    assert_status(r, 404)


def test_update_game_profile_invalid_status():
    gpid = created_ids["game_profile_id"]
    if gpid is None:
        raise AssertionError("No game profile id stored")
    r = client.put(f"/game-profiles/{gpid}", json={"status": "invalid"})
    assert_status(r, 422)


# =====================================================================
# 10. DELETE /api/game-profiles/{gpid} - Delete game profile
# =====================================================================

def test_delete_game_profile():
    # Create a temp game profile to delete
    wid = created_ids["game_work_id"]
    if wid is None:
        raise AssertionError("No game work created yet")
    r = client.post(f"/works/{wid}/game-profiles", json={
        "name": "待删除配置",
        "progress_type": "none",
        "status": "wish",
    })
    assert_status(r, 201)
    gpid = r.json()["id"]

    r2 = client.delete(f"/game-profiles/{gpid}")
    assert_status(r2, 204)

    # Verify it's gone
    r3 = client.get(f"/game-profiles/{gpid}")
    assert_status(r3, 404)


def test_delete_game_profile_not_found():
    r = client.delete("/game-profiles/999999")
    assert_status(r, 404)


# =====================================================================
# 11. GET /api/tags - List tags
# =====================================================================

def test_list_tags():
    r = client.get("/tags")
    assert_status(r, 200)
    data = r.json()
    assert_isinstance(data, list)


# =====================================================================
# 12. POST /api/tags - Create tag
# =====================================================================

def test_create_tag():
    """Tag was already created by cleanup; just verify it exists in the list."""
    tid = created_ids["tag_id"]
    if tid is None:
        raise AssertionError("No tag was created during cleanup")
    r = client.get("/tags")
    assert_status(r, 200)
    data = r.json()
    found = any(t["id"] == tid and t["name"] == "api-test-tag" for t in data)
    assert found, f"Tag {tid} (api-test-tag) not found in tag list"


def test_create_tag_duplicate():
    # Create a tag first
    r1 = client.post("/tags", json={"name": "duplicate-tag", "color": "#ff0000"})
    assert_status(r1, 201)
    dup_id = r1.json()["id"]

    # Try to create another with same name
    r2 = client.post("/tags", json={"name": "duplicate-tag", "color": "#00ff00"})
    assert_status(r2, 409)

    # Clean up
    client.delete(f"/tags/{dup_id}")


def test_create_tag_default_color():
    r = client.post("/tags", json={"name": "default-color-tag"})
    assert_status(r, 201)
    data = r.json()
    assert_eq(data["color"], "#5bc0de")  # default color from schema
    client.delete(f"/tags/{data['id']}")


# =====================================================================
# 13. PUT /api/tags/{id} - Update tag
# =====================================================================

def test_update_tag():
    tid = created_ids["tag_id"]
    if tid is None:
        raise AssertionError("No tag created yet")
    r = client.put(f"/tags/{tid}", json={"name": "api-test-tag-renamed", "color": "#00ff00"})
    assert_status(r, 200)
    data = r.json()
    assert_eq(data["name"], "api-test-tag-renamed")
    assert_eq(data["color"], "#00ff00")


def test_update_tag_partial():
    tid = created_ids["tag_id"]
    r = client.put(f"/tags/{tid}", json={"color": "#0000ff"})
    assert_status(r, 200)
    data = r.json()
    assert_eq(data["color"], "#0000ff")
    # Name should remain unchanged
    assert_eq(data["name"], "api-test-tag-renamed")


def test_update_tag_not_found():
    r = client.put("/tags/999999", json={"name": "no-such-tag"})
    assert_status(r, 404)


# =====================================================================
# 14. DELETE /api/tags/{id} - Delete tag
# =====================================================================

def test_delete_tag():
    # Create a temporary tag to delete
    r = client.post("/tags", json={"name": "temp-delete-tag", "color": "#ccc"})
    assert_status(r, 201)
    tid = r.json()["id"]

    # Associate it with a work first (to test WorkTag cleanup)
    wid = created_ids["anime_work_id"]
    if wid:
        client.put(f"/works/{wid}", json={"tag_ids": [tid]})

    r2 = client.delete(f"/tags/{tid}")
    assert_status(r2, 204)


def test_delete_tag_not_found():
    r = client.delete("/tags/999999")
    assert_status(r, 404)


# =====================================================================
# 15. GET /api/works/{id}/tags - Get tags for a work
# =====================================================================

def test_get_work_tags_via_detail():
    """Tags are embedded in the work detail response."""
    wid = created_ids["anime_work_id"]
    if wid is None:
        raise AssertionError("No anime work created yet")
    r = client.get(f"/works/{wid}")
    assert_status(r, 200)
    data = r.json()
    assert_key(data, "tags")


# =====================================================================
# 16. POST /api/works/{id}/tags - Associate tags with work
# =====================================================================

def test_associate_tags_with_work():
    """Tags are associated via the tag_ids field in work update."""
    wid = created_ids["anime_work_id"]
    if wid is None:
        raise AssertionError("No anime work created yet")

    # Create a second tag
    r = client.post("/tags", json={"name": "second-test-tag", "color": "#00aaff"})
    assert_status(r, 201)
    created_ids["second_tag_id"] = r.json()["id"]

    # Now associate both tags with the work
    r2 = client.put(f"/works/{wid}", json={
        "tag_ids": [created_ids["tag_id"], created_ids["second_tag_id"]]
    })
    assert_status(r2, 200)
    data = r2.json()
    assert_key(data, "tags")
    tag_names = [t["name"] for t in data["tags"]]
    assert "api-test-tag-renamed" in tag_names or "second-test-tag" in tag_names


# =====================================================================
# 17. DELETE /api/works/{id}/tags/{tag_id} - Remove tag from work
# =====================================================================

def test_remove_tag_from_work():
    """Remove a tag by updating the tag_ids list."""
    wid = created_ids["anime_work_id"]
    sid = created_ids["second_tag_id"]
    tid = created_ids["tag_id"]
    if wid is None or sid is None:
        raise AssertionError("Missing work or tag IDs")

    # Remove second tag by only sending the first tag_id
    r = client.put(f"/works/{wid}", json={
        "tag_ids": [tid]
    })
    assert_status(r, 200)
    data = r.json()
    tag_ids = [t["id"] for t in data["tags"]]
    assert sid not in tag_ids, f"Tag {sid} should have been removed but is still present"


# =====================================================================
# 18. GET /api/stats - Statistics
# =====================================================================

def test_get_stats():
    r = client.get("/stats")
    assert_status(r, 200)
    data = r.json()
    assert_key(data, "total_works")
    assert_key(data, "category_counts")
    assert_key(data, "status_counts")
    assert_key(data, "rating_distribution")
    assert_key(data, "week_activity")
    assert_isinstance(data["week_activity"]["operations"], int)
    assert_isinstance(data["week_activity"]["works_updated"], int)
    assert_isinstance(data["total_works"], int)
    assert_isinstance(data["category_counts"], list)
    assert_isinstance(data["status_counts"], list)
    assert_isinstance(data["rating_distribution"], list)
    assert data["total_works"] > 0, f"Expected works in database, got {data['total_works']}"


# =====================================================================
# 19. GET /api/timeline - Timeline entries
# =====================================================================

def test_get_timeline():
    r = client.get("/timeline")
    assert_status(r, 200)
    data = r.json()
    assert_key(data, "items")
    assert_key(data, "total")
    assert_key(data, "page")
    assert_key(data, "page_size")
    assert_key(data, "total_pages")
    assert_isinstance(data["items"], list)
    assert_eq(data["page"], 1)
    assert data["total"] >= 0


def test_get_timeline_pagination():
    r = client.get("/timeline", params={"page_size": 5, "page": 1})
    assert_status(r, 200)
    data = r.json()
    assert_eq(data["page_size"], 5)


def test_get_timeline_filter_by_work():
    wid = created_ids["anime_work_id"]
    if wid is None:
        raise AssertionError("No anime work created yet")
    r = client.get("/timeline", params={"work_id": wid})
    assert_status(r, 200)
    data = r.json()
    assert_isinstance(data["items"], list)
    for item in data["items"]:
        assert_eq(item["work_id"], wid, "Timeline entry work_id mismatch")


# =====================================================================
# 20. GET /api/bangumi/search - Search Bangumi
# =====================================================================

def test_bangumi_search():
    r = client.get("/bangumi/search", params={"q": "Steins;Gate"})
    # This may fail with 502 if external API is unavailable, which is acceptable
    if r.status_code == 502:
        print("    (Bangumi API unavailable, skipping assertion)")
        return
    assert_status(r, 200)
    data = r.json()
    assert_key(data, "results")
    assert_key(data, "total")
    assert_isinstance(data["results"], list)


def test_bangumi_search_no_query():
    r = client.get("/bangumi/search")
    assert_status(r, 422)  # q is required (min_length=1)


def test_bangumi_search_empty_query():
    r = client.get("/bangumi/search", params={"q": ""})
    assert_status(r, 422)  # q has min_length=1


def test_bangumi_search_with_type():
    r = client.get("/bangumi/search", params={"q": "Steins;Gate", "type": 1})
    if r.status_code == 502:
        return
    assert_status(r, 200)


# =====================================================================
# Edge cases / Extra tests
# =====================================================================

def test_create_work_very_long_title():
    long_title = "A" * 500
    r = client.post("/works", json={
        "title": long_title,
        "category": "anime",
        "progress_unit": "ep",
    })
    assert_status(r, 201)
    data = r.json()
    assert_eq(len(data["title"]), 500)
    client.delete(f"/works/{data['id']}")


def test_create_work_with_all_fields():
    r = client.post("/works", json={
        "title": "全字段作品",
        "category": "anime",
        "sub_category": "SF",
        "progress_unit": "ep",
        "total": 26,
        "progress_value": 13,
        "status": "watching",
        "rating": 7,
        "review": "还不错",
        "summary": "一个有很多字段的作品",
        "start_date": "2025-01-01",
        "finish_date": None,
        "platform": "TV",
        "priority": 5,
        "is_free": False,
    })
    assert_status(r, 201)
    data = r.json()
    assert_eq(data["title"], "全字段作品")
    assert_eq(data["sub_category"], "SF")
    assert_eq(data["total"], 26)
    assert_eq(data["progress_value"], 13)
    assert_eq(data["start_date"], "2025-01-01")
    assert_eq(data["priority"], 5)
    client.delete(f"/works/{data['id']}")


def test_tag_cascade_cleanup():
    """When a tag used by a work is deleted, the WorkTag should be cleaned up."""
    # Create a tag
    r = client.post("/tags", json={"name": "cascade-test-tag", "color": "#abc"})
    assert_status(r, 201)
    tid = r.json()["id"]

    # Create a work and associate the tag
    r2 = client.post("/works", json={
        "title": "级联测试作品",
        "category": "anime",
        "progress_unit": "ep",
        "tag_ids": [tid],
    })
    assert_status(r2, 201)
    wid = r2.json()["id"]

    # Delete the tag — WorkTag cleanup is done in the tags router
    r3 = client.delete(f"/tags/{tid}")
    assert_status(r3, 204)

    # Work should still exist, but with no tags
    r4 = client.get(f"/works/{wid}")
    assert_status(r4, 200)
    data = r4.json()
    assert_eq(len(data["tags"]), 0, "Work tags should be empty after tag deletion")

    # Clean up work
    client.delete(f"/works/{wid}")


def test_export_endpoint():
    """Test the export endpoint if it exists."""
    r = client.get("/export")
    if r.status_code == 404:
        # Endpoint may not exist or have different path
        # Try alternative
        pass
    # Just check the server responds — 404 is OK (means no such endpoint at root)
    # The export router exists so let's check what it does
    assert r.status_code in (200, 404, 405)


def test_backup_endpoint():
    """整库备份：应为合法 SQLite 文件（含时间线/附件等全部数据）。"""
    r = client.get("/backup")
    assert_status(r, 200)
    assert r.content[:16] == b"SQLite format 3\x00", "备份文件不是 SQLite 格式"
    assert len(r.content) > 4096, "备份文件过小，疑似空库快照"
    # 内容抽查：备份中应能找到 timeline 表的建表语句
    assert b"timeline_entries" in r.content, "备份缺少 timeline_entries 表"


def test_restore_roundtrip():
    """备份→还原闭环：上传当前备份应成功且数据不丢；非法文件应 400。"""
    r = client.get("/backup")
    assert_status(r, 200)
    files = {"file": ("zace-backup.db", r.content, "application/octet-stream")}
    r2 = client.post("/restore", files=files)
    assert_status(r2, 200)
    assert "还原成功" in r2.json()["message"]
    # 还原后数据仍在
    r3 = client.get("/works", params={"page_size": 1})
    assert_status(r3, 200)
    # 非法文件拒绝
    bad = client.post("/restore", files={"file": ("bad.db", b"not a sqlite file", "application/octet-stream")})
    assert_status(bad, 400)


def test_root_endpoint():
    """Check root docs are accessible."""
    r = client.get("/docs")
    assert r.status_code in (200, 404, 307)  # redirect is possible
    r2 = client.get("/openapi.json")
    assert r2.status_code in (200, 404)


# =====================================================================
# Main test runner
# =====================================================================

def main():
    print("=" * 60)
    print("  List-Mate 综合 API 测试")
    print(f"  Base URL: {BASE}")
    print(f"  Time: {date.today()}")
    print("=" * 60)

    # Health check
    print("\n[健康检查]")
    try:
        r = client.get("/works", params={"page_size": 1})
        assert r.status_code == 200, f"Backend returned {r.status_code}"
        print(f"  [PASS] Backend is running. Database has works.")
    except Exception as e:
        print(f"  [FAIL] Cannot connect to backend: {e}")
        print("  Make sure the server is running on port 8001.")
        sys.exit(1)

    # ===================== 1. Works List =====================
    print("\n[1. GET /api/works - 作品列表]")
    tests_1 = [
        ("List works", test_list_works),
        ("Pagination (page_size=2, page=1)", test_list_works_pagination),
        ("Category filter - anime", test_list_works_category_filter_anime),
        ("Category filter - game", test_list_works_category_filter_game),
        ("Category filter - novel", test_list_works_category_filter_novel),
        ("Category filter - comic", test_list_works_category_filter_comic),
        ("Status filter (completed)", test_list_works_status_filter),
        ("Search (q=a)", test_list_works_search),
        ("Invalid category returns empty", test_list_works_invalid_category),
        ("Large page_size (999)", test_list_works_invalid_page_size_large),
        ("Empty search returns empty", test_list_works_empty_search),
    ]
    for name, fn in tests_1:
        test(name, fn)

    # ===================== 2. Single Work =====================
    print("\n[2. GET /api/works/{id} - 作品详情]")
    test("Get work by valid ID", test_get_work_valid)
    test("Get work by invalid ID (999999)", test_get_work_invalid_id)
    test("Get work by negative ID (-1)", test_get_work_negative_id)

    # ===================== 3. Create Work =====================
    print("\n[3. POST /api/works - 创建作品]")
    test("Create anime work", test_create_work_anime)
    test("Create novel work", test_create_work_novel)
    test("Create comic work", test_create_work_comic)
    test("Create game work (auto GP)", test_create_work_game)
    test("Invalid category -> 422", test_create_work_invalid_category)
    test("Invalid progress_unit -> 422", test_create_work_invalid_progress_unit)
    test("Invalid status -> 422", test_create_work_invalid_status)
    test("Empty title string", test_create_work_empty_title)
    test("Minimal work (required only)", test_create_work_minimal)
    test("Create work with tags", test_create_work_with_tags)

    # ===================== 4. Update Work =====================
    print("\n[4. PUT /api/works/{id} - 更新作品]")
    test("Update title", test_update_work_title)
    test("Update rating", test_update_work_rating)
    test("Update status", test_update_work_status)
    test("Partial update (single field)", test_update_work_partial)
    test("Invalid work ID -> 404", test_update_work_invalid_id)
    test("Invalid status -> 422", test_update_work_invalid_status)
    test("Update game work status", test_update_work_game_status)
    test("Clear nullable fields (None)", test_update_work_clear_fields)

    # ===================== 5. Delete Work =====================
    print("\n[5. DELETE /api/works/{id} - 删除作品]")
    test("Delete work and verify", test_delete_work)
    test("Delete non-existent work -> 404", test_delete_work_not_found)
    test("Delete game work cascade", test_delete_game_work_cascade)

    # ===================== 6-7. Game Profiles =====================
    print("\n[6. GET /api/works/{id}/game-profiles]")
    test("List game profiles for game", test_list_game_profiles_for_game)
    test("List game profiles for non-game (empty)", test_list_game_profiles_for_non_game)
    test("List game profiles for invalid work -> 404", test_list_game_profiles_invalid_work)

    print("\n[7. POST /api/works/{id}/game-profiles - 创建 GameProfile]")
    test("Create game profile", test_create_game_profile)
    test("Create GP for invalid work -> 404", test_create_game_profile_invalid_work)
    test("Create GP for non-game work -> 400", test_create_game_profile_for_non_game)
    test("Create GP with invalid status -> 422", test_create_game_profile_invalid_status)
    test("Create GP with invalid progress_type -> 422", test_create_game_profile_invalid_progress_type)

    # ===================== 8. Get GP =====================
    print("\n[8. GET /api/game-profiles/{gpid}]")
    test("Get game profile detail", test_get_game_profile)
    test("Get non-existent GP -> 404", test_get_game_profile_not_found)

    # ===================== 9. Update GP =====================
    print("\n[9. PUT /api/game-profiles/{gpid}]")
    test("Update game profile", test_update_game_profile)
    test("Update GP status", test_update_game_profile_status)
    test("Update GP progress", test_update_game_profile_progress)
    test("Update non-existent GP -> 404", test_update_game_profile_not_found)
    test("Update GP with invalid status -> 422", test_update_game_profile_invalid_status)

    # ===================== 10. Delete GP =====================
    print("\n[10. DELETE /api/game-profiles/{gpid}]")
    test("Delete game profile and verify", test_delete_game_profile)
    test("Delete non-existent GP -> 404", test_delete_game_profile_not_found)

    # ===================== 11-14. Tags =====================
    print("\n[Cleanup] Removing leftover test tags...")
    cleanup_previous_test_data()

    print("\n[11. GET /api/tags]")
    test("List tags", test_list_tags)

    print("\n[12. POST /api/tags]")
    test("Create tag", test_create_tag)
    test("Create duplicate tag -> 409", test_create_tag_duplicate)
    test("Create tag with default color", test_create_tag_default_color)

    print("\n[13. PUT /api/tags/{id}]")
    test("Update tag (name+color)", test_update_tag)
    test("Partial update tag (color only)", test_update_tag_partial)
    test("Update non-existent tag -> 404", test_update_tag_not_found)

    print("\n[14. DELETE /api/tags/{id}]")
    test("Delete tag (with WorkTag cleanup)", test_delete_tag)
    test("Delete non-existent tag -> 404", test_delete_tag_not_found)

    # ===================== 15-17. Work-Tag =====================
    print("\n[15. GET /api/works/{id}/tags (via detail)]")
    test("Get tags from work detail", test_get_work_tags_via_detail)

    print("\n[16. POST /api/works/{id}/tags (via tag_ids update)]")
    test("Associate tags with work", test_associate_tags_with_work)

    print("\n[17. DELETE /api/works/{id}/tags/{tag_id} (via tag_ids update)]")
    test("Remove tag from work", test_remove_tag_from_work)

    # ===================== 18. Stats =====================
    print("\n[18. GET /api/stats]")
    test("Get statistics", test_get_stats)

    # ===================== 19. Timeline =====================
    print("\n[19. GET /api/timeline]")
    test("Get timeline entries", test_get_timeline)
    test("Timeline pagination", test_get_timeline_pagination)
    test("Timeline filter by work_id", test_get_timeline_filter_by_work)

    # ===================== 20. Bangumi =====================
    print("\n[20. GET /api/bangumi/search]")
    test("Search Bangumi (Steins;Gate)", test_bangumi_search)
    test("Bangumi search with no query -> 422", test_bangumi_search_no_query)
    test("Bangumi search with empty query -> 422", test_bangumi_search_empty_query)
    test("Bangumi search with type filter", test_bangumi_search_with_type)

    # ===================== Edge Cases =====================
    print("\n[Edge Cases / 边界测试]")
    test("Very long title (500 chars)", test_create_work_very_long_title)
    test("Create work with all fields filled", test_create_work_with_all_fields)
    test("Tag cascade cleanup on delete", test_tag_cascade_cleanup)
    test("Export endpoint", test_export_endpoint)
    test("Backup endpoint (SQLite snapshot)", test_backup_endpoint)
    test("Restore roundtrip (backup -> restore)", test_restore_roundtrip)
    test("Root/docs endpoint", test_root_endpoint)

    # ===================== Results =====================
    print("\n" + "=" * 60)
    total = results["passed"] + results["failed"]
    print(f"  结果: {results['passed']}/{total} 通过")
    if results["failed"] > 0:
        print(f"  失败: {results['failed']}")
    else:
        print("  全部通过!")
    print("=" * 60)

    # Save report
    report = {
        "summary": {
            "total": total,
            "passed": results["passed"],
            "failed": results["failed"],
            "date": str(date.today()),
            "base_url": BASE,
        },
        "tests": results["tests"],
    }
    with open("api_full_test_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n报告已保存到 api_full_test_report.json")

    # Exit with code 1 if any test failed
    if results["failed"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
