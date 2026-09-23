from typing import Optional, List
from pydantic import BaseModel, EmailStr
from datetime import datetime


# ---------- Profile ----------

class ProfileUpdate(BaseModel):
    age: Optional[int] = None
    sex: Optional[str] = None
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    health_conditions: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    dietary_preference: Optional[str] = None
    fitness_goal: Optional[str] = None
    activity_level: Optional[str] = None


class ProfileResponse(BaseModel):
    id: int
    user_id: int
    age: Optional[int]
    sex: Optional[str]
    weight_kg: Optional[float]
    height_cm: Optional[float]
    health_conditions: Optional[List[str]]
    allergies: Optional[List[str]]
    dietary_preference: Optional[str]
    fitness_goal: Optional[str]
    activity_level: Optional[str]

    class Config:
        from_attributes = True


# ---------- Meal Log ----------

class MealLogRequest(BaseModel):
    input_text: str
    meal_type: Optional[str] = "meal"


class RecognizedFood(BaseModel):
    name: str
    quantity_g: Optional[float] = 100.0
    calories: Optional[float] = 0.0
    protein_g: Optional[float] = 0.0
    carbs_g: Optional[float] = 0.0
    fat_g: Optional[float] = 0.0
    fiber_g: Optional[float] = 0.0


class MealLogResponse(BaseModel):
    id: int
    meal_type: str
    input_text: Optional[str]
    recognized_foods: List[RecognizedFood]
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float
    feedback: Optional[str]
    logged_at: datetime

    class Config:
        from_attributes = True


# ---------- Diet Plan ----------

class DietPlanResponse(BaseModel):
    id: int
    plan_data: dict
    calorie_target: float
    protein_target_g: float
    carbs_target_g: float
    fat_target_g: float
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Dashboard ----------

class DashboardSummary(BaseModel):
    today_calories: float
    today_protein_g: float
    today_carbs_g: float
    today_fat_g: float
    calorie_target: float
    protein_target_g: float
    carbs_target_g: float
    fat_target_g: float
    weekly_trend: List[dict]
    deficiency_alerts: List[str]
    streak_days: int


# ---------- Chat ----------

class ChatRequest(BaseModel):
    message: str
    intent: Optional[str] = "general"


class ChatResponse(BaseModel):
    response: str
    citations: Optional[List[str]] = []
    agent_used: Optional[str] = None


# ---------- Food Search ----------

class FoodSearchResult(BaseModel):
    name: str
    calories_per_100g: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float
    cuisine: Optional[str] = None
