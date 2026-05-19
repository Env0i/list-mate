from __future__ import annotations
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.work import Work
from ..models.game_profile import GameProfile, GameStatus, ProgressType
from ..schemas.game_profile import GameProfileCreate, GameProfileUpdate, GameProfileResponse
from ..utils import record_timeline

router = APIRouter(tags=["game-profiles"])


@router.get("/works/{work_id}/game-profiles", response_model=List[GameProfileResponse])
def list_game_profiles(work_id: int, db: Session = Depends(get_db)):
    work = db.query(Work).get(work_id)
    if not work:
        raise HTTPException(status_code=404, detail="作品不存在")
    return db.query(GameProfile).filter(GameProfile.work_id == work_id).all()


@router.post("/works/{work_id}/game-profiles", response_model=GameProfileResponse, status_code=201)
def create_game_profile(work_id: int, data: GameProfileCreate, db: Session = Depends(get_db)):
    work = db.query(Work).get(work_id)
    if not work:
        raise HTTPException(status_code=404, detail="作品不存在")
    if work.category != "game":
        raise HTTPException(status_code=400, detail="只有游戏作品支持 GameProfile")

    gp = GameProfile(work_id=work_id, **data.model_dump(exclude_unset=True))
    if gp.status is None:
        gp.status = GameStatus.WISH

    # Smart default for progress_type based on config name
    if "progress_type" not in data.model_dump(exclude_unset=True):
        gp.progress_type = _guess_progress_type(gp.name)

    db.add(gp)
    db.flush()
    st_val = gp.status.value if hasattr(gp.status, "value") else gp.status
    record_timeline(db, work_id, "created", game_profile_id=gp.id,
                    new_value={"name": gp.name, "status": st_val})
    db.commit()
    db.refresh(gp)
    return gp


@router.get("/game-profiles/{profile_id}", response_model=GameProfileResponse)
def get_game_profile(profile_id: int, db: Session = Depends(get_db)):
    gp = db.query(GameProfile).get(profile_id)
    if not gp:
        raise HTTPException(status_code=404, detail="GameProfile 不存在")
    return gp


@router.put("/game-profiles/{profile_id}", response_model=GameProfileResponse)
def update_game_profile(profile_id: int, data: GameProfileUpdate, db: Session = Depends(get_db)):
    gp = db.query(GameProfile).get(profile_id)
    if not gp:
        raise HTTPException(status_code=404, detail="GameProfile 不存在")

    update_data = data.model_dump(exclude_unset=True)
    user_set_status = "status" in update_data

    # Record timeline for changed fields
    if "status" in update_data and update_data["status"] != gp.status.value:
        record_timeline(db, gp.work_id, "status_change", game_profile_id=gp.id,
                        old_value=gp.status.value, new_value=update_data["status"])
    if "rating" in update_data and update_data["rating"] != gp.rating:
        record_timeline(db, gp.work_id, "rating_change", game_profile_id=gp.id,
                        old_value=gp.rating, new_value=update_data["rating"])
    if "review" in update_data and update_data["review"] != gp.review:
        record_timeline(db, gp.work_id, "review_change", game_profile_id=gp.id,
                        old_value=gp.review, new_value=update_data["review"])
    if "progress_value" in update_data and update_data["progress_value"] != gp.progress_value:
        record_timeline(db, gp.work_id, "progress_update", game_profile_id=gp.id,
                        old_value=gp.progress_value, new_value=update_data["progress_value"])

    if user_set_status and update_data["status"] != GameStatus.COMPLETED.value:
        update_data["auto_completed"] = False

    for key, value in update_data.items():
        setattr(gp, key, value)

    # 自动完成（仅 percent 类型，>=100 时标记完成）
    if not user_set_status and gp.progress_type == ProgressType.PERCENT:
        if (
            gp.progress_value is not None
            and gp.progress_value >= 100
            and not gp.auto_completed
        ):
            record_timeline(db, gp.work_id, "status_change", game_profile_id=gp.id,
                            old_value=gp.status.value if gp.status else None,
                            new_value=GameStatus.COMPLETED.value)
            gp.status = GameStatus.COMPLETED
            gp.auto_completed = True

    db.commit()
    db.refresh(gp)
    return gp


def _guess_progress_type(name: str) -> ProgressType:
    if any(kw in name for kw in ["二刷", "周目", "二周目"]):
        return ProgressType.COUNT
    if any(kw in name for kw in ["整合包", "模组", "整合"]):
        return ProgressType.PERCENT
    return ProgressType.NONE


@router.delete("/game-profiles/{profile_id}", status_code=204)
def delete_game_profile(profile_id: int, db: Session = Depends(get_db)):
    gp = db.query(GameProfile).get(profile_id)
    if not gp:
        raise HTTPException(status_code=404, detail="GameProfile 不存在")
    db.delete(gp)
    db.commit()
