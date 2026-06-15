from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_admin
from app.models.models import PricingPlan
from app.schemas.schemas import (
    PricingPlanCreate, PricingPlanUpdate, PricingPlanOut, MessageResponse,
)

router = APIRouter(prefix="/api/pricing", tags=["Pricing"])


@router.get("/", response_model=List[PricingPlanOut])
def get_active_plans(db: Session = Depends(get_db)):
    return (
        db.query(PricingPlan)
        .filter(PricingPlan.is_active == True)
        .order_by(PricingPlan.price)
        .all()
    )


@router.post("/", response_model=PricingPlanOut, status_code=status.HTTP_201_CREATED)
def create_plan(
    data: PricingPlanCreate,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    plan = PricingPlan(**data.model_dump())
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


@router.put("/{plan_id}", response_model=PricingPlanOut)
def update_plan(
    plan_id: int,
    data: PricingPlanUpdate,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    plan = db.query(PricingPlan).filter(PricingPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    for key, value in data.model_dump().items():
        setattr(plan, key, value)
    db.commit()
    db.refresh(plan)
    return plan


@router.delete("/{plan_id}", response_model=MessageResponse)
def delete_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    plan = db.query(PricingPlan).filter(PricingPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    db.delete(plan)
    db.commit()
    return {"message": "Pricing plan deleted"}

