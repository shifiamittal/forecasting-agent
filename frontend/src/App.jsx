import { useState } from "react"
import ScenarioPanel from "./components/ScenarioPanel"
import AgentPanel from "./components/AgentPanel"
import RagPanel from "./components/RagPanel"
import OutputPanel from "./components/OutputPanel"
import "./App.css"

const API_BASE = "http://127.0.0.1:8000"

export default function App() {
  const [scenario, setScenario] = useState("hersheys_cycle_47")
  const [role, setRole] = useState("DS")
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)

  async function runCycle() {
    setLoading(true)
    setResults(null)
    setError(null)
    try {
      const res = await fetch(`${API_BASE}/api/run-cycle`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scenario_id: scenario, user_role: role }),
      })
      const data = await res.json()
      if (data.status === "error") {
        setError(data.detail)
      } else {
        setResults(data.results)
      }
    } catch (e) {
      setError("Cannot reach backend. Is uvicorn running on port 8000?")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-left">
          <span className="header-logo">Keystone</span>
          <span className="header-title">Forecasting Agent</span>
        </div>
        <div className="header-right">
          <span className="header-badge">
            {role === "DS" ? "Data Scientist" : "Planner"} view
          </span>
          <span className="header-badge scenario-badge">
            {scenario === "hersheys_cycle_47" ? "HERSHEYS" : "CORNING"}
          </span>
        </div>
      </header>

      <div className="panels">
        <ScenarioPanel
          scenario={scenario}
          setScenario={setScenario}
          role={role}
          setRole={setRole}
          onRun={runCycle}
          loading={loading}
        />
        <AgentPanel results={results} loading={loading} />
        <RagPanel results={results} loading={loading} role={role} />
        <OutputPanel results={results} loading={loading} />
      </div>

      {error && (
        <div className="error-bar">
          {error}
        </div>
      )}
    </div>
  )
}
