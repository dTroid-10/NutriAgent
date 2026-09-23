from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Profile, DietPlan
from app.auth import get_current_user
from app.schemas import DietPlanResponse
from app.agents import recommendation_agent

router = APIRouter(prefix="/diet-plan", tags=["diet-plan"])


def _profile_to_dict(profile: Profile) -> dict:
    if not profile:
        return {}
    return {
        "age": profile.age,
        "sex": profile.sex,
        "weight_kg": profile.weight_kg,
        "height_cm": profile.height_cm,
        "health_conditions": profile.health_conditions or [],
        "allergies": profile.allergies or [],
        "dietary_preference": profile.dietary_preference or "none",
        "fitness_goal": profile.fitness_goal or "maintain",
        "activity_level": profile.activity_level or "moderate",
    }


@router.post("/generate", response_model=DietPlanResponse)
def generate_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=400, detail="Complete your profile before generating a plan")

    profile_dict = _profile_to_dict(profile)
    result = recommendation_agent.run(profile_dict)

    targets = result["targets"]

    # Deactivate previous plans
    db.query(DietPlan).filter(
        DietPlan.user_id == current_user.id, DietPlan.is_active == 1
    ).update({"is_active": 0})

    plan = DietPlan(
        user_id=current_user.id,
        plan_data=result["plan"],
        calorie_target=targets["calorie_target"],
        protein_target_g=targets["protein_target_g"],
        carbs_target_g=targets["carbs_target_g"],
        fat_target_g=targets["fat_target_g"],
        is_active=1,
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


@router.get("/current", response_model=DietPlanResponse)
def get_current_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    plan = (
        db.query(DietPlan)
        .filter(DietPlan.user_id == current_user.id, DietPlan.is_active == 1)
        .order_by(DietPlan.created_at.desc())
        .first()
    )
    if not plan:
        raise HTTPException(status_code=404, detail="No active diet plan found")
    return plan
