function ChunkCard({ result, index }) {
  const typeColors = {
    incident_record:   "#D85A30",
    readiness_report:  "#BA7517",
    override_decision: "#1D9E75",
    retrain_decision:  "#7F77DD",
    trade_calendar:    "#185FA5",
  }
  const color = typeColors[result.source_type] || "#888"

  return (
    <div className="chunk-card">
      <div className="chunk-header">
        <span className="chunk-id">{result.doc_id}</span>
        <span className="chunk-type" style={{ background: color + "22", color }}>
          {result.source_type?.replace(/_/g, " ")}
        </span>
        <span className="chunk-score">{result.relevance_score}</span>
      </div>
      <div className="chunk-date">{result.date}</div>
      <div className="chunk-content">{result.content?.slice(0, 220)}...</div>
    </div>
  )
}

export default function RagPanel({ results, loading, role }) {
  const rca = results?.rca_diagnostic
  const triage = results?.exception_triage

  const ragMeta = results ? {
    intent: "data_issue",
    source_types: ["incident_record", "readiness_report"],
    role,
    note: "Pre-filter → semantic search → re-rank"
  } : null

  const sampleChunks = results ? [
    {
      doc_id: "INC-001",
      source_type: "incident_record",
      date: "2024-03-15",
      relevance_score: 0.941,
      content: "Incident INC-001: Kroger POS feed failure for chocolate seasonal SKUs. Symptom: wMAPE degraded 3.8 points on chocolate_seasonal segment, cycle 31. Investigation: Kroger POS ingestion job failed due to connection timeout in Argo workflow. Feed was stale for 11 days."
    },
    {
      doc_id: "RR-001",
      source_type: "readiness_report",
      date: "2024-03-14",
      relevance_score: 0.887,
      content: "Data Readiness Report RR-001 | Run: hersheys_cycle_31 | Verdict: BLOCKED. Schema validation: APPROVED. Feed freshness: BLOCKED — Kroger POS feed stale 11 days. Temporal integrity: BLOCKED — 18 chocolate seasonal SKUs missing 11 days of actuals at Kroger."
    },
    {
      doc_id: "OVR-003",
      source_type: "override_decision",
      date: "2024-02-08",
      relevance_score: 0.743,
      content: "Override Decision OVR-003 | Approved by: planner_hersheys_lead | Segment: chocolate_seasonal | Cycle: 6 | Correction: +16% applied to Valentine's Day chocolate SKUs. Outcome: forecast error reduced from -19% to -3%."
    },
  ] : []

  return (
    <div className="panel panel-rag">
      <div className="panel-header">RAG context</div>
      <div className="panel-body">
        {!results && !loading && (
          <div className="empty-state">Retrieved chunks will appear here</div>
        )}
        {loading && (
          <div className="empty-state">Retrieving from Qdrant...</div>
        )}
        {results && (
          <>
            <div className="rag-meta">
              <div className="meta-row">
                <span className="meta-key">Intent</span>
                <span className="meta-val intent-badge">data_issue</span>
              </div>
              <div className="meta-row">
                <span className="meta-key">Role filter</span>
                <span className="meta-val">{role}</span>
              </div>
              <div className="meta-row">
                <span className="meta-key">Pipeline</span>
                <span className="meta-val">pre-filter → semantic → re-rank</span>
              </div>
            </div>
            <div className="chunk-label">Top retrieved chunks</div>
            {sampleChunks.map((c, i) => <ChunkCard key={i} result={c} index={i} />)}
            <div className="permission-note">
              {role === "planner"
                ? "Planner role: model eval logs and retrain decisions excluded"
                : role === "DS"
                ? "DS role: full access to all source types"
                : "Engineering role: pipeline logs and incidents only"}
            </div>
          </>
        )}
      </div>
    </div>
  )
}
