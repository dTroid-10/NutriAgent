from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import date, datetime, timedelta

from app.database import get_db
from app.models import User, MealLog, DietPlan, Profile
from app.auth import get_current_user
from app.schemas import DashboardSummary
from app.agents import advisory_agent

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def _logs_to_dicts(logs) -> list:
    return [
        {
            "calories": l.calories,
            "protein_g": l.protein_g,
            "carbs_g": l.carbs_g,
            "fat_g": l.fat_g,
            "fiber_g": l.fiber_g,
            "logged_at": l.logged_at.isoformat() if l.logged_at else "",
        }
        for l in logs
    ]


@router.get("/summary", response_model=DashboardSummary)
def get_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    today = date.today()
    today_start = datetime.combine(today, datetime.min.time())

    # Active plan
    plan = (
        db.query(DietPlan)
        .filter(DietPlan.user_id == current_user.id, DietPlan.is_active == 1)
        .order_by(DietPlan.created_at.desc())
        .first()
    )

    calorie_target = plan.calorie_target if plan else 2000.0
    protein_target = plan.protein_target_g if plan else 100.0
    carbs_target = plan.carbs_target_g if plan else 225.0
    fat_target = plan.fat_target_g if plan else 55.0

    # Today's logs
    today_logs = (
        db.query(MealLog)
        .filter(MealLog.user_id == current_user.id, MealLog.logged_at >= today_start)
        .all()
    )
    today_calories = sum(l.calories for l in today_logs)
    today_protein = sum(l.protein_g for l in today_logs)
    today_carbs = sum(l.carbs_g for l in today_logs)
    today_fat = sum(l.fat_g for l in today_logs)

    # Weekly trend (last 7 days)
    weekly_trend = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_start = datetime.combine(day, datetime.min.time())
        day_end = datetime.combine(day + timedelta(days=1), datetime.min.time())
        day_logs = (
            db.query(MealLog)
            .filter(
                MealLog.user_id == current_user.id,
                MealLog.logged_at >= day_start,
                MealLog.logged_at < day_end,
            )
            .all()
        )
        weekly_trend.append({
            "date": day.isoformat(),
            "calories": round(sum(l.calories for l in day_logs), 1),
            "protein_g": round(sum(l.protein_g for l in day_logs), 1),
            "carbs_g": round(sum(l.carbs_g for l in day_logs), 1),
            "fat_g": round(sum(l.fat_g for l in day_logs), 1),
        })

    # Deficiency alerts
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    profile_dict = {}
    if profile:
        profile_dict = {
            "health_conditions": profile.health_conditions or [],
            "allergies": profile.allergies or [],
            "calorie_target": calorie_target,
        }

    recent_logs = (
        db.query(MealLog)
        .filter(MealLog.user_id == current_user.id)
        .order_by(MealLog.logged_at.desc())
        .limit(21)
        .all()
    )
    advisory_result = advisory_agent.run(profile_dict, _logs_to_dicts(recent_logs))
    deficiency_alerts = advisory_result.get("deficiency_alerts", [])

    # Streak counter (consecutive days with at least one log)
    streak = 0
    check_day = today
    while True:
        ds = datetime.combine(check_day, datetime.min.time())
        de = datetime.combine(check_day + timedelta(days=1), datetime.min.time())
        count = (
            db.query(MealLog)
            .filter(
                MealLog.user_id == current_user.id,
                MealLog.logged_at >= ds,
                MealLog.logged_at < de,
            )
            .count()
        )
        if count > 0:
            streak += 1
            check_day -= timedelta(days=1)
        else:
            break
        if streak > 365:
            break

    return DashboardSummary(
        today_calories=round(today_calories, 1),
        today_protein_g=round(today_protein, 1),
        today_carbs_g=round(today_carbs, 1),
        today_fat_g=round(today_fat, 1),
        calorie_target=calorie_target,
        protein_target_g=protein_target,
        carbs_target_g=carbs_target,
        fat_target_g=fat_target,
        weekly_trend=weekly_trend,
        deficiency_alerts=deficiency_alerts,
        streak_days=streak,
    )
