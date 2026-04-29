function TierBadge({ tier }) {
  const styles = {
    1: { bg: "#EAF3DE", color: "#3B6D11", label: "T1 autonomous" },
    2: { bg: "#FAEEDA", color: "#854F0B", label: "T2 approve" },
    3: { bg: "#FCEBEB", color: "#A32D2D", label: "T3 surface" },
  }
  const s = styles[tier] || styles[2]
  return (
    <span className="tier-badge" style={{ background: s.bg, color: s.color }}>
      {s.label}
    </span>
  )
}

function EvalBar({ score, label }) {
  const pct = Math.round(score * 100)
  const color = score >= 0.9 ? "#3B6D11" : score >= 0.7 ? "#854F0B" : "#A32D2D"
  return (
    <div className="eval-row">
      <span className="eval-label">{label}</span>
      <div className="eval-track">
        <div className="eval-fill" style={{ width: `${pct}%`, background: color }} />
      </div>
      <span className="eval-score" style={{ color }}>{score.toFixed(2)}</span>
    </div>
  )
}

export default function OutputPanel({ results, loading }) {
  const rca     = results?.rca_diagnostic
  const retrain = results?.retrain_override
  const evalOut = results?.rca_eval
  const triage  = results?.exception_triage

  const allTierActions = []
  if (rca?.tier_actions) {
    rca.tier_actions.tier_1?.forEach(a => allTierActions.push({ tier: 1, text: a }))
    rca.tier_actions.tier_2?.forEach(a => allTierActions.push({ tier: 2, text: a }))
    rca.tier_actions.tier_3?.forEach(a => allTierActions.push({ tier: 3, text: a }))
  }
  if (retrain?.tier_actions) {
    retrain.tier_actions.tier_2?.forEach(a => allTierActions.push({ tier: 2, text: a }))
    retrain.tier_actions.tier_3?.forEach(a => allTierActions.push({ tier: 3, text: a }))
  }

  return (
    <div className="panel panel-output">
      <div className="panel-header">Output + eval</div>
      <div className="panel-body">
        {!results && !loading && (
          <div className="empty-state">Actions and eval scores will appear here</div>
        )}
        {loading && (
          <div className="empty-state">Generating outputs...</div>
        )}

        {results && rca && (
          <>
            <div className="output-section-label">RCA result</div>
            <div className="rca-summary">
              <div className="rca-row">
                <span className="rca-key">Root cause</span>
                <span className="rca-val layer-badge">{rca.root_cause_layer}</span>
              </div>
              <div className="rca-row">
                <span className="rca-key">Confidence</span>
                <span className="rca-val">{rca.confidence}</span>
              </div>
              <div className="rca-row">
                <span className="rca-key">Downstream</span>
                <span className="rca-val">{rca.downstream_trigger}</span>
              </div>
            </div>

            {allTierActions.length > 0 && (
              <>
                <div className="output-section-label" style={{ marginTop: "16px" }}>
                  Actions
                </div>
                {allTierActions.map((a, i) => (
                  <div key={i} className="action-item">
                    <TierBadge tier={a.tier} />
                    <span className="action-text">{a.text}</span>
                  </div>
                ))}
              </>
            )}

            {evalOut && (
              <>
                <div className="output-section-label" style={{ marginTop: "16px" }}>
                  Eval scores
                </div>
                <EvalBar
                  score={evalOut.diagnostic_faithfulness?.score ?? 0}
                  label="Faithfulness"
                />
                <EvalBar
                  score={evalOut.layer_sequence_compliance?.score ?? 0}
                  label="Layer sequence"
                />
                <EvalBar
                  score={evalOut.tier_classification_accuracy?.score ?? 0}
                  label="Tier accuracy"
                />
                <div className="eval-overall">
                  Overall {evalOut.overall_score?.toFixed(2)}
                  <span className={`action-chip ${evalOut.action_required === "none" ? "chip-ok" : "chip-warn"}`}>
                    {evalOut.action_required}
                  </span>
                </div>
                {evalOut.improvement_note && (
                  <div className="improvement-note">{evalOut.improvement_note}</div>
                )}
              </>
            )}

            {retrain && (
              <>
                <div className="output-section-label" style={{ marginTop: "16px" }}>
                  Retrain / override
                </div>
                <div className="rca-summary">
                  <div className="rca-row">
                    <span className="rca-key">Recommendation</span>
                    <span className="rca-val">{retrain.recommendation_type}</span>
                  </div>
                  <div className="rca-row">
                    <span className="rca-key">Confidence</span>
                    <span className="rca-val">{retrain.confidence}</span>
                  </div>
                  <div className="rca-row">
                    <span className="rca-key">Expected lift</span>
                    <span className="rca-val">{retrain.expected_accuracy_lift}</span>
                  </div>
                </div>
              </>
            )}
          </>
        )}
      </div>
    </div>
  )
}
