from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import Response
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.game_profile import GameProfile
from ..models.attachment import Attachment
from ..schemas.attachment import AttachmentResponse, AttachmentUploadResponse

router = APIRouter(tags=["attachments"])


@router.post("/game-profiles/{gpid}/attachments", response_model=AttachmentUploadResponse, status_code=201)
def upload_attachment(
    gpid: int,
    file: UploadFile = File(...),
    label: str = Form(""),
    db: Session = Depends(get_db),
):
    gp = db.query(GameProfile).get(gpid)
    if not gp:
        raise HTTPException(status_code=404, detail="GameProfile 不存在")

    data = file.file.read()
    att = Attachment(
        game_profile_id=gpid,
        label=label,
        file_name=file.filename or "unnamed",
        file_type=file.content_type or "application/octet-stream",
        file_data=data,
    )
    db.add(att)
    db.commit()
    db.refresh(att)
    return AttachmentUploadResponse(
        id=att.id,
        label=att.label,
        file_name=att.file_name,
        file_size=len(data),
    )


@router.get("/game-profiles/{gpid}/attachments", response_model=list[AttachmentResponse])
def list_attachments(gpid: int, db: Session = Depends(get_db)):
    gp = db.query(GameProfile).get(gpid)
    if not gp:
        raise HTTPException(status_code=404, detail="GameProfile 不存在")

    attachments = db.query(Attachment).filter(Attachment.game_profile_id == gpid).all()
    return [
        AttachmentResponse(
            id=a.id,
            game_profile_id=a.game_profile_id,
            label=a.label,
            file_name=a.file_name,
            file_size=len(a.file_data),
            created_at=a.created_at,
        )
        for a in attachments
    ]


@router.get("/attachments/{attachment_id}")
def download_attachment(attachment_id: int, db: Session = Depends(get_db)):
    att = db.query(Attachment).get(attachment_id)
    if not att:
        raise HTTPException(status_code=404, detail="附件不存在")
    return Response(
        content=att.file_data,
        media_type=att.file_type,
        headers={"Content-Disposition": f'attachment; filename="{att.file_name}"'},
    )


@router.delete("/attachments/{attachment_id}", status_code=204)
def delete_attachment(attachment_id: int, db: Session = Depends(get_db)):
    att = db.query(Attachment).get(attachment_id)
    if not att:
        raise HTTPException(status_code=404, detail="附件不存在")
    db.delete(att)
    db.commit()
