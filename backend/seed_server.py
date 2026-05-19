"""
服务器种子数据脚本
用法: python seed_server.py
  1. 插入示例作品数据
  2. 搜索 Bangumi 补全封面和数据
"""
import sys, os, json, httpx
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, init_db
from app.models.work import Work, Category, ProgressUnit, WorkStatus
from app.models.game_profile import GameProfile, GameStatus, ProgressType

BANGUMI_HEADERS = {"User-Agent": "list-mate/1.0 (personal project)"}

TITLE_MAP = {
    "我的世界": "Minecraft", "英雄联盟": "League of Legends",
    "艾尔登法环": "艾尔登法环", "极乐迪斯科": "极乐迪斯科",
    "葬送的芙莉莲": "葬送的芙莉莲", "命运石之门": "命运石之门",
    "进击的巨人": "进击的巨人", "无畏契约": "无畏契约",
}
TYPE_MAP = {"anime": 1, "comic": 2, "game": 3, "novel": 5}


def seed_data():
    init_db()
    db = SessionLocal()

    existing = db.query(Work).count()
    if existing > 1:
        print(f"数据库已有 {existing} 条记录，跳过插入")
        db.close()
        return

    works = [
        Work(title="我的世界", category=Category.GAME, sub_category="沙盒",
             progress_unit=ProgressUnit.PERCENT, summary="Minecraft，一款沙盒建造游戏。",
             platform="PC", purchase_price=165.0, playtime_hours=500, priority=5),
        Work(title="英雄联盟", category=Category.GAME, sub_category="MOBA",
             progress_unit=ProgressUnit.PERCENT, summary="全球最受欢迎的 MOBA 游戏之一。",
             platform="wegame", priority=4),
        Work(title="艾尔登法环", category=Category.GAME, sub_category="ARPG",
             progress_unit=ProgressUnit.PERCENT, summary="宫崎英高与乔治·R·R·马丁合作的开放世界动作RPG。",
             platform="steam", purchase_price=298.0, playtime_hours=120, priority=5),
        Work(title="极乐迪斯科", category=Category.GAME, sub_category="CRPG",
             progress_unit=ProgressUnit.PERCENT, summary="一款开创性的侦探 RPG。",
             platform="steam", purchase_price=69.0, playtime_hours=40, priority=3),
        Work(title="葬送的芙莉莲", category=Category.ANIME, sub_category="奇幻",
             progress_unit=ProgressUnit.EP, total=28, progress_value=28,
             status=WorkStatus.COMPLETED, summary="勇者小队击败魔王后的故事。",
             platform="bilibili", priority=5, rating=10, review="年度最佳。"),
        Work(title="命运石之门", category=Category.NOVEL, sub_category="科幻",
             progress_unit=ProgressUnit.CHAPTER, total=12, progress_value=12,
             status=WorkStatus.COMPLETED, summary="时间旅行 ADV 系列巅峰之作。",
             platform="steam", priority=5, rating=10, review="El. Psy. Congroo."),
        Work(title="进击的巨人", category=Category.COMIC, sub_category="奇幻",
             progress_unit=ProgressUnit.VOLUME, total=34, progress_value=34,
             status=WorkStatus.COMPLETED, summary="人类与巨人的战斗。",
             priority=4, rating=9),
    ]

    for w in works:
        db.add(w)
    db.flush()

    profiles = [
        GameProfile(work_id=works[0].id, name="纯净生存", status=GameStatus.COMPLETED,
            progress_type=ProgressType.COUNT, progress_value=3, playtime_hours=300),
        GameProfile(work_id=works[0].id, name="模组整合包", status=GameStatus.PLAYING,
            progress_type=ProgressType.PERCENT, progress_value=35, source="CurseForge",
            notes="GTNH 养老整合包"),
        GameProfile(work_id=works[1].id, name="本体", status=GameStatus.PLAYING,
            progress_type=ProgressType.NONE, playtime_hours=800),
        GameProfile(work_id=works[2].id, name="一周目", status=GameStatus.COMPLETED,
            progress_type=ProgressType.COUNT, progress_value=1, playtime_hours=120,
            rating=10, review="魂系巅峰。"),
        GameProfile(work_id=works[2].id, name="二刷（纯近战）", status=GameStatus.PLAYING,
            progress_type=ProgressType.PERCENT, progress_value=60, playtime_hours=50),
        GameProfile(work_id=works[3].id, name="本体", status=GameStatus.WISH,
            progress_type=ProgressType.NONE),
    ]
    for p in profiles:
        db.add(p)

    db.commit()
    db.close()
    print(f"已插入 {len(works)} 个作品 + {len(profiles)} 个游戏配置")


def fetch_covers():
    db = SessionLocal()
    works = db.query(Work).filter(Work.cover_data.is_(None)).all()
    total = len(works)
    if total == 0:
        print("所有作品已有封面，无需补抓")
        db.close()
        return

    print(f"找到 {total} 个无封面的作品")
    for i, w in enumerate(works, 1):
        keyword = TITLE_MAP.get(w.title, w.title)
        cat_type = TYPE_MAP.get(w.category)
        print(f"[{i}/{total}] {w.title} → 搜索 '{keyword}'...")

        body = {"keyword": keyword}
        if cat_type:
            body["type"] = cat_type
        try:
            resp = httpx.post("https://api.bgm.tv/v0/search/subjects", json=body,
                              headers=BANGUMI_HEADERS, timeout=10)
            resp.raise_for_status()
        except Exception as e:
            print(f"  搜索失败: {e}")
            continue

        items = resp.json().get("data", [])
        if not items:
            print("  无搜索结果")
            continue

        hit = items[0]
        bid = hit["id"]
        image_url = hit.get("images", {}).get("medium")
        name_cn = hit.get("name_cn", "") or hit.get("name", "")

        try:
            detail = httpx.get(f"https://api.bgm.tv/v0/subjects/{bid}",
                               headers=BANGUMI_HEADERS, timeout=10)
            detail.raise_for_status()
            detail_data = detail.json()
        except Exception:
            detail_data = hit

        bangumi_data = {
            "id": bid, "name": hit.get("name", ""), "name_cn": name_cn,
            "summary": hit.get("summary", ""), "image_url": image_url,
            "date": detail_data.get("date", ""), "platform": detail_data.get("platform", ""),
            "score": detail_data.get("rating", {}).get("score", 0),
            "infobox": detail_data.get("infobox", []),
            "tags": [t.get("name", "") for t in (detail_data.get("tags") or [])],
        }

        cover_data = None
        if image_url:
            try:
                img_resp = httpx.get(image_url, timeout=10)
                if img_resp.status_code == 200:
                    cover_data = img_resp.content
                    print(f"  封面已下载 ({len(cover_data)} bytes)")
            except Exception:
                pass

        w.bangumi_id = bid
        w.bangumi_data = json.dumps(bangumi_data, ensure_ascii=False)
        if cover_data:
            w.cover_data = cover_data
            w.cover_url = image_url
        w.summary = w.summary or hit.get("summary", "")
        db.flush()
        print(f"  ✓ {w.title} → Bangumi #{bid}")

    db.commit()
    db.close()
    print(f"封面同步完成！")


if __name__ == "__main__":
    seed_data()
    fetch_covers()
