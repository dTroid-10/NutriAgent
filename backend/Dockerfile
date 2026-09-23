FROM python:3.11-slim

WORKDIR /app

# Install system deps (for torch/sentence-transformers)
RUN apt-get update && apt-get install -y \
    gcc g++ curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Pre-build the RAG vector store at image build time
RUN python -m app.rag.ingest || true

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
