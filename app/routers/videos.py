import os
import time
from typing import List, Optional, Dict
import cloudinary.utils

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


@router.get("/signature", response_model=Dict[str, str])
def get_cloudinary_signature(
    admin: dict = Depends(get_current_admin),
):
    """Generate signature for direct frontend upload to Cloudinary."""
    if settings.STORAGE_BACKEND != "cloudinary" or not settings.CLOUDINARY_API_SECRET:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cloudinary storage is not configured",
        )
    
    timestamp = int(time.time())
    folder = "portfolio/uploads"
    params = {
        "timestamp": timestamp,
        "folder": folder
    }
    
    signature = cloudinary.utils.api_sign_request(
        params,
        settings.CLOUDINARY_API_SECRET
    )
    
    return {
        "signature": signature,
        "timestamp": str(timestamp),
        "folder": folder,
        "api_key": settings.CLOUDINARY_API_KEY,
        "cloud_name": settings.CLOUDINARY_CLOUD_NAME
    }


@router.get("/upload-params", response_model=Dict[str, str])
def get_upload_params(
    filename: Optional[str] = Query(None),
    filetype: Optional[str] = Query(None),
    admin: dict = Depends(get_current_admin),
):
    """Get parameters and credentials/signatures for uploading files to the active backend."""
    backend = settings.STORAGE_BACKEND
    
    if backend == "cloudinary":
        if not settings.CLOUDINARY_API_SECRET:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cloudinary storage is not configured",
            )
        timestamp = int(time.time())
        folder = "portfolio/uploads"
        params = {
            "timestamp": timestamp,
            "folder": folder
        }
        signature = cloudinary.utils.api_sign_request(
            params,
            settings.CLOUDINARY_API_SECRET
        )
        return {
            "backend": "cloudinary",
            "signature": signature,
            "timestamp": str(timestamp),
            "folder": folder,
            "api_key": settings.CLOUDINARY_API_KEY,
            "cloud_name": settings.CLOUDINARY_CLOUD_NAME
        }
        
    elif backend == "s3":
        if not all([settings.S3_ACCESS_KEY_ID, settings.S3_SECRET_ACCESS_KEY, settings.S3_BUCKET_NAME]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="S3 storage is not configured",
            )
        if not filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="filename query parameter is required for S3 upload",
            )
            
        import boto3
        from botocore.config import Config
        
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
            endpoint_url=settings.S3_ENDPOINT_URL or None,
            region_name=settings.S3_REGION_NAME or None,
            config=Config(signature_version="s3v4")
        )
        
        from app.core.storage import _detect_file_type
        is_video, is_image = _detect_file_type(filename)
        
        sub_dir = "videos" if is_video else "thumbnails"
        key = f"portfolio/uploads/{sub_dir}/{int(time.time())}_{os.path.basename(filename)}"
        
        if not filetype:
            import mimetypes
            filetype, _ = mimetypes.guess_type(filename)
            if not filetype:
                filetype = "video/mp4" if is_video else "image/png"
                
        try:
            presigned_url = s3_client.generate_presigned_url(
                ClientMethod="put_object",
                Params={
                    "Bucket": settings.S3_BUCKET_NAME,
                    "Key": key,
                    "ContentType": filetype,
                },
                ExpiresIn=3600,
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate presigned S3 URL: {e}"
            )
            
        if settings.S3_PUBLIC_URL:
            public_url = f"{settings.S3_PUBLIC_URL.rstrip('/')}/{key}"
        else:
            region = settings.S3_REGION_NAME or "us-east-1"
            if settings.S3_ENDPOINT_URL:
                public_url = f"{settings.S3_ENDPOINT_URL.rstrip('/')}/{settings.S3_BUCKET_NAME}/{key}"
            else:
                public_url = f"https://{settings.S3_BUCKET_NAME}.s3.{region}.amazonaws.com/{key}"
                
        return {
            "backend": "s3",
            "presigned_url": presigned_url,
            "public_url": public_url,
        }
        
    else:
        return {
            "backend": "local"
        }

