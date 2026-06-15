import re
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float
from app.core.database import Base


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    youtube_url = Column(String(500), nullable=True)
    video_file_url = Column(String(500), nullable=True)
    thumbnail_url = Column(String(500), nullable=True)
    category = Column(String(50), nullable=False, default="cinematic")  # cinematic / reels / wedding
    description = Column(Text, nullable=True, default="")
    is_featured = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    @staticmethod
    def extract_youtube_id(url: str) -> str:
        """Extract YouTube video ID from various URL formats."""
        if not url:
            return ""
        patterns = [
            r'(?:youtube\.com\/watch\?v=)([a-zA-Z0-9_-]{11})',
            r'(?:youtu\.be\/)([a-zA-Z0-9_-]{11})',
            r'(?:youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
            r'(?:youtube\.com\/shorts\/)([a-zA-Z0-9_-]{11})',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return ""

    def generate_thumbnail(self):
        """Auto-generate thumbnail URL from YouTube video ID if no custom thumbnail is provided."""
        if not self.youtube_url:
            return
        if not self.thumbnail_url or self.thumbnail_url.startswith("https://img.youtube.com/"):
            vid = self.extract_youtube_id(self.youtube_url)
            if vid:
                self.thumbnail_url = f"https://img.youtube.com/vi/{vid}/maxresdefault.jpg"


class ClientEnquiry(Base):
    __tablename__ = "client_enquiries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False)
    phone = Column(String(20), nullable=True, default="")
    project_type = Column(String(100), nullable=False)
    budget_range = Column(String(100), nullable=True, default="")
    event_date = Column(String(50), nullable=True, default="")
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    received_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class BlogPost(Base):
    __tablename__ = "blog_posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300), nullable=False)
    slug = Column(String(300), unique=True, nullable=False, index=True)
    content = Column(Text, nullable=False, default="")
    cover_image_url = Column(String(500), nullable=True, default="")
    category = Column(String(100), nullable=True, default="tips")
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))


class PricingPlan(Base):
    __tablename__ = "pricing_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    original_price = Column(Float, nullable=True)
    features = Column(Text, nullable=False, default="")  # comma-separated
    is_popular = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)


class SiteSettings(Base):
    """Key-value store for site-wide configuration."""
    __tablename__ = "site_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=False, default="")
