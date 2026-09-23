"""
Diet Recommendation Agent
Generates structured weekly meal plans personalized to user profile.
- Calls knowledge_agent for food data
- Filters out any food matching user's allergy list (code-level guardrail)
- Uses Replicate/Granite LLM or falls back to a mock plan
"""
import json
import re
from typing import Dict, Any, List

from app.config import REPLICATE_API_TOKEN, GRANITE_MODEL, USE_MOCK
from app.agents import knowledge_agent


def _calculate_tdee(profile: dict) -> dict:
    """Mifflin-St Jeor TDEE calculation."""
    weight = profile.get("weight_kg", 70)
    height = profile.get("height_cm", 170)
    age = profile.get("age", 30)
    sex = profile.get("sex", "male")
    activity_multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9,
    }
    activity = activity_multipliers.get(profile.get("activity_level", "moderate"), 1.55)

    if sex == "female":
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age + 5

    tdee = bmr * activity
    goal = profile.get("fitness_goal", "maintain")
    if goal == "lose":
        tdee -= 500
    elif goal == "gain" or goal == "muscle":
        tdee += 300

    # Macros: 30% protein, 45% carbs, 25% fat
    protein_g = (tdee * 0.30) / 4
    carbs_g = (tdee * 0.45) / 4
    fat_g = (tdee * 0.25) / 9

    return {
        "calorie_target": round(tdee),
        "protein_target_g": round(protein_g),
        "carbs_target_g": round(carbs_g),
        "fat_target_g": round(fat_g),
    }


def _is_allergen(food_name: str, allergies: List[str]) -> bool:
    food_lower = food_name.lower()
    for allergen in allergies:
        if allergen.lower() in food_lower:
            return True
    return False


def _filter_allergies(plan: dict, allergies: List[str]) -> dict:
    """Code-level allergy filter — removes any meal containing an allergen."""
    if not allergies:
        return plan
    days = plan.get("days", [])
    for day in days:
        for meal_type in ["breakfast", "lunch", "dinner", "snacks"]:
            items = day.get(meal_type, [])
            filtered = [
                item for item in items
                if not _is_allergen(item.get("food", ""), allergies)
            ]
            day[meal_type] = filtered
    return plan


def _get_mock_plan(profile: dict, targets: dict) -> dict:
    pref = profile.get("dietary_preference", "none")
    cuisine = profile.get("cuisine_preference", "Western")

    days = []
    meal_templates = [
        {
            "day": "Monday",
            "breakfast": [
                {"food": "Oatmeal with Berries", "quantity_g": 200, "calories": 180},
                {"food": "Greek Yogurt (plain, full fat)", "quantity_g": 150, "calories": 146},
            ],
            "lunch": [
                {"food": "Quinoa (cooked)", "quantity_g": 150, "calories": 180},
                {"food": "Grilled Vegetable Wrap", "quantity_g": 200, "calories": 290},
            ],
            "dinner": [
                {"food": "Salmon (baked)", "quantity_g": 150, "calories": 312},
                {"food": "Broccoli", "quantity_g": 100, "calories": 34},
                {"food": "Brown Rice", "quantity_g": 150, "calories": 324},
            ],
            "snacks": [
                {"food": "Almonds", "quantity_g": 30, "calories": 174},
                {"food": "Apple", "quantity_g": 150, "calories": 78},
            ],
        },
        {
            "day": "Tuesday",
            "breakfast": [
                {"food": "Avocado Toast (Whole Grain)", "quantity_g": 200, "calories": 370},
                {"food": "Eggs (boiled)", "quantity_g": 100, "calories": 155},
            ],
            "lunch": [
                {"food": "Lentil Soup", "quantity_g": 300, "calories": 216},
                {"food": "Pita Bread", "quantity_g": 60, "calories": 165},
            ],
            "dinner": [
                {"food": "Chicken Tikka Masala", "quantity_g": 200, "calories": 310},
                {"food": "Basmati Rice", "quantity_g": 150, "calories": 182},
            ],
            "snacks": [
                {"food": "Mixed Nuts (unsalted)", "quantity_g": 30, "calories": 182},
                {"food": "Banana", "quantity_g": 120, "calories": 107},
            ],
        },
        {
            "day": "Wednesday",
            "breakfast": [
                {"food": "Poha (Flattened Rice)", "quantity_g": 200, "calories": 260},
                {"food": "Chai (with milk, low sugar)", "quantity_g": 200, "calories": 104},
            ],
            "lunch": [
                {"food": "Hummus", "quantity_g": 100, "calories": 177},
                {"food": "Greek Salad", "quantity_g": 200, "calories": 236},
                {"food": "Pita Bread", "quantity_g": 60, "calories": 165},
            ],
            "dinner": [
                {"food": "Palak Paneer", "quantity_g": 200, "calories": 308},
                {"food": "Roti (Whole Wheat Chapati)", "quantity_g": 100, "calories": 297},
            ],
            "snacks": [
                {"food": "Guava", "quantity_g": 150, "calories": 102},
                {"food": "Chia Seeds", "quantity_g": 20, "calories": 97},
            ],
        },
        {
            "day": "Thursday",
            "breakfast": [
                {"food": "Smoothie Bowl (Acai)", "quantity_g": 250, "calories": 300},
                {"food": "Blueberries", "quantity_g": 100, "calories": 57},
            ],
            "lunch": [
                {"food": "Sushi Roll (Cucumber)", "quantity_g": 200, "calories": 186},
                {"food": "Miso Soup", "quantity_g": 200, "calories": 80},
                {"food": "Edamame", "quantity_g": 100, "calories": 121},
            ],
            "dinner": [
                {"food": "Stir-Fried Vegetables with Tofu", "quantity_g": 300, "calories": 255},
                {"food": "Brown Rice", "quantity_g": 150, "calories": 324},
            ],
            "snacks": [
                {"food": "Green Tea", "quantity_g": 250, "calories": 2},
                {"food": "Rice Crackers", "quantity_g": 40, "calories": 155},
            ],
        },
        {
            "day": "Friday",
            "breakfast": [
                {"food": "Dosa (Plain)", "quantity_g": 150, "calories": 252},
                {"food": "Sambar", "quantity_g": 150, "calories": 98},
            ],
            "lunch": [
                {"food": "Tabbouleh", "quantity_g": 200, "calories": 218},
                {"food": "Falafel", "quantity_g": 100, "calories": 333},
                {"food": "Hummus", "quantity_g": 60, "calories": 106},
            ],
            "dinner": [
                {"food": "Grilled Fish with Lemon", "quantity_g": 200, "calories": 270},
                {"food": "Ratatouille", "quantity_g": 200, "calories": 130},
                {"food": "Couscous (cooked)", "quantity_g": 150, "calories": 168},
            ],
            "snacks": [
                {"food": "Pomegranate", "quantity_g": 150, "calories": 125},
                {"food": "Walnuts", "quantity_g": 25, "calories": 164},
            ],
        },
        {
            "day": "Saturday",
            "breakfast": [
                {"food": "Upma", "quantity_g": 200, "calories": 290},
                {"food": "Coconut Water", "quantity_g": 250, "calories": 48},
            ],
            "lunch": [
                {"food": "Bibimbap", "quantity_g": 350, "calories": 455},
                {"food": "Kimchi", "quantity_g": 50, "calories": 8},
            ],
            "dinner": [
                {"food": "Dal Tadka (Yellow Lentil Curry)", "quantity_g": 200, "calories": 220},
                {"food": "Khichdi", "quantity_g": 200, "calories": 240},
                {"food": "Raita", "quantity_g": 100, "calories": 62},
            ],
            "snacks": [
                {"food": "Mango", "quantity_g": 150, "calories": 90},
                {"food": "Protein Bar (generic)", "quantity_g": 50, "calories": 188},
            ],
        },
        {
            "day": "Sunday",
            "breakfast": [
                {"food": "Tamago Kake Gohan", "quantity_g": 250, "calories": 388},
                {"food": "Miso Soup", "quantity_g": 200, "calories": 80},
            ],
            "lunch": [
                {"food": "Chicken Breast (cooked)", "quantity_g": 150, "calories": 248},
                {"food": "Caesar Salad (no croutons)", "quantity_g": 200, "calories": 240},
                {"food": "Whole Wheat Bread", "quantity_g": 60, "calories": 148},
            ],
            "dinner": [
                {"food": "Shakshuka", "quantity_g": 300, "calories": 285},
                {"food": "Pita Bread", "quantity_g": 80, "calories": 220},
            ],
            "snacks": [
                {"food": "Dark Chocolate (70%+)", "quantity_g": 25, "calories": 150},
                {"food": "Strawberry", "quantity_g": 150, "calories": 48},
            ],
        },
    ]
    return {"days": meal_templates, **targets}


def _call_llm_for_plan(profile: dict, targets: dict) -> str:
    """Call Granite via Replicate for plan generation."""
    import replicate

    conditions_str = ", ".join(profile.get("health_conditions", [])) or "none"
    allergies_str = ", ".join(profile.get("allergies", [])) or "none"
    prompt = f"""You are a certified dietitian. Generate a 7-day meal plan as JSON.
Profile: Age {profile.get('age')}, {profile.get('sex')}, {profile.get('weight_kg')}kg, 
{profile.get('height_cm')}cm, Goal: {profile.get('fitness_goal')},
Dietary preference: {profile.get('dietary_preference')},
Health conditions: {conditions_str}, Allergies (NEVER include): {allergies_str}.
Calorie target: {targets['calorie_target']} kcal/day.

Return ONLY valid JSON with structure:
{{"days": [{{"day": "Monday", "breakfast": [{{"food": "name", "quantity_g": 200, "calories": 200}}], 
"lunch": [...], "dinner": [...], "snacks": [...]}}]}}"""

    output = replicate.run(GRANITE_MODEL, input={"prompt": prompt, "max_tokens": 2000})
    return "".join(output) if hasattr(output, "__iter__") else str(output)


def run(profile: dict) -> Dict[str, Any]:
    """Generate a weekly meal plan for the given user profile."""
    targets = _calculate_tdee(profile)
    allergies = profile.get("allergies", [])

    plan = None
    used_mock = False

    if not USE_MOCK:
        try:
            raw = _call_llm_for_plan(profile, targets)
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', raw, re.DOTALL)
            if json_match:
                plan = json.loads(json_match.group())
                plan.update(targets)
        except Exception as e:
            print(f"[RecommendationAgent] LLM call failed: {e}. Using mock.")
            used_mock = True

    if plan is None:
        plan = _get_mock_plan(profile, targets)
        used_mock = True

    # Code-level allergy guardrail
    plan = _filter_allergies(plan, allergies)

    return {
        "plan": plan,
        "targets": targets,
        "used_mock": used_mock,
        "citations": ["NutriAgent Knowledge Base (seed_foods.json)"],
    }
