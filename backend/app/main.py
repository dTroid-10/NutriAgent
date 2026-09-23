from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import sys

# Ensure the app directory is importable when running from backend/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine
from app import models
from app.auth import router as auth_router
from app.routes.profile import router as profile_router
from app.routes.diet_plan import router as diet_plan_router
from app.routes.meal_log import router as meal_log_router
from app.routes.dashboard import router as dashboard_router
from app.routes.chat import router as chat_router
from app.routes.food_search import router as food_router

# Create all DB tables
models.Base.metadata.create_all(bind=engine)

# Bootstrap RAG vector store on startup (non-blocking — creates if missing)
def _bootstrap_rag():
    from app.config import CHROMA_PERSIST_DIR
    chroma_path = os.path.join(os.getcwd(), CHROMA_PERSIST_DIR.lstrip("./"))
    if not os.path.exists(chroma_path) or not os.listdir(chroma_path) if os.path.exists(chroma_path) else True:
        try:
            from app.rag.ingest import ingest
            ingest()
        except Exception as e:
            print(f"[RAG Bootstrap] Warning: {e}")

_bootstrap_rag()

app = FastAPI(
    title="NutriAgent API",
    description="AI-powered multi-agent nutrition platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(diet_plan_router)
app.include_router(meal_log_router)
app.include_router(dashboard_router)
app.include_router(chat_router)
app.include_router(food_router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "NutriAgent API"}
