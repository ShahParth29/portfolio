from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_admin
from app.models.models import BlogPost
from app.schemas.schemas import (
    BlogPostCreate, BlogPostUpdate, BlogPostOut, MessageResponse,
)

router = APIRouter(prefix="/api/blog", tags=["Blog"])


@router.get("/", response_model=List[BlogPostOut])
def get_published_posts(db: Session = Depends(get_db)):
    return (
        db.query(BlogPost)
        .filter(BlogPost.is_published == True)
        .order_by(BlogPost.created_at.desc())
        .all()
    )


@router.get("/admin/all", response_model=List[BlogPostOut])
def get_all_posts_admin(
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    return (
        db.query(BlogPost)
        .order_by(BlogPost.created_at.desc())
        .all()
    )



@router.get("/{slug}", response_model=BlogPostOut)
def get_post_by_slug(slug: str, db: Session = Depends(get_db)):
    post = db.query(BlogPost).filter(BlogPost.slug == slug).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.post("/", response_model=BlogPostOut, status_code=status.HTTP_201_CREATED)
def create_post(
    data: BlogPostCreate,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    existing = db.query(BlogPost).filter(BlogPost.slug == data.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="A post with this slug already exists")
    post = BlogPost(**data.model_dump())
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


@router.patch("/{post_id}", response_model=BlogPostOut)
def update_post(
    post_id: int,
    data: BlogPostUpdate,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(post, key, value)
    db.commit()
    db.refresh(post)
    return post


@router.delete("/{post_id}", response_model=MessageResponse)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    db.delete(post)
    db.commit()
    return {"message": "Post deleted"}
