from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, EmailStr


# ── Video ──────────────────────────────────────────────────────────────────────

class VideoBase(BaseModel):
    title: str
    youtube_url: Optional[str] = None
    video_file_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    category: str = "cinematic"
    description: str = ""
    is_featured: bool = False
    sort_order: int = 0


class VideoCreate(VideoBase):
    pass


class VideoUpdate(VideoBase):
    pass


class VideoOut(VideoBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ── Client Enquiry ─────────────────────────────────────────────────────────────

class EnquiryCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str = ""
    project_type: str
    budget_range: str = ""
    event_date: str = ""
    message: str
    website: Optional[str] = None  # Honeypot field for spam protection


class EnquiryOut(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    project_type: str
    budget_range: str
    event_date: str
    message: str
    is_read: bool
    received_at: datetime

    class Config:
        from_attributes = True


# ── Blog ───────────────────────────────────────────────────────────────────────

class BlogPostBase(BaseModel):
    title: str
    slug: str
    content: str = ""
    cover_image_url: str = ""
    category: str = "tips"
    is_published: bool = False


class BlogPostCreate(BlogPostBase):
    pass


class BlogPostUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    content: Optional[str] = None
    cover_image_url: Optional[str] = None
    category: Optional[str] = None
    is_published: Optional[bool] = None


class BlogPostOut(BlogPostBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ── Pricing ────────────────────────────────────────────────────────────────────

class PricingPlanBase(BaseModel):
    name: str
    price: float
    original_price: Optional[float] = None
    features: str = ""
    is_popular: bool = False
    is_active: bool = True


class PricingPlanCreate(PricingPlanBase):
    pass


class PricingPlanUpdate(PricingPlanBase):
    pass


class PricingPlanOut(PricingPlanBase):
    id: int

    class Config:
        from_attributes = True


# ── Site Settings ──────────────────────────────────────────────────────────────

class SiteSettingsOut(BaseModel):
    """All site settings as a flat dict."""
    settings: Dict[str, str]


class SiteSettingsUpdate(BaseModel):
    """Partial update — only send keys you want to change."""
    settings: Dict[str, str]


# ── Auth ───────────────────────────────────────────────────────────────────────

class TokenRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ── Generic ────────────────────────────────────────────────────────────────────

class MessageResponse(BaseModel):
    message: str
