import os
from typing import List, Optional, Dict

from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_admin
from app.core.storage import upload_file_to_storage
from app.models.models import Video
from app.schemas.schemas import VideoCreate, VideoUpdate, VideoOut, MessageResponse

from app.core.config import get_settings

router = APIRouter(prefix="/api/videos", tags=["Videos"])

settings = get_settings()

# Ensure local upload dirs exist (used when STORAGE_BACKEND=local)
UPLOAD_DIR = settings.UPLOAD_DIR
VIDEOS_DIR = os.path.join(UPLOAD_DIR, "videos")
THUMBNAILS_DIR = os.path.join(UPLOAD_DIR, "thumbnails")

os.makedirs(VIDEOS_DIR, exist_ok=True)
os.makedirs(THUMBNAILS_DIR, exist_ok=True)


@router.post("/upload", response_model=Dict[str, str])
def upload_file(
    file: UploadFile = File(...),
    admin: dict = Depends(get_current_admin),
):
    """Upload a video or image file. Uses Cloudinary or local storage based on config."""
    try:
        url = upload_file_to_storage(file.file, file.filename)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {exc}")

    return {"url": url}



@router.get("/", response_model=List[VideoOut])
def get_videos(category: Optional[str] = Query(None), db: Session = Depends(get_db)):
    query = db.query(Video)
    if category:
        query = query.filter(Video.category == category)
    return query.order_by(Video.sort_order, Video.created_at.desc()).all()


@router.get("/featured", response_model=List[VideoOut])
def get_featured_videos(db: Session = Depends(get_db)):
    return (
        db.query(Video)
        .filter(Video.is_featured == True)
        .order_by(Video.sort_order)
        .limit(6)
        .all()
    )


@router.post("/", response_model=VideoOut, status_code=status.HTTP_201_CREATED)
def create_video(
    data: VideoCreate,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    video = Video(**data.model_dump())
    video.generate_thumbnail()
    db.add(video)
    db.commit()
    db.refresh(video)
    return video


@router.put("/{video_id}", response_model=VideoOut)
def update_video(
    video_id: int,
    data: VideoUpdate,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    for key, value in data.model_dump().items():
        setattr(video, key, value)
    video.generate_thumbnail()
    db.commit()
    db.refresh(video)
    return video


@router.delete("/{video_id}", response_model=MessageResponse)
def delete_video(
    video_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    db.delete(video)
    db.commit()
    return {"message": "Video deleted"}
