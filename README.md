# Keystone.ai — Forecasting Agent

An agentic AI system that monitors supply chain forecasts, diagnoses accuracy degradation, and recommends corrective actions. Built as a working prototype demonstrating Director-level AI PM product thinking.

## What it does

The agent pipeline runs after every forecast cycle and:
- **Scans** 2,400+ SKUs automatically to find forecast exceptions
- **Diagnoses** root causes across four layers: data pipeline, feature drift, model performance, external signals
- **Recommends** corrective actions classified by tier: autonomous (T1), recommend + approve (T2), surface only (T3)
- **Evaluates** its own reasoning on faithfulness, layer sequence compliance, and tier classification accuracy

## Architecture

- **Frontend**: React + Vite — four-tab UI (Planner view, Agent reasoning, RAG retrieval, Eval scores)
- **Backend**: FastAPI — five-agent pipeline (Trigger Router, Exception Triage, RCA Diagnostic, Retrain/Override, Eval)
- **Knowledge layer**: Qdrant vector store — institutional memory for incident records, override history, trade calendars
- **LLM**: Claude 3.5 Sonnet — all agent reasoning
- **Clients**: Hershey's, Corning, Michelin (multi-tenant, compliance-isolated)

## Running locally

**Backend:**
```bash
cd backend
.\venv\Scripts\Activate.ps1
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm run dev
```

Open `http://localhost:5173`

## Environment variables

Create `backend/.env`:
```
ANTHROPIC_API_KEY=your_key
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_key
```

## Key design decisions

- **Pipeline adapter pattern**: orchestrator output translated to frontend schema without modifying agent code
- **Fixture fallback**: live pipeline failures gracefully fall back to pre-computed fixture data
- **SSE streaming**: real-time agent progress visible during 30-60s pipeline execution
- **Tier classification**: autonomous actions only for reversible, low-stakes operations
