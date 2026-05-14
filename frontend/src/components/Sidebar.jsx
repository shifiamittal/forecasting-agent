export default function Sidebar({ clients, selectedClient, onSelectClient, cycleData, isRunning, onRun, pipelineProgress }) {
  const cycle = cycleData?.cycle

  return (
    <aside className="sidebar">
      <div className="sb-top">
        <div className="sb-brand">Keystone<span>.ai</span></div>
        <div className="sb-sub">Forecasting Agent</div>
      </div>

      <div className="sb-section">
        <div className="sb-label">Clients</div>
        {clients.map(c => (
          <button
            key={c.id}
            className={`client-card${selectedClient === c.id ? ' active' : ''}`}
            onClick={() => onSelectClient(c.id)}
          >
            <span className="cc-name">{c.name}</span>
            <span className="cc-cycle">{c.cycle}</span>
          </button>
        ))}
      </div>

      {cycle && (
        <div className="sb-section">
          <div className="sb-label">Active cycle</div>
          <div className="cycle-card">
            <div className="cc-row">
              <span className="cc-k">Client</span>
              <span className="cc-v">{cycle.client_name}</span>
            </div>
            <div className="cc-row">
              <span className="cc-k">Cycle</span>
              <span className="cc-v">{cycle.cycle_id}</span>
            </div>
            <div className="cc-row">
              <span className="cc-k">SKUs scanned</span>
              <span className="cc-v">{cycle.skus_scanned?.toLocaleString()}</span>
            </div>
            <div className="cc-row">
              <span className="cc-k">Agents active</span>
              <span className="cc-v">{cycle.agents_active}</span>
            </div>
          </div>
        </div>
      )}

      <div className="sb-section">
        <div className="sb-label">System</div>
        <div className="cycle-card">
          <div className="cc-row">
            <span className="cc-k">Backend</span>
            <span className="cc-v"><span className="status-dot" />Live</span>
          </div>
          <div className="cc-row">
            <span className="cc-k">Vector store</span>
            <span className="cc-v">Qdrant</span>
          </div>
          <div className="cc-row">
            <span className="cc-k">LLM</span>
            <span className="cc-v">Claude 3.5</span>
          </div>
          <div className="cc-row">
            <span className="cc-k">Model</span>
            <span className="cc-v">AutoGluon v2.3</span>
          </div>
        </div>
      </div>

      {isRunning && pipelineProgress ? (
        <div className="pipeline-progress">
          <div className="pp-agent">{pipelineProgress.agent_name}</div>
          <div className="pp-message">{pipelineProgress.message}</div>
          <div className="pp-bar">
            <div
              className="pp-fill"
              style={{ width: `${((pipelineProgress.step) / (pipelineProgress.total || 5)) * 100}%` }}
            />
          </div>
          <div className="pp-step">
            {pipelineProgress.step > 0
              ? `Agent ${pipelineProgress.step} of ${pipelineProgress.total || 5}`
              : 'Initialising…'}
          </div>
        </div>
      ) : (
        <button className="run-btn" onClick={onRun} disabled={isRunning}>
          {isRunning && <span className="spin" />}
          {isRunning ? 'Running agents…' : '▶ Run live'}
        </button>
      )}

      <div className="sb-footer">Keystone Platform v2.3</div>
    </aside>
  )
}
