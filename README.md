# NutriAgent — AI-Powered Multi-Agent Nutrition Platform

A full-stack web application that uses four specialized AI agents orchestrated by LangChain to deliver personalized nutrition guidance, meal planning, and health advisory.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React + Vite + Tailwind)        │
│  Login/Register → Onboarding → Dashboard → Log Meal → Chat      │
│  Recharts (calorie ring, macro rings, weekly trend line chart)   │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP (REST)
┌────────────────────────────▼────────────────────────────────────┐
│                       FastAPI Backend                            │
│  /auth  /profile  /diet-plan  /meal-log  /dashboard  /chat       │
└────────────┬───────────────────────────────────────┬────────────┘
             │                                       │
┌────────────▼─────────────┐            ┌────────────▼────────────┐
│    Orchestrator           │            │    SQLite (SQLAlchemy)   │
│  handle_request(intent)  │            │  Users, Profiles,        │
└───────────┬──────────────┘            │  MealLogs, DietPlans     │
     ┌──────┼──────────────┐            └─────────────────────────┘
     │      │              │
┌────▼──┐ ┌─▼────┐ ┌──────▼──────┐ ┌──────────────┐
│Know-  │ │Reco- │ │  Advisory   │ │  FoodLog &   │
│ledge  │ │mmen- │ │  Agent      │ │  Feedback    │
│Agent  │ │dation│ │(conditions, │ │  Agent       │
│(RAG)  │ │Agent │ │deficiency)  │ │(text/image/  │
└───┬───┘ └──────┘ └─────────────┘ │  voice)      │
    │                               └──────────────┘
┌───▼──────────────────────────────────────────────┐
│  ChromaDB Vector Store                           │
│  seed_foods.json → HuggingFace MiniLM embeddings │
│  ~150 foods: Indian, Western, Mediterranean,     │
│  East Asian cuisines                             │
└──────────────────────────────────────────────────┘
                    │ (optional, with fallback)
        ┌───────────▼───────────┐
        │   Replicate API       │
        │   IBM Granite 3.3 8B  │
        │   LLaVA 13B (vision)  │
        └───────────────────────┘
```

---

## Quick Start (Docker — recommended)

```bash
# 1. Clone / navigate to project root
cd nutriagent

# 2. (Optional) Create .env with your Replicate token
echo "REPLICATE_API_TOKEN=r8_..." > backend/.env

# 3. Start everything
docker-compose up --build

# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API docs: http://localhost:8000/docs
```

> **Works without a Replicate API key!** All AI agents fall back to high-quality mock responses using the built-in nutrition knowledge base. The full demo flow is runnable with zero external dependencies.

---

## Local Development (without Docker)

### Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy env file
cp .env.example .env
# Edit .env to add REPLICATE_API_TOKEN if you have one

# Build the RAG vector store (first time only)
python -m app.rag.ingest

# Start the API server
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server (proxies /api → http://localhost:8000)
npm run dev
# Open http://localhost:5173
```

---

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `REPLICATE_API_TOKEN` | Replicate API key for IBM Granite + LLaVA | (empty — mock mode) |
| `SECRET_KEY` | JWT signing secret | `nutriagent-dev-secret-key-change-in-prod` |
| `DATABASE_URL` | SQLAlchemy DB URL | `sqlite:///./nutriagent.db` |
| `CHROMA_PERSIST_DIR` | ChromaDB persistence directory | `./chroma_db` |

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/auth/register` | Create account |
| POST | `/auth/login` | Get JWT token |
| GET | `/profile` | Get user profile |
| PUT | `/profile` | Update profile |
| POST | `/diet-plan/generate` | Generate 7-day meal plan |
| GET | `/diet-plan/current` | Get active plan |
| POST | `/meal-log` | Log meal (text/image/voice) |
| GET | `/meal-log/history` | Get log history |
| GET | `/dashboard/summary` | Today's totals + weekly trend + alerts |
| POST | `/chat` | Chat with AI agent |
| GET | `/food/search?q=` | RAG food lookup |

Interactive API docs available at `http://localhost:8000/docs`

---

## Multi-Agent System

### 1. Nutrition Knowledge Agent
- RAG-powered lookup in ChromaDB (150 foods across 4 cuisines)
- Returns calories, protein, carbs, fat, fiber, micronutrients
- Cites the source food item — never invents values
- Embedded via `sentence-transformers/all-MiniLM-L6-v2`

### 2. Diet Recommendation Agent
- TDEE calculation (Mifflin-St Jeor equation)
- Personalized 7-day meal plans (breakfast/lunch/dinner/snacks)
- **Code-level allergy filter** — removes any meal containing an allergen after plan generation
- Uses Granite LLM or falls back to a structured mock plan

### 3. Health Advisory Agent
- Condition-specific guidance: diabetes, hypertension, heart disease, kidney disease
- Deficiency detection from meal log history
- Every response ends with the required medical disclaimer
- Rule-based guidance always available (no API key needed)

### 4. Food Log & Feedback Agent
- Parses free-text meal descriptions → food items + portions
- Image upload → LLaVA vision model (or manual text fallback)
- Voice input → Web Speech API transcription → same text pipeline
- Looks up nutrition values in knowledge base, compares vs. daily targets

### Orchestrator
`handle_request(intent, payload)` routes to the right agent based on intent keyword and heuristic message analysis.

---

## Data

`backend/data/seed_foods.json` contains ~150 items covering:
- **Indian**: Dal Tadka, Palak Paneer, Biryani, Idli, Dosa, Sambar, Roti, Chole, Raita
- **Western**: Chicken Breast, Salmon, Quinoa, Oatmeal, Greek Yogurt, Avocado Toast
- **Mediterranean**: Hummus, Falafel, Tabbouleh, Greek Salad, Shakshuka, Lentil Soup
- **East Asian**: Miso Soup, Sushi, Ramen, Gyoza, Bibimbap, Kimchi, Pad Thai, Natto
- Common fruits, vegetables, nuts, seeds, dairy, and beverages

---

## Design Decisions

| Decision | Rationale |
|---|---|
| SQLite | Zero-config DB for local dev; replace `DATABASE_URL` with Postgres for production |
| ChromaDB local | No external vector DB needed; persists to `./chroma_db` |
| `all-MiniLM-L6-v2` embeddings | Fast, lightweight, runs on CPU, good semantic similarity |
| Mock fallback | Every agent catches Replicate exceptions and returns useful mock data |
| Code-level allergy filter | LLM prompts can fail; the `_filter_allergies` function always runs on generated plans |
| HuggingFace embeddings | First run downloads the model (~90MB); subsequent runs use cached version |

---

## Known Limitations

1. **Embeddings first run**: Downloads `all-MiniLM-L6-v2` model on first startup (~90MB). This may take a minute.
2. **Image recognition**: LLaVA vision model requires a valid `REPLICATE_API_TOKEN`. Without it, image input falls back to text description parsing.
3. **LLM meal plan quality**: Mock plans are good but not fully personalized to every edge case (e.g., specific cultural sub-cuisines). With a Replicate key, Granite generates tailored plans.
4. **Voice API**: Works in Chrome and Safari. Firefox has limited Web Speech API support.
5. **SQLite concurrency**: Not suitable for multi-user production loads. Swap `DATABASE_URL` for PostgreSQL.
6. **Nutrition data accuracy**: Seed data contains realistic averages from standard nutrition databases, but values may vary by preparation method and brand.

---

## Tech Stack

- **Backend**: Python 3.11, FastAPI, SQLAlchemy, SQLite
- **AI**: LangChain, IBM Granite 3.3 8B via Replicate, LLaVA 13B (vision)
- **RAG**: ChromaDB, HuggingFace `sentence-transformers/all-MiniLM-L6-v2`
- **Auth**: JWT (python-jose), bcrypt (passlib)
- **Frontend**: React 18, Vite, TypeScript, Tailwind CSS
- **Charts**: Recharts
- **Icons**: Lucide React
- **Containers**: Docker + Docker Compose
