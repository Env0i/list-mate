"""
修复：清除游戏作品的 Work.status 字段
游戏的状态应由 GameProfile 管理
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.work import Work, Category

db = SessionLocal()
games = db.query(Work).filter(Work.category == Category.GAME, Work.status.isnot(None)).all()
for w in games:
    print(f"  清空 {w.title} 的 status ({w.status.value})")
    w.status = None
db.commit()
db.close()
print(f"已修复 {len(games)} 个游戏作品")
