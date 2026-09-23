from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Profile, MealLog
from app.auth import get_current_user
from app.schemas import ChatRequest, ChatResponse
from app.agents import orchestrator

router = APIRouter(prefix="/chat", tags=["chat"])


def _get_profile_dict(user_id: int, db: Session) -> dict:
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
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


@router.post("", response_model=ChatResponse)
def chat(
    req: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = _get_profile_dict(current_user.id, db)

    recent_logs = (
        db.query(MealLog)
        .filter(MealLog.user_id == current_user.id)
        .order_by(MealLog.logged_at.desc())
        .limit(14)
        .all()
    )
    meal_logs_dicts = [
        {
            "calories": l.calories,
            "protein_g": l.protein_g,
            "carbs_g": l.carbs_g,
            "fat_g": l.fat_g,
            "fiber_g": l.fiber_g,
            "logged_at": l.logged_at.isoformat() if l.logged_at else "",
        }
        for l in recent_logs
    ]

    result = orchestrator.handle_request(
        intent=req.intent,
        payload={
            "message": req.message,
            "profile": profile,
            "meal_logs": meal_logs_dicts,
        },
    )

    return ChatResponse(
        response=result.get("answer", str(result)),
        citations=result.get("citations", []),
        agent_used=result.get("agent_used", req.intent),
    )
