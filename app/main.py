from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.database import Base, engine, SessionLocal
from app.core.config import get_settings
from app.models.models import Video, ClientEnquiry, BlogPost, PricingPlan, SiteSettings
from app.routers import videos, contact, blog, pricing, settings

# ── Create tables ──────────────────────────────────────────────────────────────
Base.metadata.create_all(bind=engine)

settings_cfg = get_settings()

# ── App ────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="NextFrame Studios — Portfolio API",
    description="Backend API for NextFrame Studios video production portfolio",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

# ── Security Headers Middleware ────────────────────────────────────────────────
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

# ── CORS ───────────────────────────────────────────────────────────────────────
origins = ["*"]
if settings_cfg.CORS_ORIGINS != "*":
    origins = [origin.strip() for origin in settings_cfg.CORS_ORIGINS.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────────────────
app.include_router(videos.router)
app.include_router(contact.router)
app.include_router(blog.router)
app.include_router(pricing.router)
app.include_router(settings.router)

@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "NextFrame Studios API"}


# ── Seed Data ──────────────────────────────────────────────────────────────────
def seed_data():
    """Insert sample data on first run so the site is not empty."""
    db = SessionLocal()
    try:
        # Seed Settings if empty
        if db.query(SiteSettings).count() == 0:
            default_settings = {
                "site_name": "NextFrame Studios",
                "tagline": "I turn moments into memories",
                "email": "shahparth29980@gmail.com",
                "phone": "+91 81410 50770",
                "location": "Ahmedabad, Gujarat, India",
                "youtube": "#",
                "instagram": "#",
                "twitter": "#",
                "about_text": "Professional video editor specializing in cinematic films, reels, and wedding videos. Turning your raw footage into visual stories.",
                "about_bio": "I am a passionate video editor with over 3 years of experience in creating stunning visuals. I specialize in color grading, sound design, and motion graphics to deliver cinema-grade videos.",
            }
            for k, v in default_settings.items():
                db.add(SiteSettings(key=k, value=v))
            db.commit()
            print("[SEED] Site settings seeded.")

        # Only seed if the videos table is empty
        if db.query(Video).count() > 0:
            return

        # No sample YouTube videos — only user-uploaded videos will be shown
        # (Seed video section removed to keep site clean)

        # ── Sample Pricing Plans ───────────────────────────────────────────
        db.add_all([
            PricingPlan(
                name="Editing (Up to 3 min)",
                price=2000,
                original_price=3000,
                features="Up to 3 min video,Basic color grading,Cuts & transitions,Royalty-free music,2 revisions,Delivery in 2 days",
                is_popular=False,
            ),
            PricingPlan(
                name="Shoot & Edit (Up to 3 min)",
                price=3000,
                original_price=5000,
                features="Custom video shooting,Full professional editing,Cuts & transitions,Basic color grading,3 revisions,Delivery in 4 days",
                is_popular=False,
            ),
            PricingPlan(
                name="Editing (Up to 10 min)",
                price=4000,
                original_price=6000,
                features="Up to 10 min video,Advanced color grading,Cuts & transitions,Royalty-free music,3 revisions,Delivery in 4 days",
                is_popular=True,
            ),
            PricingPlan(
                name="Shoot & Edit (Up to 10 min)",
                price=5000,
                original_price=8000,
                features="Custom video shooting,Full professional editing,Cinema-grade color grading,Sound design & custom SFX,5 revisions,Delivery in 6 days",
                is_popular=False,
            ),
        ])

        # ── Sample Blog Post ──────────────────────────────────────────────
        db.add(BlogPost(
            title="5 Color Grading Tips for Cinematic Videos",
            slug="5-color-grading-tips",
            content="""## Introduction

Color grading can make or break your video. Here are my top 5 tips that I use on every project.

## 1. Start with a Clean Base

Before applying any creative LUT, make sure your footage is properly **white-balanced** and **exposure-corrected**. This gives you a clean canvas to work with.

## 2. Use Power Windows for Skin Tones

Isolate skin tones using qualifier tools in DaVinci Resolve. This lets you adjust the background mood without affecting how people look on screen.

## 3. Embrace the Teal & Orange Look

The classic cinematic look pairs cool shadows (teal) with warm highlights (orange). It works because it creates natural contrast with skin tones.

## 4. Don't Over-Saturate

Less is more. Pull back on saturation and let the contrast do the heavy lifting. Over-saturated footage looks amateur.

## 5. Match Your Shots

Consistency across shots is more important than any single grade. Use DaVinci Resolve's **Shot Match** feature to maintain a cohesive look.

---

*Happy grading! — NextFrame Studios*
""",
            cover_image_url="https://images.unsplash.com/photo-1574717024653-61fd2cf4d44d?w=800",
            category="tips",
            is_published=True,
        ))

        db.commit()
        print("[SEED] Sample data inserted successfully.")
    except Exception as exc:
        db.rollback()
        print(f"[SEED] Error: {exc}")
    finally:
        db.close()


seed_data()


# ── Serve uploads and frontend (optional, for local dev) ──────────────────────
import os

upload_dir = settings_cfg.UPLOAD_DIR
os.makedirs(upload_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")

frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.isdir(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

