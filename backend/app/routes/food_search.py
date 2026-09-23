from fastapi import APIRouter, Query
from typing import List
from app.rag.retriever import search_foods_with_score
from app.schemas import FoodSearchResult

router = APIRouter(prefix="/food", tags=["food"])


@router.get("/search", response_model=List[FoodSearchResult])
def search_food(q: str = Query(..., min_length=1)):
    results = search_foods_with_score(q, k=8)
    foods = []
    for doc, score in results:
        meta = doc.metadata
        foods.append(
            FoodSearchResult(
                name=meta.get("name", ""),
                calories_per_100g=meta.get("calories_per_100g", 0),
                protein_g=meta.get("protein_g", 0),
                carbs_g=meta.get("carbs_g", 0),
                fat_g=meta.get("fat_g", 0),
                fiber_g=meta.get("fiber_g", 0),
                cuisine=meta.get("cuisine", ""),
            )
        )
    return foods
