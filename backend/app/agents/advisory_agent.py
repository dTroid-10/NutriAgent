"""
Health Advisory Agent
Given user profile + recent meal logs, returns:
- Preventive guidance for chronic conditions (diabetes, hypertension, heart disease, kidney)
- Nutrient deficiency flags based on meal history
ALWAYS appends medical disclaimer.
"""
from typing import Dict, Any, List
from app.config import REPLICATE_API_TOKEN, GRANITE_MODEL, USE_MOCK

DISCLAIMER = (
    "\n\n---\n*This is general guidance, not medical advice — "
    "consult a healthcare professional for medical decisions.*"
)

CONDITION_ADVICE = {
    "diabetes": (
        "**Diabetes Management Tips:**\n"
        "• Choose low-GI foods: whole grains, legumes, most vegetables\n"
        "• Limit refined carbohydrates, sugary drinks, and white rice in large portions\n"
        "• Distribute carbohydrates evenly across meals to stabilize blood sugar\n"
        "• Include fiber-rich foods (>25g/day) to slow glucose absorption\n"
        "• Monitor portion sizes carefully for starchy foods"
    ),
    "hypertension": (
        "**Hypertension Management Tips:**\n"
        "• Follow DASH diet principles: fruits, vegetables, low-fat dairy, whole grains\n"
        "• Limit sodium to <2300mg/day (ideally <1500mg for high-risk individuals)\n"
        "• Increase potassium intake: bananas, sweet potatoes, leafy greens\n"
        "• Reduce processed and packaged foods — often high in hidden sodium\n"
        "• Limit alcohol and caffeine intake"
    ),
    "heart disease": (
        "**Heart Disease Prevention Tips:**\n"
        "• Prioritize omega-3 rich foods: salmon, walnuts, flaxseeds, chia seeds\n"
        "• Replace saturated fats with unsaturated fats: olive oil, avocado, nuts\n"
        "• Increase soluble fiber intake to help lower LDL cholesterol\n"
        "• Avoid trans fats and highly processed foods\n"
        "• Include antioxidant-rich fruits and vegetables daily"
    ),
    "kidney": (
        "**Kidney Health Tips:**\n"
        "• Limit high-phosphorus foods: dairy, nuts, seeds, dark colas (if advised by doctor)\n"
        "• Monitor potassium intake based on lab values\n"
        "• Reduce protein intake to levels recommended by your nephrologist\n"
        "• Limit sodium to reduce blood pressure and fluid retention\n"
        "• Stay adequately hydrated unless fluid restricted"
    ),
    "obesity": (
        "**Weight Management Tips:**\n"
        "• Focus on caloric deficit through portion control, not food elimination\n"
        "• Prioritize protein and fiber to increase satiety\n"
        "• Choose whole, minimally processed foods over calorie-dense packaged foods\n"
        "• Incorporate regular physical activity alongside dietary changes"
    ),
}


def _calculate_daily_averages(meal_logs: List[dict]) -> dict:
    """Compute average daily intake from recent meal logs."""
    if not meal_logs:
        return {}
    days: dict = {}
    for log in meal_logs:
        date_str = str(log.get("logged_at", ""))[:10]
        if date_str not in days:
            days[date_str] = {
                "calories": 0, "protein_g": 0, "carbs_g": 0,
                "fat_g": 0, "fiber_g": 0,
            }
        days[date_str]["calories"] += log.get("calories", 0)
        days[date_str]["protein_g"] += log.get("protein_g", 0)
        days[date_str]["carbs_g"] += log.get("carbs_g", 0)
        days[date_str]["fat_g"] += log.get("fat_g", 0)
        days[date_str]["fiber_g"] += log.get("fiber_g", 0)

    n = len(days)
    if n == 0:
        return {}
    totals = {k: sum(d[k] for d in days.values()) / n for k in days[list(days.keys())[0]]}
    return totals


def _detect_deficiencies(averages: dict, profile: dict) -> List[str]:
    """Heuristic deficiency detection based on macro/fiber averages."""
    alerts = []
    if not averages:
        return alerts

    calorie_target = profile.get("calorie_target", 2000)
    if averages.get("fiber_g", 100) < 20:
        alerts.append("⚠️ Low fiber intake (avg {:.1f}g/day). Target ≥25g. Include more vegetables, legumes, and whole grains.".format(averages.get("fiber_g", 0)))
    if averages.get("protein_g", 100) < (calorie_target * 0.15 / 4):
        alerts.append("⚠️ Protein intake may be low. Ensure adequate lean proteins, legumes, or dairy at each meal.")
    if averages.get("calories", 10000) < calorie_target * 0.8:
        alerts.append("⚠️ Calorie intake significantly below target — risk of micronutrient deficiency.")
    return alerts


def _call_llm_advisory(profile: dict, averages: dict, conditions: List[str]) -> str:
    import replicate
    conditions_str = ", ".join(conditions)
    prompt = (
        f"You are a preventive nutrition advisor. Give personalized health guidance.\n"
        f"Patient profile: Age {profile.get('age')}, {profile.get('sex')}, "
        f"Conditions: {conditions_str}\n"
        f"Average daily intake: calories={averages.get('calories', 'N/A'):.0f}, "
        f"protein={averages.get('protein_g', 'N/A'):.1f}g, "
        f"fiber={averages.get('fiber_g', 'N/A'):.1f}g\n"
        f"Provide 3-5 specific, actionable dietary recommendations. Be concise."
    )
    output = replicate.run(GRANITE_MODEL, input={"prompt": prompt, "max_tokens": 600})
    return "".join(output) if hasattr(output, "__iter__") else str(output)


def run(profile: dict, meal_logs: List[dict]) -> Dict[str, Any]:
    """Return health advisory response for the user."""
    conditions = [c.lower() for c in profile.get("health_conditions", [])]
    averages = _calculate_daily_averages(meal_logs)
    deficiency_alerts = _detect_deficiencies(averages, profile)

    # Build condition-specific advice
    advice_sections = []
    for condition in conditions:
        for key, text in CONDITION_ADVICE.items():
            if key in condition:
                advice_sections.append(text)
                break

    llm_advice = ""
    used_mock = False
    if not USE_MOCK and conditions and averages:
        try:
            llm_advice = _call_llm_advisory(profile, averages, conditions)
        except Exception as e:
            print(f"[AdvisoryAgent] LLM call failed: {e}. Using rule-based advice.")
            used_mock = True
    else:
        used_mock = True

    # Compose final response
    parts = []

    if advice_sections:
        parts.append("\n\n".join(advice_sections))

    if deficiency_alerts:
        parts.append("**Nutrient Alerts from Your Meal Log:**\n" + "\n".join(deficiency_alerts))

    if llm_advice and not used_mock:
        parts.append("**Personalized Guidance:**\n" + llm_advice)
    elif not advice_sections and not deficiency_alerts:
        parts.append(
            "Your profile looks good! Keep maintaining a balanced diet with varied whole foods, "
            "adequate protein, plenty of fiber-rich vegetables, and stay hydrated."
        )

    if averages:
        parts.append(
            f"**Your Recent Averages (per day):** "
            f"Calories: {averages.get('calories', 0):.0f} kcal | "
            f"Protein: {averages.get('protein_g', 0):.1f}g | "
            f"Carbs: {averages.get('carbs_g', 0):.1f}g | "
            f"Fat: {averages.get('fat_g', 0):.1f}g | "
            f"Fiber: {averages.get('fiber_g', 0):.1f}g"
        )

    response_text = "\n\n".join(parts) + DISCLAIMER

    return {
        "answer": response_text,
        "deficiency_alerts": deficiency_alerts,
        "averages": averages,
        "used_mock": used_mock,
        "citations": ["NutriAgent dietary guidelines database"],
    }
