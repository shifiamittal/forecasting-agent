"""
FastAPI backend — Forecasting Agent
Sessions 1+2: health, ingest, retrieve, run-cycle endpoints
"""

import json
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

app = FastAPI(title="Forecasting Agent API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "version": "0.2.0"}


@app.post("/api/ingest")
def ingest():
    try:
        from knowledge.ingest import main as run_ingest
        run_ingest()
        return {"status": "ingestion complete"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


@app.post("/api/retrieve")
def retrieve(payload: dict):
    """
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


@app.post("/api/run-cycle")
def run_cycle(payload: dict):
    """
    Run full agent chain for a scenario.
    Body: { "scenario_id": "hersheys_cycle_47", "user_role": "DS" }
    Returns complete results (non-streaming).
    """
    try:
        from agents.orchestrator import run_full_cycle, DEMO_SCENARIOS
        scenario_id = payload.get("scenario_id", "hersheys_cycle_47")
        user_role   = payload.get("user_role", "DS")
        scenario    = DEMO_SCENARIOS.get(scenario_id)
        if not scenario:
            return {"status": "error",
                    "detail": f"Unknown scenario: {scenario_id}. "
                              f"Available: {list(DEMO_SCENARIOS.keys())}"}
        results = run_full_cycle(scenario, user_role=user_role)
        return {"status": "complete", "results": results}
    except Exception as e:
        import traceback
        return {"status": "error", "detail": str(e),
                "trace": traceback.format_exc()}


@app.get("/api/scenarios")
def list_scenarios():
    from agents.orchestrator import DEMO_SCENARIOS
    return {"scenarios": list(DEMO_SCENARIOS.keys())}