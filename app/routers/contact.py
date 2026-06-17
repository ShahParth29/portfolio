from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
import time
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_admin, create_access_token
from app.core.config import get_settings
from app.core.email import send_email_notification, build_enquiry_email
from app.models.models import ClientEnquiry
from app.schemas.schemas import (
    EnquiryCreate, EnquiryOut, TokenRequest, TokenResponse, MessageResponse,
)

router = APIRouter(prefix="/api/contact", tags=["Contact"])

# In-memory store for rate limiting: IP -> list of floats (timestamps)
login_attempts = {}


@router.post("/", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def submit_enquiry(data: EnquiryCreate, db: Session = Depends(get_db)):
    # Honeypot spam check: if website is filled, discard the submit silently but return success
    if data.website:
        print(f"[SPAM DETECTED] Discarding spam submission from {data.email} with honeypot field filled.")
        return {"message": "Your enquiry has been submitted! We'll get back to you soon."}

    enquiry_data = data.model_dump(exclude={"website"})
    enquiry = ClientEnquiry(**enquiry_data)
    db.add(enquiry)
    db.commit()
    db.refresh(enquiry)

    # Send email notification (non-blocking, won't crash on failure)
    try:
        html_body = build_enquiry_email(
            name=data.name,
            email=data.email,
            phone=data.phone,
            project_type=data.project_type,
            budget_range=data.budget_range,
            event_date=data.event_date,
            message=data.message,
        )
        send_email_notification(
            subject=f"New Enquiry from {data.name} — {data.project_type}",
            body_html=html_body,
        )
    except Exception as exc:
        print(f"[CONTACT] Email notification failed: {exc}")

    return {"message": "Your enquiry has been submitted! We'll get back to you soon."}


# ── Admin Auth ─────────────────────────────────────────────────────────────────

@router.post("/admin/token", response_model=TokenResponse)
def admin_login(data: TokenRequest, request: Request):
    settings = get_settings()
    ip = request.client.host if request.client else "unknown"
    current_time = time.time()

    # Clean up older timestamps for this IP
    if ip not in login_attempts:
        login_attempts[ip] = []
    login_attempts[ip] = [t for t in login_attempts[ip] if current_time - t < 60]

    # Check rate limit
    if len(login_attempts[ip]) >= settings.LOGIN_RATE_LIMIT:
        print(f"[SECURITY] Rate limit exceeded for login attempts from IP: {ip} at {datetime.now(timezone.utc)}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again in a minute.",
        )

    # Log the attempt
    print(f"[SECURITY] Login attempt for user '{data.username}' from IP '{ip}' at {datetime.now(timezone.utc)}")

    if data.username != settings.ADMIN_USERNAME or data.password != settings.ADMIN_PASSWORD:
        login_attempts[ip].append(current_time)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Clear rate limit attempts on successful login
    login_attempts[ip] = []

    token = create_access_token({"sub": data.username})
    return {"access_token": token, "token_type": "bearer"}



# ── Admin Enquiries ────────────────────────────────────────────────────────────

@router.get("/admin/enquiries", response_model=List[EnquiryOut])
def get_enquiries(
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    return db.query(ClientEnquiry).order_by(ClientEnquiry.received_at.desc()).all()


@router.patch("/admin/enquiries/{enquiry_id}/read", response_model=EnquiryOut)
def mark_enquiry_read(
    enquiry_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    enquiry = db.query(ClientEnquiry).filter(ClientEnquiry.id == enquiry_id).first()
    if not enquiry:
        raise HTTPException(status_code=404, detail="Enquiry not found")
    enquiry.is_read = not enquiry.is_read
    db.commit()
    db.refresh(enquiry)
    return enquiry
