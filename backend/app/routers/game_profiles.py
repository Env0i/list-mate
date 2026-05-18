from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.work import Work
from ..models.game_profile import GameProfile, GameStatus
from ..schemas.game_profile import GameProfileCreate, GameProfileUpdate, GameProfileResponse

router = APIRouter(tags=["game-profiles"])


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

    db.add(gp)
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

    if user_set_status and update_data["status"] != GameStatus.COMPLETED.value:
        update_data["auto_completed"] = False

    for key, value in update_data.items():
        setattr(gp, key, value)

    # 自动完成
    if not user_set_status:
        work = db.query(Work).get(gp.work_id)
        if (
            work and work.total and work.total > 0
            and gp.progress_value is not None
            and gp.progress_value >= work.total
            and not gp.auto_completed
        ):
            gp.status = GameStatus.COMPLETED
            gp.auto_completed = True

    db.commit()
    db.refresh(gp)
    return gp


@router.delete("/game-profiles/{profile_id}", status_code=204)
def delete_game_profile(profile_id: int, db: Session = Depends(get_db)):
    gp = db.query(GameProfile).get(profile_id)
    if not gp:
        raise HTTPException(status_code=404, detail="GameProfile 不存在")
    db.delete(gp)
    db.commit()
