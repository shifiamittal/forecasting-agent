export default function ScenarioPanel({
  scenario, setScenario, role, setRole, onRun, loading
}) {
  return (
    <div className="panel panel-scenario">
      <div className="panel-header">Scenario input</div>
      <div className="panel-body">

        <label className="field-label">Forecast cycle</label>
        <select
          className="select"
          value={scenario}
          onChange={e => setScenario(e.target.value)}
        >
          <option value="hersheys_cycle_47">Hersheys — cycle 47</option>
          <option value="corning_cycle_47">Corning — cycle 47</option>
        </select>

        <label className="field-label" style={{ marginTop: "16px" }}>
          User role
          <span className="field-hint">
            Controls which knowledge base chunks are retrieved
          </span>
        </label>
        <div className="role-toggle">
          {["DS", "planner", "engineering"].map(r => (
            <button
              key={r}
              className={`role-btn ${role === r ? "active" : ""}`}
              onClick={() => setRole(r)}
            >
              {r}
            </button>
          ))}
        </div>

        <div className="role-note">
          {role === "DS" && "Retrieves: incidents, eval logs, retrain decisions, readiness reports"}
          {role === "planner" && "Retrieves: exceptions, trade calendar, override decisions"}
          {role === "engineering" && "Retrieves: pipeline logs, incidents, readiness reports"}
        </div>

        <button
          className={`run-btn ${loading ? "loading" : ""}`}
          onClick={onRun}
          disabled={loading}
        >
          {loading ? (
            <span className="spinner-row">
              <span className="spinner" />
              Running agents...
            </span>
          ) : "Run cycle"}
        </button>

        <div className="scenario-meta">
          <div className="meta-row">
            <span className="meta-key">Backend</span>
            <span className="meta-val">localhost:8000</span>
          </div>
          <div className="meta-row">
            <span className="meta-key">Model</span>
            <span className="meta-val">claude-sonnet-4-5</span>
          </div>
          <div className="meta-row">
            <span className="meta-key">Vector store</span>
            <span className="meta-val">Qdrant Cloud</span>
          </div>
          <div className="meta-row">
            <span className="meta-key">Agents</span>
            <span className="meta-val">5 (trigger → eval)</span>
          </div>
        </div>
      </div>
    </div>
  )
}
