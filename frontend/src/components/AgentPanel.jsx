function AgentBlock({ name, data, color }) {
  if (!data) return null
  const lines = []

  if (name === "trigger_router") {
    lines.push(`Activated: ${data.agents_activated?.join(", ")}`)
    lines.push(`Priority: ${data.priority_segments?.join(", ")}`)
    lines.push(data.cycle_summary)
  } else if (name === "exception_triage") {
    data.exceptions?.forEach(ex => {
      lines.push(`[${ex.tier === 1 ? "T1" : ex.tier === 2 ? "T2" : "T3"}] ${ex.sku_id} — ${ex.exception_type}`)
      lines.push(`  severity: ${ex.severity_score} | ${ex.one_line_diagnosis}`)
    })
    if (data.tier1_actions_taken?.length) {
      lines.push(`Auto-executed: ${data.tier1_actions_taken.length} action(s)`)
    }
  } else if (name === "rca_diagnostic") {
    lines.push(`Root cause: ${data.root_cause_layer?.toUpperCase()}`)
    lines.push(`Confidence: ${data.confidence}`)
    lines.push(data.root_cause_summary)
    lines.push(`Downstream: ${data.downstream_trigger}`)
  } else if (name === "retrain_override") {
    lines.push(`Recommendation: ${data.recommendation_type?.toUpperCase()}`)
    lines.push(`Confidence: ${data.confidence}`)
    lines.push(data.decision_rationale)
  }

  return (
    <div className="agent-block" style={{ borderLeftColor: color }}>
      <div className="agent-name" style={{ color }}>{name.replace(/_/g, " ")}</div>
      {lines.map((l, i) => (
        <div key={i} className="agent-line">{l}</div>
      ))}
    </div>
  )
}

const AGENT_ORDER = [
  ["trigger_router",   "#7F77DD"],
  ["exception_triage", "#1D9E75"],
  ["rca_diagnostic",   "#D85A30"],
  ["retrain_override", "#BA7517"],
]

export default function AgentPanel({ results, loading }) {
  return (
    <div className="panel panel-agent">
      <div className="panel-header">Agent reasoning</div>
      <div className="panel-body">
        {loading && (
          <div className="loading-state">
            <div className="pulse-row">
              {AGENT_ORDER.map(([name, color]) => (
                <div key={name} className="pulse-chip" style={{ background: color + "22", borderColor: color }}>
                  {name.replace(/_/g, " ")}
                </div>
              ))}
            </div>
            <div className="loading-hint">Agents reasoning via Claude API...</div>
          </div>
        )}
        {!loading && !results && (
          <div className="empty-state">Run a cycle to see agent reasoning traces</div>
        )}
        {results && AGENT_ORDER.map(([name, color]) => (
          <AgentBlock key={name} name={name} data={results[name]} color={color} />
        ))}
      </div>
    </div>
  )
}
