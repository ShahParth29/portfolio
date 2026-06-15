import os
import shutil
import time
from typing import List, Optional, Dict

from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_admin
from app.models.models import Video
from app.schemas.schemas import VideoCreate, VideoUpdate, VideoOut, MessageResponse

router = APIRouter(prefix="/api/videos", tags=["Videos"])

UPLOAD_DIR = os.path.join("frontend", "uploads")
VIDEOS_DIR = os.path.join(UPLOAD_DIR, "videos")
THUMBNAILS_DIR = os.path.join(UPLOAD_DIR, "thumbnails")

os.makedirs(VIDEOS_DIR, exist_ok=True)
os.makedirs(THUMBNAILS_DIR, exist_ok=True)


@router.post("/upload", response_model=Dict[str, str])
def upload_file(
    file: UploadFile = File(...),
    admin: dict = Depends(get_current_admin),
):
    # Determine directory based on file extension
    ext = os.path.splitext(file.filename)[1].lower()
    is_video = ext in [".mp4", ".mov", ".avi", ".mkv", ".webm"]
    is_image = ext in [".jpg", ".jpeg", ".png", ".webp", ".gif"]

    if not is_video and not is_image:
        raise HTTPException(status_code=400, detail="Unsupported file format")

    target_dir = VIDEOS_DIR if is_video else THUMBNAILS_DIR
    filename = f"{int(time.time())}_{os.path.basename(file.filename)}"
    filepath = os.path.join(target_dir, filename)

    try:
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {exc}")

    relative_path = f"/uploads/{'videos' if is_video else 'thumbnails'}/{filename}"
    return {"url": relative_path}



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
