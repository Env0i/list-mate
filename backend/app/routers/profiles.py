from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.work import Work
from ..models.profile import Profile, ProfileStatus
from ..schemas.profile import ProfileCreate, ProfileUpdate, ProfileResponse

router = APIRouter(tags=["profiles"])


@router.post("/works/{work_id}/profiles", response_model=ProfileResponse, status_code=201)
def create_profile(work_id: int, data: ProfileCreate, db: Session = Depends(get_db)):
    work = db.query(Work).get(work_id)
    if not work:
        raise HTTPException(status_code=404, detail="作品不存在")

    profile = Profile(work_id=work_id, **data.model_dump(exclude_unset=True))
    if profile.status is None:
        profile.status = ProfileStatus.WISH

    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/profiles/{profile_id}", response_model=ProfileResponse)
def get_profile(profile_id: int, db: Session = Depends(get_db)):
    profile = db.query(Profile).get(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile 不存在")
    return profile


@router.put("/profiles/{profile_id}", response_model=ProfileResponse)
def update_profile(profile_id: int, data: ProfileUpdate, db: Session = Depends(get_db)):
    profile = db.query(Profile).get(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile 不存在")

    update_data = data.model_dump(exclude_unset=True)
    user_set_status = "status" in update_data

    # If user explicitly changes status away from completed, clear auto flag
    if user_set_status and update_data["status"] != ProfileStatus.COMPLETED.value:
        update_data["auto_completed"] = False

    for key, value in update_data.items():
        setattr(profile, key, value)

    # Auto-complete: only when user didn't explicitly set status
    if not user_set_status:
        work = db.query(Work).get(profile.work_id)
        if (
            work and work.total and work.total > 0
            and profile.progress_value is not None
            and profile.progress_value >= work.total
            and not profile.auto_completed
        ):
            profile.status = ProfileStatus.COMPLETED
            profile.auto_completed = True

    db.commit()
    db.refresh(profile)
    return profile


@router.delete("/profiles/{profile_id}", status_code=204)
def delete_profile(profile_id: int, db: Session = Depends(get_db)):
    profile = db.query(Profile).get(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile 不存在")
    db.delete(profile)
    db.commit()
