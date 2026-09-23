"""
Food Log & Feedback Agent
Accepts text/image/voice input describing a meal, identifies foods, estimates portions,
returns nutrition breakdown + comparison vs daily targets.
"""
import re
import json
import base64
from typing import Dict, Any, List, Optional

from app.config import REPLICATE_API_TOKEN, GRANITE_MODEL, VISION_MODEL, USE_MOCK
from app.agents import knowledge_agent

# Default portion size when not specified
DEFAULT_PORTION_G = 150


def _parse_foods_from_text_mock(text: str) -> List[Dict]:
    """
    Simple heuristic parser for mock mode.
    Searches for food names in the knowledge base.
    """
    from app.rag.retriever import search_foods
    results = search_foods(text, k=5)
    foods = []
    for doc in results:
        meta = doc.metadata
        qty = DEFAULT_PORTION_G
        scale = qty / 100
        foods.append({
            "name": meta["name"],
            "quantity_g": qty,
            "calories": round(meta.get("calories_per_100g", 0) * scale, 1),
            "protein_g": round(meta.get("protein_g", 0) * scale, 1),
            "carbs_g": round(meta.get("carbs_g", 0) * scale, 1),
            "fat_g": round(meta.get("fat_g", 0) * scale, 1),
            "fiber_g": round(meta.get("fiber_g", 0) * scale, 1),
        })
    return foods[:3]  # Return top 3 likely items


def _parse_foods_with_llm(text: str) -> List[Dict]:
    """Use Granite to extract food items + portions from text."""
    import replicate
    prompt = (
        "Extract all food items and portion sizes from this meal description. "
        "Return only valid JSON array:\n"
        f"Meal: '{text}'\n\n"
        "Format: [{\"name\": \"food name\", \"quantity_g\": 150}]\n"
        "Use 150g as default portion if unspecified. Return only the JSON array."
    )
    output = replicate.run(GRANITE_MODEL, input={"prompt": prompt, "max_tokens": 400})
    raw = "".join(output) if hasattr(output, "__iter__") else str(output)
    json_match = re.search(r'\[.*\]', raw, re.DOTALL)
    if json_match:
        return json.loads(json_match.group())
    return []


def _recognize_image_with_llm(image_bytes: bytes, mime_type: str = "image/jpeg") -> str:
    """Use vision model to identify foods from an image."""
    import replicate
    b64 = base64.b64encode(image_bytes).decode()
    data_uri = f"data:{mime_type};base64,{b64}"
    try:
        output = replicate.run(
            VISION_MODEL,
            input={
                "image": data_uri,
                "prompt": (
                    "Identify all food items visible in this image and estimate portions. "
                    "List each food item on a new line with approximate weight in grams."
                ),
            },
        )
        return "".join(output) if hasattr(output, "__iter__") else str(output)
    except Exception as e:
        return f"[Vision model unavailable: {e}]"


def _enrich_with_nutrition(parsed_items: List[Dict]) -> List[Dict]:
    """Look up each identified food in the knowledge base to get macro data."""
    enriched = []
    for item in parsed_items:
        name = item.get("name", "")
        qty = item.get("quantity_g", DEFAULT_PORTION_G)
        scale = qty / 100

        result = knowledge_agent.run(name, k=1)
        if result["foods"]:
            f = result["foods"][0]
            enriched.append({
                "name": f["name"],
                "quantity_g": qty,
                "calories": round(f["calories_per_100g"] * scale, 1),
                "protein_g": round(f["protein_g"] * scale, 1),
                "carbs_g": round(f["carbs_g"] * scale, 1),
                "fat_g": round(f["fat_g"] * scale, 1),
                "fiber_g": round(f["fiber_g"] * scale, 1),
            })
        else:
            enriched.append({
                "name": name,
                "quantity_g": qty,
                "calories": 0,
                "protein_g": 0,
                "carbs_g": 0,
                "fat_g": 0,
                "fiber_g": 0,
                "note": "Nutrition data not found in knowledge base",
            })
    return enriched


def _compute_totals(foods: List[Dict]) -> Dict:
    return {
        "calories": round(sum(f.get("calories", 0) for f in foods), 1),
        "protein_g": round(sum(f.get("protein_g", 0) for f in foods), 1),
        "carbs_g": round(sum(f.get("carbs_g", 0) for f in foods), 1),
        "fat_g": round(sum(f.get("fat_g", 0) for f in foods), 1),
        "fiber_g": round(sum(f.get("fiber_g", 0) for f in foods), 1),
    }


def _generate_feedback(totals: Dict, daily_remaining: Optional[Dict]) -> str:
    """Generate a brief feedback message."""
    lines = [
        f"**Meal Summary:** {totals['calories']:.0f} kcal | "
        f"P: {totals['protein_g']:.1f}g | C: {totals['carbs_g']:.1f}g | "
        f"F: {totals['fat_g']:.1f}g | Fiber: {totals['fiber_g']:.1f}g"
    ]

    if daily_remaining:
        rem_cal = daily_remaining.get("calories", 0) - totals["calories"]
        lines.append(
            f"**After this meal:** ~{max(0, rem_cal):.0f} kcal remaining for the day."
        )
        if totals["fiber_g"] < 5:
            lines.append("💡 Consider adding vegetables or legumes to boost fiber intake.")
        if totals["protein_g"] < 15:
            lines.append("💡 This meal is low in protein — try adding eggs, legumes, or lean meat.")

    return "\n".join(lines)


def run(
    text: Optional[str] = None,
    image_bytes: Optional[bytes] = None,
    image_mime: str = "image/jpeg",
    daily_remaining: Optional[Dict] = None,
) -> Dict[str, Any]:
    """
    Process a meal input (text, image, or voice transcription) and return nutrition breakdown.
    """
    raw_description = text or ""
    used_mock = False
    recognized_from_image = False

    # Step 1: If image provided, run vision model
    if image_bytes and not USE_MOCK:
        try:
            vision_text = _recognize_image_with_llm(image_bytes, image_mime)
            raw_description = vision_text if vision_text else raw_description
            recognized_from_image = True
        except Exception as e:
            print(f"[FoodLogAgent] Vision failed: {e}")

    if not raw_description and image_bytes:
        raw_description = "mixed meal from photo"
        recognized_from_image = True

    # Step 2: Parse food items from text
    parsed_items = []
    if not USE_MOCK:
        try:
            parsed_items = _parse_foods_with_llm(raw_description)
        except Exception as e:
            print(f"[FoodLogAgent] LLM parse failed: {e}. Using mock.")
            used_mock = True

    if not parsed_items:
        parsed_items = _parse_foods_from_text_mock(raw_description)
        used_mock = True

    # Step 3: Enrich with nutrition data from knowledge base
    enriched = _enrich_with_nutrition(parsed_items)

    # Step 4: Compute totals
    totals = _compute_totals(enriched)

    # Step 5: Generate feedback
    feedback = _generate_feedback(totals, daily_remaining)

    return {
        "recognized_foods": enriched,
        "totals": totals,
        "feedback": feedback,
        "source_text": raw_description,
        "recognized_from_image": recognized_from_image,
        "used_mock": used_mock,
        "citations": [f["name"] for f in enriched if f.get("calories", 0) > 0],
    }
