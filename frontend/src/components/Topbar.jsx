const TABS = [
  { id: 'planner',   label: 'Planner view' },
  { id: 'reasoning', label: 'Agent reasoning' },
  { id: 'rag',       label: 'RAG retrieval' },
  { id: 'eval',      label: 'Eval scores' },
]

const ROLE = {
  HERSHEYS: { label: 'Demand Planner', cls: 'rp-planner' },
  MICHELIN:  { label: 'Demand Planner', cls: 'rp-planner' },
  CORNING:   { label: 'Data Scientist', cls: 'rp-ds' },
}

export default function Topbar({ activeTab, onTabChange, selectedExc, cycleData, selectedClient }) {
  const role = ROLE[selectedClient] ?? { label: 'Demand Planner', cls: 'rp-planner' }
  const cycleId = cycleData?.cycle?.cycle_id
  const source = cycleData?.source

  return (
    <header className="topbar">
      {TABS.map(t => (
        <button
          key={t.id}
          className={`tab${activeTab === t.id ? ' active' : ''}`}
          onClick={() => onTabChange(t.id)}
        >
          {t.label}
        </button>
      ))}
      <div className="topbar-right">
        {selectedExc && (
          <span className="selected-exc-pill">{selectedExc.sku}</span>
        )}
        {cycleId && <span className="cycle-pill">Cycle {cycleId}</span>}
        {source && (
          <span className={`source-pill${source === 'live' ? ' source-live' : ' source-fixture'}`}>
            {source === 'live' ? 'Live run' : 'Fixture data'}
          </span>
        )}
        <span className={`role-pill ${role.cls}`}>{role.label}</span>
      </div>
    </header>
  )
}
