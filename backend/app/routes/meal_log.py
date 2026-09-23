from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date, datetime

from app.database import get_db
from app.models import User, Profile, MealLog, DietPlan
from app.auth import get_current_user
from app.schemas import MealLogResponse
from app.agents import foodlog_agent

router = APIRouter(prefix="/meal-log", tags=["meal-log"])


def _get_daily_remaining(user_id: int, db: Session) -> dict:
    """Calculate remaining calorie/macro budget for today."""
    today = date.today()
    plan = (
        db.query(DietPlan)
        .filter(DietPlan.user_id == user_id, DietPlan.is_active == 1)
        .order_by(DietPlan.created_at.desc())
        .first()
    )
    targets = {
        "calories": plan.calorie_target if plan else 2000,
        "protein_g": plan.protein_target_g if plan else 100,
        "carbs_g": plan.carbs_target_g if plan else 225,
        "fat_g": plan.fat_target_g if plan else 55,
    }

    # Sum today's logs
    logs_today = (
        db.query(MealLog)
        .filter(
            MealLog.user_id == user_id,
            MealLog.logged_at >= datetime.combine(today, datetime.min.time()),
        )
        .all()
    )
    consumed = {
        "calories": sum(l.calories for l in logs_today),
        "protein_g": sum(l.protein_g for l in logs_today),
        "carbs_g": sum(l.carbs_g for l in logs_today),
        "fat_g": sum(l.fat_g for l in logs_today),
    }

    return {k: targets[k] - consumed.get(k, 0) for k in targets}


@router.post("", response_model=MealLogResponse)
async def log_meal(
    meal_type: Optional[str] = Form("meal"),
    input_text: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    image_bytes = None
    image_mime = "image/jpeg"

    if image:
        image_bytes = await image.read()
        image_mime = image.content_type or "image/jpeg"

    if not input_text and not image_bytes:
        raise HTTPException(status_code=400, detail="Provide either input_text or an image")

    daily_remaining = _get_daily_remaining(current_user.id, db)

    result = foodlog_agent.run(
        text=input_text,
        image_bytes=image_bytes,
        image_mime=image_mime,
        daily_remaining=daily_remaining,
    )

    totals = result["totals"]

    log = MealLog(
        user_id=current_user.id,
        meal_type=meal_type or "meal",
        input_text=input_text or result.get("source_text", ""),
        recognized_foods=result["recognized_foods"],
        calories=totals["calories"],
        protein_g=totals["protein_g"],
        carbs_g=totals["carbs_g"],
        fat_g=totals["fat_g"],
        fiber_g=totals["fiber_g"],
        feedback=result["feedback"],
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.get("/history", response_model=List[MealLogResponse])
def get_history(
    limit: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    logs = (
        db.query(MealLog)
        .filter(MealLog.user_id == current_user.id)
        .order_by(MealLog.logged_at.desc())
        .limit(limit)
        .all()
    )
    return logs
