from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict

from app.core.database import get_db
from app.core.auth import get_current_admin
from app.models.models import SiteSettings
from app.schemas.schemas import SiteSettingsOut, SiteSettingsUpdate

router = APIRouter(prefix="/api/settings", tags=["Settings"])


@router.get("/", response_model=SiteSettingsOut)
def get_all_settings(db: Session = Depends(get_db)):
    rows = db.query(SiteSettings).all()
    settings_dict = {row.key: row.value for row in rows}
    return {"settings": settings_dict}


@router.put("/", response_model=SiteSettingsOut)
def update_all_settings(
    data: SiteSettingsUpdate,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    for key, value in data.settings.items():
        setting = db.query(SiteSettings).filter(SiteSettings.key == key).first()
        if setting:
            setting.value = value
        else:
            setting = SiteSettings(key=key, value=value)
            db.add(setting)
    db.commit()

    rows = db.query(SiteSettings).all()
    settings_dict = {row.key: row.value for row in rows}
    return {"settings": settings_dict}
