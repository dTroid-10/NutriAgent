"""
Ingest seed_foods.json into a Chroma vector store.
Run once: python -m app.rag.ingest
"""
import json
import os
from pathlib import Path

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document

from app.config import CHROMA_PERSIST_DIR

DATA_FILE = Path(__file__).resolve().parents[3] / "data" / "seed_foods.json"


def build_documents(foods: list) -> list[Document]:
    docs = []
    for food in foods:
        content = (
            f"Food: {food['name']}\n"
            f"Cuisine: {food.get('cuisine', 'N/A')} | Category: {food.get('category', 'N/A')}\n"
            f"Calories: {food['calories_per_100g']} kcal per 100g\n"
            f"Protein: {food['protein_g']}g | Carbs: {food['carbs_g']}g | "
            f"Fat: {food['fat_g']}g | Fiber: {food['fiber_g']}g\n"
            f"Sodium: {food.get('sodium_mg', 0)}mg | Iron: {food.get('iron_mg', 0)}mg | "
            f"Calcium: {food.get('calcium_mg', 0)}mg | Vitamin C: {food.get('vitamin_c_mg', 0)}mg"
        )
        docs.append(
            Document(
                page_content=content,
                metadata={
                    "name": food["name"],
                    "calories_per_100g": food["calories_per_100g"],
                    "protein_g": food["protein_g"],
                    "carbs_g": food["carbs_g"],
                    "fat_g": food["fat_g"],
                    "fiber_g": food["fiber_g"],
                    "sodium_mg": food.get("sodium_mg", 0),
                    "iron_mg": food.get("iron_mg", 0),
                    "calcium_mg": food.get("calcium_mg", 0),
                    "vitamin_c_mg": food.get("vitamin_c_mg", 0),
                    "cuisine": food.get("cuisine", ""),
                    "category": food.get("category", ""),
                },
            )
        )
    return docs


def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


def ingest():
    print(f"Loading seed data from {DATA_FILE}")
    with open(DATA_FILE, "r") as f:
        foods = json.load(f)

    docs = build_documents(foods)
    embeddings = get_embeddings()

    print(f"Building Chroma vector store at {CHROMA_PERSIST_DIR} ...")
    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=CHROMA_PERSIST_DIR,
        collection_name="nutrition_knowledge",
    )
    print(f"Ingested {len(docs)} food items into vector store.")
    return vectorstore


if __name__ == "__main__":
    ingest()
