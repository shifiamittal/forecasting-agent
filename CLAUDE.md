# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Forecasting Agent** — An agentic system for demand forecasting exception handling and root cause analysis. The system runs 5 specialized agents in sequence after each forecast cycle to evaluate forecast quality, triage exceptions, diagnose degradation, and recommend retrain/override decisions.

**Stack:** Python (FastAPI + Anthropic SDK) backend with React (Vite) frontend. Knowledge base powered by Qdrant (vector DB) + sentence-transformers embeddings.

---

## Architecture: The Agent Pipeline

The core system is an **orchestrated chain of 5 agents** that run in sequence on a forecast scenario. Each agent has a specific role, and activation is conditional based on upstream results.

### Agent 1: Trigger Router
- **Role:** Decides which downstream agents to activate
- **Input:** Forecast summary, config thresholds, escalation flag, prior accuracy metrics
- **Output:** List of agents to activate, priority segments, cycle metadata
- **Activation Rules:** Activates Exception Triage if any SKU delta exceeds threshold, bias breaches bounds, or data quality < 0.7. Activates RCA Diagnostic if wMAPE/bias crosses degradation threshold or escalation flag is true.
- **File:** `backend/agents/trigger_router.py`

### Agent 2: Exception Triage
- **Role:** Scores every SKU exception by severity, classifies exception type, produces ranked queue with tier-classified actions
- **Input:** Cycle ID, client ID, priority segments, SKU exceptions, retrieves prior incident/override history from RAG
- **Output:** Ranked exception queue with tier 1/2/3 classification
- **Exception Types:** `data_issue` (quality < 0.7 or known outage), `model_issue` (quality >= 0.7 but bias outside threshold 2+ cycles), `demand_signal` (external event explains delta)
- **Tier System:**
  - Tier 1 (autonomous): severity < 4 or demand_signal with known calendar event
  - Tier 2 (recommend + approve): severity 4-7 or model_issue on non-top-20 velocity SKU
  - Tier 3 (surface only): severity > 7 or data_issue with no known root cause
- **File:** `backend/agents/exception_triage.py`

### Agent 3: RCA Diagnostic (Root Cause Analysis)
- **Role:** Executes structured 4-layer diagnostic to find root cause of degradation
- **Input:** Degraded segment, degradation metrics, pipeline diagnostic data, retrieves prior incident history from RAG
- **Output:** Root cause layer (data|feature|model|external), confidence score, evidence-based reasoning, downstream trigger
- **Diagnostic Sequence (stops at root cause):**
  1. **Data Pipeline:** Check feed freshness, pipeline failures, data quality
  2. **Feature Drift:** Check input distributions, promo flags, ACV data shifts
  3. **Model Performance:** Check model version, training date, segment coverage
  4. **External Signals:** Trade calendar events, macro flags, competitor actions
- **File:** `backend/agents/rca_diagnostic.py`

### Agent 4: Retrain/Override Recommendation
- **Role:** Decides whether fix is statistical override or full model retrain
- **Input:** RCA output, degradation history, retrieves prior retrain/override decisions from RAG
- **Output:** Recommendation type (override|retrain|both), rationale citing evidence and precedent
- **Decision Rules:**
  - **OVERRIDE** when: segment-specific (< 15% scope), identifiable root cause, time-bounded, duration < 3 cycles
  - **RETRAIN** when: broad scope (> 15%), structural shift, persistent worsening bias 3+ cycles, training data misaligned
- **Important:** No autonomous actions. All recommendations are Tier 2 (approval) or Tier 3 (surfaced)
- **File:** `backend/agents/retrain_override.py`

### Agent 5: Eval Agent
- **Role:** Validates agent quality on three dimensions asynchronously
- **Input:** Any RCA or retrain/override output
- **Output:** Scores on faithfulness, layer-sequence compliance, tier-classification accuracy
- **Thresholds:** tier_classification_accuracy < 0.9 triggers prompt review; any Tier 1 irreversible action triggers immediate escalation
- **File:** `backend/agents/eval_agent.py`

### Knowledge Layer (RAG)
- **Role:** Provides permission-scoped context retrieval to every agent
- **Components:**
  - **Ingestion** (`backend/knowledge/ingest.py`): Embeds synthetic documents using `sentence-transformers`, stores in Qdrant with full metadata (client_id, source_type, visible_to permissions)
  - **Retrieval** (`backend/knowledge/retrieval.py`): 3-stage pipeline:
    1. NL query router (intent classification → pre-filter source_types)
    2. Semantic vector search with metadata filtering
    3. Re-rank by keyword overlap + permission-aware filtering (scoped by user_role)
- **Intent Routing:** Classifies queries into `data_issue`, `model_issue`, `override`, `promo_event`, `feature_drift` to pre-select relevant source types
- **Permission Graph:** `visible_to` field controls which user roles (DS, planner, engineering) retrieve each chunk — same query returns different results by role
- **Files:** `backend/knowledge/ingest.py`, `backend/knowledge/retrieval.py`

### Synthetic Data
- **File:** `backend/data/synthetic_data.py`
- **Contents:** 5 document types across 3 tenants (HERSHEYS, CORNING, MICHELIN)
  - `incident_record`: Feed failures, distribution drift, promo forecast errors
  - `readiness_report`: Data quality, pipeline diagnostics
  - `override_decision`: Planner decisions with rationale
  - `retrain_decision`: Model retraining history and outcomes
  - `trade_calendar`: Promo events and lift multipliers
- **Each document includes:** doc_id, source_type, client_id, date, segment, retailer_scope, severity, root_cause_layer, visible_to (permission), content

---

## Common Commands

### Backend Setup
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1   # PowerShell
# venv\Scripts\activate.bat   # CMD
python -m pip install -r requirements.txt
```

### Start Backend (FastAPI + Uvicorn)
```bash
cd backend
uvicorn main:app --reload --port 8000
```
Endpoints available:
- `GET /health` — Health check
- `POST /api/ingest` — Ingest synthetic docs into Qdrant
- `POST /api/retrieve` — RAG retrieval (body: query, client_id, user_role)
- `POST /api/run-cycle` — Run full agent chain (body: scenario_id, user_role)
- `GET /api/scenarios` — List available demo scenarios

### Environment Variables
Create `backend/.env`:
```
ANTHROPIC_API_KEY=sk-ant-...
QDRANT_URL=https://...qdrant.io:6333
QDRANT_API_KEY=...
```

### Run a Single Agent (Demo)
```bash
cd backend
python agents/trigger_router.py          # Runs demo trigger routing
python agents/exception_triage.py        # Runs demo exception triage
python agents/rca_diagnostic.py          # Runs demo RCA
python agents/retrain_override.py        # Runs demo retrain/override
python agents/eval_agent.py              # Runs demo eval
```

### Run Full Orchestrator (End-to-End)
```bash
cd backend
python agents/orchestrator.py            # Runs full cycle on HERSHEYS_DEMO
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev                              # Start dev server on http://localhost:5173
npm run build                            # Production build
npm run lint                             # ESLint check
```

---

## Key Design Patterns

### 1. Claude API Integration
- **Model:** claude-sonnet-4-5 (all agents use same model for consistency)
- **Pattern:** Agents accept structured input, emit strict JSON output (with markdown fence stripping for robustness)
- **RAG:** Each agent (2-4) retrieves context before reasoning via `get_rag_context()`

### 2. Tier Classification System
Every agent output includes tier-classified actions:
- **Tier 1 (Autonomous):** Executed without approval (low-stakes, reversible)
- **Tier 2 (Recommend + Approve):** Queued for human decision
- **Tier 3 (Surface Only):** Surfaced to engineers/PMs for visibility

This is **enforced by the Eval Agent** — any Tier 1 action on an irreversible decision triggers immediate escalation.

### 3. Permission Graph (Role-Scoped Retrieval)
The `visible_to` field in every document controls which user roles retrieve it:
- **DS:** Sees incident_record, eval_logs, retrain_decision, readiness_report
- **Planner:** Sees exception_queue, trade_calendar, override_decision
- **Engineering:** Sees pipeline_logs, incident_record, readiness_report

This is evaluated in `backend/knowledge/retrieval.py` during the permission-graph filtering stage.

### 4. Scenario-Driven Testing
Two demo scenarios baked into `backend/agents/orchestrator.py`:
- `hersheys_cycle_47`: Chocolate seasonal SKU with Kroger feed failure + trade calendar event
- `corning_cycle_47`: Industrial SKU group with distribution drift

Each includes: forecast_summary, config thresholds, SKU exceptions, pipeline diagnostic data, degradation_history.

**Frontend** selects scenario + user role, calls `POST /api/run-cycle`, displays results across 4 panels (Scenario, Agent Outputs, RAG Context, Final Results).

---

## Frontend Architecture (React + Vite)

### Main Component Structure
- **App.jsx:** Root component managing scenario selection, role toggle, run-cycle orchestration, error handling
- **ScenarioPanel:** Scenario/role selector with metadata display (backend URL, model, vector store, agent count)
- **AgentPanel:** Displays agent outputs (trigger_router, exception_triage, rca_diagnostic, retrain_override, evals)
- **RagPanel:** Shows RAG retrieval results with intent classification, source types, relevant chunks
- **OutputPanel:** Final structured results from full cycle

### Data Flow
1. User selects scenario + role in ScenarioPanel
2. Click "Run cycle" → calls `POST /api/run-cycle` with scenario_id + user_role
3. Backend orchestrates 5-agent chain, returns structured results
4. Results rendered in AgentPanel, RagPanel, OutputPanel with role-aware filtering

---

## Important Implementation Details

### JSON Output Parsing
All agents return JSON with potential markdown fences. Parsing pattern:
```python
raw = response.content[0].text.strip()
if raw.startswith("```"):
    raw = raw.split("```")[1]
    if raw.startswith("json"):
        raw = raw[4:]
return json.loads(raw.strip())
```

### RAG Query Context
Agents pass retrieval context to downstream agents via knowledge base:
- **Exception Triage** queries: `"exception override history {segment}"` → retrieves prior overrides and triage decisions
- **RCA** queries: `"feed failure degradation incident {segment}"` → retrieves prior incident history for pattern matching
- **Retrain/Override** queries: `"retrain override decision {root_cause_layer} {segment}"` → retrieves prior retrain/override decisions

### Metadata Catalog Schema
Every ingested document includes:
- `doc_id`, `source_type`, `client_id`, `date`, `segment`, `retailer_scope`
- `severity`, `root_cause_layer`, `visible_to` (permission), `freshness_ts`, `embedding_model`
- `content` (full text)

---

## Extending the System

### Adding a New Agent
1. Create `backend/agents/new_agent.py` with a `run_new_agent()` function
2. Define SYSTEM_PROMPT with structured output schema (JSON format required)
3. Call `get_rag_context()` if context is needed
4. Add to orchestrator chain in `backend/agents/orchestrator.py`
5. Update Eval Agent to score new agent's output if needed

### Adding New Synthetic Documents
1. Extend `SYNTHETIC_DOCUMENTS` list in `backend/data/synthetic_data.py`
2. Include all metadata fields (doc_id, source_type, client_id, date, segment, retailer_scope, severity, root_cause_layer, visible_to, content)
3. Call `POST /api/ingest` to refresh Qdrant collection

### Adding New Scenarios
1. Create scenario dict in `backend/agents/orchestrator.py` (must include all required fields: forecast_summary, config, escalation_flag, prior_accuracy, sku_exceptions, pipeline_data, degradation_history)
2. Add to `DEMO_SCENARIOS` dict with a key
3. Frontend can then select it via scenario dropdown

---

## Testing Patterns

### Testing a Single Agent
Each agent has a `if __name__ == "__main__"` section demonstrating typical input. Run via:
```bash
cd backend
python agents/trigger_router.py
```

### Testing the Full Cycle
```bash
cd backend
python agents/orchestrator.py
```
This runs HERSHEYS_DEMO through all 5 agents and prints structured JSON output.

### Testing RAG
```bash
cd backend
python knowledge/retrieval.py
```
This demonstrates intent classification, semantic search, re-ranking, and permission filtering.

### Testing Ingestion
```bash
cd backend
python knowledge/ingest.py
```
This embeds synthetic documents and upserts to Qdrant.

---

## Debugging Tips

1. **Backend logs:** Uvicorn prints agent invocations, intent routing, RAG confidence, etc. Watch for `print()` statements in agent files
2. **Qdrant connectivity:** Verify `QDRANT_URL` and `QDRANT_API_KEY` in `.env` before calling `/api/ingest`
3. **JSON parse errors:** Check if Claude returned unparseable JSON (common with truncated responses). Increase `max_tokens` if needed.
4. **Permission filtering:** If RAG returns empty, check if document's `visible_to` list includes the user_role being queried
5. **Agent activation logic:** Check `agents_activated` list from trigger_router output to understand why downstream agents did/didn't run

---

## Key Files Summary

| File | Purpose |
|------|---------|
| `backend/main.py` | FastAPI app, 4 endpoints (ingest, retrieve, run-cycle, scenarios) |
| `backend/agents/trigger_router.py` | Agent 1: decision routing |
| `backend/agents/exception_triage.py` | Agent 2: SKU severity scoring + triage queue |
| `backend/agents/rca_diagnostic.py` | Agent 3: 4-layer diagnostic sequence |
| `backend/agents/retrain_override.py` | Agent 4: override vs retrain decision |
| `backend/agents/eval_agent.py` | Agent 5: quality validation |
| `backend/agents/orchestrator.py` | Chains all agents, defines demo scenarios |
| `backend/knowledge/ingest.py` | Qdrant ingestion pipeline |
| `backend/knowledge/retrieval.py` | Permission-scoped RAG retrieval |
| `backend/data/synthetic_data.py` | Demo documents for 3 clients |
| `frontend/src/App.jsx` | Root React component |
| `frontend/src/components/*.jsx` | Scenario, Agent, RAG, Output panels |
