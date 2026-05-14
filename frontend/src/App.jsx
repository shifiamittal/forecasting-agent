import { useState, useEffect } from 'react'
import Sidebar from './components/Sidebar'
import Topbar from './components/Topbar'
import PlannerPanel from './components/panels/PlannerPanel'
import ReasoningPanel from './components/panels/ReasoningPanel'
import RagPanel from './components/panels/RagPanel'
import EvalPanel from './components/panels/EvalPanel'
import './App.css'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function App() {
  const [clients, setClients] = useState([])
  const [selectedClient, setSelectedClient] = useState('HERSHEYS')
  const [cycleData, setCycleData] = useState(null)
  const [selectedExcId, setSelectedExcId] = useState(null)
  const [activeTab, setActiveTab] = useState('planner')
  const [isRunning, setIsRunning] = useState(false)
  const [pipelineProgress, setPipelineProgress] = useState(null)

  useEffect(() => {
    fetch(`${API_BASE}/api/clients`)
      .then(r => {
        if (!r.ok) throw new Error(`/api/clients returned ${r.status}`)
        return r.json()
      })
      .then(data => {
        if (Array.isArray(data)) setClients(data)
        else console.error('/api/clients did not return an array:', data)
      })
      .catch(console.error)
  }, [])

  useEffect(() => {
    setCycleData(null)
    setSelectedExcId(null)
    fetch(`${API_BASE}/api/fixture/${selectedClient}`)
      .then(r => r.json())
      .then(setCycleData)
      .catch(console.error)
  }, [selectedClient])

  function runLive() {
    setIsRunning(true)
    setPipelineProgress({ step: 0, total: 5, agent_name: 'Starting pipeline…', message: '' })

    const es = new EventSource(`${API_BASE}/api/run-stream/${selectedClient}`)

    es.onmessage = (event) => {
      const msg = JSON.parse(event.data)

      if (msg.type === 'agent_start') {
        setPipelineProgress({
          step:       msg.step,
          total:      msg.total_agents ?? 5,
          agent_name: msg.agent_name,
          message:    msg.message,
        })
      }

      if (msg.type === 'complete') {
        es.close()
        setCycleData(msg.data)
        setSelectedExcId(null)
        setPipelineProgress(null)
        setIsRunning(false)
      }

      if (msg.type === 'error') {
        console.error('Pipeline stream error:', msg.message)
      }
    }

    es.onerror = () => {
      es.close()
      console.error('SSE connection lost — pipeline may still be running')
      setPipelineProgress(null)
      setIsRunning(false)
    }
  }

  const selectedExc = cycleData?.exceptions?.find(e => e.id === selectedExcId) ?? null

  return (
    <div className="shell">
      <Sidebar
        clients={clients}
        selectedClient={selectedClient}
        onSelectClient={setSelectedClient}
        cycleData={cycleData}
        isRunning={isRunning}
        onRun={runLive}
        pipelineProgress={pipelineProgress}
      />
      <Topbar
        activeTab={activeTab}
        onTabChange={setActiveTab}
        selectedExc={selectedExc}
        cycleData={cycleData}
        selectedClient={selectedClient}
      />
      <main className="main">
        <div className={`panel${activeTab === 'planner' ? ' active' : ''}`}>
          <PlannerPanel
            cycleData={cycleData}
            selectedExcId={selectedExcId}
            onSelectExc={setSelectedExcId}
          />
        </div>
        <div className={`panel${activeTab === 'reasoning' ? ' active' : ''}`}>
          <ReasoningPanel selectedExc={selectedExc} />
        </div>
        <div className={`panel${activeTab === 'rag' ? ' active' : ''}`}>
          <RagPanel selectedExc={selectedExc} />
        </div>
        <div className={`panel${activeTab === 'eval' ? ' active' : ''}`}>
          <EvalPanel selectedExc={selectedExc} />
        </div>
      </main>
    </div>
  )
}
