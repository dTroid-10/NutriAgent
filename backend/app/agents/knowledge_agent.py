"""
Nutrition Knowledge Agent — RAG-based food data lookup.
Returns calories/macros/micronutrients from the Chroma vector store.
Never invents values not present in the retrieved context.
"""
from typing import List, Dict, Any
from app.rag.retriever import search_foods_with_score


def run(query: str, k: int = 5) -> Dict[str, Any]:
    """
    Given a food name/query, return top-k matching food items with nutrition data.
    """
    results = search_foods_with_score(query, k=k)

    if not results:
        return {
            "answer": f"No nutrition data found for '{query}' in the knowledge base.",
            "foods": [],
            "citations": [],
        }

    foods = []
    citations = []
    lines = []

    for doc, score in results:
        meta = doc.metadata
        food_entry = {
            "name": meta.get("name", "Unknown"),
            "calories_per_100g": meta.get("calories_per_100g", 0),
            "protein_g": meta.get("protein_g", 0),
            "carbs_g": meta.get("carbs_g", 0),
            "fat_g": meta.get("fat_g", 0),
            "fiber_g": meta.get("fiber_g", 0),
            "sodium_mg": meta.get("sodium_mg", 0),
            "iron_mg": meta.get("iron_mg", 0),
            "calcium_mg": meta.get("calcium_mg", 0),
            "vitamin_c_mg": meta.get("vitamin_c_mg", 0),
            "cuisine": meta.get("cuisine", ""),
            "relevance_score": round(float(score), 3),
        }
        foods.append(food_entry)
        citations.append(meta.get("name", "Unknown"))
        lines.append(
            f"• **{meta.get('name')}** ({meta.get('cuisine', '')}): "
            f"{meta.get('calories_per_100g')} kcal/100g | "
            f"P: {meta.get('protein_g')}g | C: {meta.get('carbs_g')}g | F: {meta.get('fat_g')}g"
        )

    answer = f"Here are the top nutrition matches for **{query}**:\n\n" + "\n".join(lines)

    return {
        "answer": answer,
        "foods": foods,
        "citations": citations,
    }
