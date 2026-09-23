"""
Chroma retriever — singleton pattern so the vector store is loaded once.
"""
import os
from functools import lru_cache
from typing import List

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document

from app.config import CHROMA_PERSIST_DIR


def _get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


_vectorstore: Chroma | None = None


def get_vectorstore() -> Chroma:
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = Chroma(
            persist_directory=CHROMA_PERSIST_DIR,
            embedding_function=_get_embeddings(),
            collection_name="nutrition_knowledge",
        )
    return _vectorstore


def search_foods(query: str, k: int = 5) -> List[Document]:
    """Retrieve top-k food documents from the vector store."""
    try:
        vs = get_vectorstore()
        results = vs.similarity_search(query, k=k)
        return results
    except Exception as e:
        return []


def search_foods_with_score(query: str, k: int = 5):
    """Retrieve top-k food documents with relevance scores."""
    try:
        vs = get_vectorstore()
        results = vs.similarity_search_with_score(query, k=k)
        return results
    except Exception as e:
        return []


def get_food_by_name(name: str) -> Document | None:
    """Exact or close match for a food name."""
    results = search_foods(name, k=3)
    if results:
        return results[0]
    return None
