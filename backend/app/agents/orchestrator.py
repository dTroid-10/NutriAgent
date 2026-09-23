"""
Orchestrator — routes requests to the appropriate agent(s) and merges output.
Entry point for /chat and other multi-agent endpoints.
"""
from typing import Dict, Any, Optional

from app.agents import knowledge_agent, recommendation_agent, advisory_agent, foodlog_agent


def handle_request(intent: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Route to the correct agent based on intent.

    Intents:
        - "knowledge"      → Nutrition Knowledge Agent (food lookup)
        - "recommendation" → Diet Recommendation Agent (meal plan generation)
        - "advisory"       → Health Advisory Agent (guidance + deficiency detection)
        - "foodlog"        → Food Log & Feedback Agent (parse meal + feedback)
        - "general"        → Tries knowledge agent first, falls back to advisory
    """
    intent = (intent or "general").lower().strip()

    if intent == "knowledge" or _is_food_lookup(payload.get("message", "")):
        query = payload.get("message") or payload.get("query", "")
        return knowledge_agent.run(query, k=payload.get("k", 5))

    elif intent == "recommendation":
        profile = payload.get("profile", {})
        return recommendation_agent.run(profile)

    elif intent == "advisory":
        profile = payload.get("profile", {})
        meal_logs = payload.get("meal_logs", [])
        return advisory_agent.run(profile, meal_logs)

    elif intent == "foodlog":
        return foodlog_agent.run(
            text=payload.get("text"),
            image_bytes=payload.get("image_bytes"),
            image_mime=payload.get("image_mime", "image/jpeg"),
            daily_remaining=payload.get("daily_remaining"),
        )

    else:
        # General: try knowledge agent, then advisory if no good results
        query = payload.get("message", "")
        result = knowledge_agent.run(query, k=5)

        if not result["foods"]:
            # No food match — try advisory style response
            profile = payload.get("profile", {})
            meal_logs = payload.get("meal_logs", [])
            adv_result = advisory_agent.run(profile, meal_logs)
            return {
                "answer": adv_result["answer"],
                "foods": [],
                "citations": adv_result.get("citations", []),
                "agent_used": "advisory",
            }

        result["agent_used"] = "knowledge"
        return result


def _is_food_lookup(message: str) -> bool:
    """Heuristic: detect if the message is a food nutrition query."""
    keywords = [
        "nutrition", "calories", "calorie", "protein", "carbs", "fat", "macro",
        "how much", "what is in", "nutrient", "vitamin", "mineral", "fiber",
    ]
    message_lower = message.lower()
    return any(kw in message_lower for kw in keywords)
