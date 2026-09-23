from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    profile = relationship("Profile", back_populates="user", uselist=False)
    meal_logs = relationship("MealLog", back_populates="user")
    diet_plans = relationship("DietPlan", back_populates="user")


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    age = Column(Integer)
    sex = Column(String)
    weight_kg = Column(Float)
    height_cm = Column(Float)
    health_conditions = Column(JSON, default=list)   # e.g. ["diabetes", "hypertension"]
    allergies = Column(JSON, default=list)            # e.g. ["peanuts", "shellfish"]
    dietary_preference = Column(String, default="none")  # vegetarian/vegan/halal/kosher/none
    fitness_goal = Column(String, default="maintain")    # lose/maintain/gain/muscle/disease_management
    activity_level = Column(String, default="moderate")  # sedentary/light/moderate/active/very_active
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="profile")


class MealLog(Base):
    __tablename__ = "meal_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    meal_type = Column(String, default="meal")  # breakfast/lunch/dinner/snack
    input_text = Column(Text)
    recognized_foods = Column(JSON, default=list)  # [{name, quantity_g, ...macros}]
    calories = Column(Float, default=0.0)
    protein_g = Column(Float, default=0.0)
    carbs_g = Column(Float, default=0.0)
    fat_g = Column(Float, default=0.0)
    fiber_g = Column(Float, default=0.0)
    feedback = Column(Text)
    logged_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="meal_logs")


class DietPlan(Base):
    __tablename__ = "diet_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_data = Column(JSON)   # full weekly plan JSON
    calorie_target = Column(Float)
    protein_target_g = Column(Float)
    carbs_target_g = Column(Float)
    fat_target_g = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Integer, default=1)

    user = relationship("User", back_populates="diet_plans")
