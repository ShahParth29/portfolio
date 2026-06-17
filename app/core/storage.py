"""
Storage abstraction — supports local filesystem and Cloudinary.

Usage:
    from app.core.storage import upload_file_to_storage
    result = upload_file_to_storage(file)  # returns {"url": "..."}

When STORAGE_BACKEND=cloudinary, files are uploaded to Cloudinary CDN.
When STORAGE_BACKEND=local (default), files are saved to the local uploads dir.
"""

import os
import shutil
import time

import cloudinary
import cloudinary.uploader

from app.core.config import get_settings

settings = get_settings()

# ── Storage Configuration ──────────────────────────────────────────────────
_cloudinary_configured = False
_s3_configured = False

if settings.STORAGE_BACKEND == "cloudinary":
    if not all([settings.CLOUDINARY_CLOUD_NAME, settings.CLOUDINARY_API_KEY, settings.CLOUDINARY_API_SECRET]):
        raise ValueError(
            "STORAGE_BACKEND is set to 'cloudinary' but CLOUDINARY_CLOUD_NAME, "
            "CLOUDINARY_API_KEY, or CLOUDINARY_API_SECRET is missing. "
            "Set them in your .env file."
        )
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True,
    )
    _cloudinary_configured = True
    print("[STORAGE] Cloudinary configured successfully.")
elif settings.STORAGE_BACKEND == "s3":
    if not all([settings.S3_ACCESS_KEY_ID, settings.S3_SECRET_ACCESS_KEY, settings.S3_BUCKET_NAME]):
        raise ValueError(
            "STORAGE_BACKEND is set to 's3' but S3_ACCESS_KEY_ID, "
            "S3_SECRET_ACCESS_KEY, or S3_BUCKET_NAME is missing. "
            "Set them in your .env file."
        )
    _s3_configured = True
    print("[STORAGE] S3 configured successfully.")
else:
    print("[STORAGE] Using local file storage.")


# ── File type detection ───────────────────────────────────────────────────────

VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


def _detect_file_type(filename: str) -> tuple[bool, bool]:
    """Returns (is_video, is_image) based on file extension."""
    ext = os.path.splitext(filename)[1].lower()
    return ext in VIDEO_EXTENSIONS, ext in IMAGE_EXTENSIONS


# ── Upload Functions ──────────────────────────────────────────────────────────

def _upload_to_cloudinary(file, filename: str) -> str:
    """Upload a file to Cloudinary and return the public URL."""
    is_video, is_image = _detect_file_type(filename)

    if not is_video and not is_image:
        raise ValueError("Unsupported file format")

    resource_type = "video" if is_video else "image"
    folder = "portfolio/videos" if is_video else "portfolio/thumbnails"

    result = cloudinary.uploader.upload(
        file,
        resource_type=resource_type,
        folder=folder,
        public_id=f"{int(time.time())}_{os.path.splitext(filename)[0]}",
        overwrite=True,
    )

    return result["secure_url"]


def _upload_to_s3(file, filename: str) -> str:
    """Upload a file to S3 and return the public URL."""
    is_video, is_image = _detect_file_type(filename)

    if not is_video and not is_image:
        raise ValueError("Unsupported file format")

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

    sub_dir = "videos" if is_video else "thumbnails"
    key = f"portfolio/uploads/{sub_dir}/{int(time.time())}_{os.path.basename(filename)}"
    
    import mimetypes
    content_type, _ = mimetypes.guess_type(filename)
    if not content_type:
        content_type = "video/mp4" if is_video else "image/png"

    s3_client.upload_fileobj(
        file,
        settings.S3_BUCKET_NAME,
        key,
        ExtraArgs={"ContentType": content_type}
    )

    if settings.S3_PUBLIC_URL:
        return f"{settings.S3_PUBLIC_URL.rstrip('/')}/{key}"
    else:
        region = settings.S3_REGION_NAME or "us-east-1"
        if settings.S3_ENDPOINT_URL:
            return f"{settings.S3_ENDPOINT_URL.rstrip('/')}/{settings.S3_BUCKET_NAME}/{key}"
        return f"https://{settings.S3_BUCKET_NAME}.s3.{region}.amazonaws.com/{key}"


def _upload_to_local(file, filename: str) -> str:
    """Save a file to the local uploads directory and return the relative URL."""
    is_video, is_image = _detect_file_type(filename)

    if not is_video and not is_image:
        raise ValueError("Unsupported file format")

    upload_dir = settings.UPLOAD_DIR
    sub_dir = "videos" if is_video else "thumbnails"
    target_dir = os.path.join(upload_dir, sub_dir)
    os.makedirs(target_dir, exist_ok=True)

    safe_filename = f"{int(time.time())}_{os.path.basename(filename)}"
    filepath = os.path.join(target_dir, safe_filename)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file, buffer)

    return f"/uploads/{sub_dir}/{safe_filename}"


def upload_file_to_storage(file, filename: str) -> str:
    """
    Upload a file using the configured storage backend.
    Returns the URL where the file can be accessed.
    """
    if _cloudinary_configured:
        return _upload_to_cloudinary(file, filename)
    elif _s3_configured:
        return _upload_to_s3(file, filename)
    else:
        return _upload_to_local(file, filename)
