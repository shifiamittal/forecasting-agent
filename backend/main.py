"""
FastAPI backend — Forecasting Agent
Session 1: health check + ingest endpoint
Sessions 2-4 will add agent endpoints and SSE streaming
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Forecasting Agent API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0"}


@app.post("/api/ingest")
def ingest():
    """Trigger knowledge base ingestion. Run once to seed Qdrant."""
    try:
        from knowledge.ingest import main as run_ingest
        run_ingest()
        return {"status": "ingestion complete"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


@app.post("/api/retrieve")
def retrieve(payload: dict):
    """
    Test retrieval endpoint.
    Body: { "query": "...", "client_id": "HERSHEYS", "user_role": "DS" }
    """
    try:
        from knowledge.retrieval import get_rag_context
        result = get_rag_context(
            query=payload.get("query", ""),
            client_id=payload.get("client_id", "HERSHEYS"),
            user_role=payload.get("user_role", "DS"),
        )
        return result
    except Exception as e:
        return {"status": "error", "detail": str(e)}
