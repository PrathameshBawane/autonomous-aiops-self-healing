import { useState, useEffect } from "react"
import axios from "axios"

const API = "http://localhost:8000/api"

const agentSteps = [
  { key: "sentry", label: "Sentry", icon: "📡", desc: "Detecting faults" },
  { key: "librarian", label: "Librarian", icon: "📚", desc: "Finding solutions" },
  { key: "architect", label: "Architect", icon: "🔧", desc: "Writing patch" },
  { key: "safety_officer", label: "Safety Officer", icon: "🛡️", desc: "Reviewing patch" },
  { key: "docker", label: "Docker Sandbox", icon: "🐳", desc: "Testing patch" },
  { key: "human_approval", label: "Human Approval", icon: "👤", desc: "Awaiting decision" },
]

function AgentCard({ agent, currentAgent, status }) {
  const isDone = agentSteps.findIndex(a => a.key === currentAgent) >
                 agentSteps.findIndex(a => a.key === agent.key)
  const isActive = currentAgent === agent.key
  const isPending = !isDone && !isActive

  return (
    <div style={{
      padding: "16px",
      borderRadius: "12px",
      border: `2px solid ${isActive ? "#6366f1" : isDone ? "#22c55e" : "#334155"}`,
      background: isActive ? "#1e1b4b" : isDone ? "#052e16" : "#0f172a",
      display: "flex",
      alignItems: "center",
      gap: "12px",
      transition: "all 0.3s"
    }}>
      <span style={{ fontSize: "28px" }}>{agent.icon}</span>
      <div>
        <div style={{
          color: isActive ? "#a5b4fc" : isDone ? "#86efac" : "#94a3b8",
          fontWeight: "bold",
          fontSize: "15px"
        }}>
          {agent.label}
          {isActive && <span style={{ marginLeft: "8px", color: "#f59e0b" }}>● Running...</span>}
          {isDone && <span style={{ marginLeft: "8px", color: "#22c55e" }}>✓ Done</span>}
        </div>
        <div style={{ color: "#475569", fontSize: "13px" }}>{agent.desc}</div>
      </div>
    </div>
  )
}

export default function App() {
  const [status, setStatus] = useState(null)
  const [activeTab, setActiveTab] = useState("pipeline")
  const [loading, setLoading] = useState(false)

  // Poll status every 3 seconds
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const res = await axios.get(`${API}/status`)
        setStatus(res.data)
      } catch (e) {}
    }, 3000)
    fetchStatus()
    return () => clearInterval(interval)
  }, [])

  const fetchStatus = async () => {
    const res = await axios.get(`${API}/status`)
    setStatus(res.data)
  }

  const startPipeline = async () => {
    setLoading(true)
    await axios.post(`${API}/start`)
    setLoading(false)
  }

  const handleApproval = async (action) => {
    await axios.post(`${API}/approve`, { action })
    fetchStatus()
  }

  const resetPipeline = async () => {
    await axios.post(`${API}/reset`)
    fetchStatus()
  }

  if (!status) return (
    <div style={{ background: "#020617", minHeight: "100vh",
      display: "flex", alignItems: "center", justifyContent: "center",
      color: "white", fontSize: "20px" }}>
      Loading AIOps Dashboard...
    </div>
  )

  const statusColor = {
    idle: "#94a3b8",
    running: "#f59e0b",
    awaiting_approval: "#6366f1",
    approved: "#22c55e",
    rejected: "#ef4444",
    error: "#ef4444"
  }[status.status] || "#94a3b8"

  return (
    <div style={{ background: "#020617", minHeight: "100vh",
      color: "white", fontFamily: "monospace", padding: "24px" }}>

      {/* Header */}
      <div style={{ marginBottom: "24px", borderBottom: "1px solid #1e293b",
        paddingBottom: "16px" }}>
        <h1 style={{ margin: 0, fontSize: "22px", color: "#a5b4fc" }}>
          🤖 AIOps Self-Healing Dashboard
        </h1>
        <div style={{ marginTop: "8px", display: "flex",
          alignItems: "center", gap: "12px" }}>
          <span style={{ color: statusColor, fontWeight: "bold" }}>
            ● {status.status.toUpperCase()}
          </span>
          {status.current_agent && (
            <span style={{ color: "#475569" }}>
              → {status.current_agent}
            </span>
          )}
        </div>
      </div>

      {/* Control Buttons */}
      <div style={{ display: "flex", gap: "12px", marginBottom: "24px" }}>
        <button onClick={startPipeline} disabled={status.status === "running" || loading}
          style={{ padding: "10px 20px", borderRadius: "8px", border: "none",
            background: status.status === "running" ? "#334155" : "#6366f1",
            color: "white", cursor: "pointer", fontFamily: "monospace",
            fontSize: "14px", fontWeight: "bold" }}>
          {loading ? "Starting..." : "🚀 Start Pipeline"}
        </button>
        <button onClick={resetPipeline}
          style={{ padding: "10px 20px", borderRadius: "8px",
            border: "1px solid #334155", background: "transparent",
            color: "#94a3b8", cursor: "pointer", fontFamily: "monospace",
            fontSize: "14px" }}>
          🔄 Reset
        </button>
      </div>

      {/* Tabs */}
      <div style={{ display: "flex", gap: "4px", marginBottom: "20px" }}>
        {["pipeline", "diagnosis", "patch", "logs"].map(tab => (
          <button key={tab} onClick={() => setActiveTab(tab)}
            style={{ padding: "8px 16px", borderRadius: "8px", border: "none",
              background: activeTab === tab ? "#1e293b" : "transparent",
              color: activeTab === tab ? "#a5b4fc" : "#475569",
              cursor: "pointer", fontFamily: "monospace",
              fontSize: "13px", textTransform: "capitalize" }}>
            {tab}
          </button>
        ))}
      </div>

      {/* Pipeline Tab */}
      {activeTab === "pipeline" && (
        <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
          {agentSteps.map(agent => (
            <AgentCard key={agent.key} agent={agent}
              currentAgent={status.current_agent} status={status.status} />
          ))}

          {/* Human Approval Buttons */}
          {status.status === "awaiting_approval" && (
            <div style={{ marginTop: "16px", padding: "20px",
              borderRadius: "12px", border: "2px solid #6366f1",
              background: "#0f172a", textAlign: "center" }}>
              <p style={{ color: "#a5b4fc", marginBottom: "16px", fontSize: "16px" }}>
                👤 Patch ready for approval!
              </p>
              <div style={{ display: "flex", gap: "12px", justifyContent: "center" }}>
                <button onClick={() => handleApproval("approve")}
                  style={{ padding: "12px 28px", borderRadius: "8px",
                    border: "none", background: "#22c55e", color: "white",
                    cursor: "pointer", fontSize: "15px",
                    fontWeight: "bold", fontFamily: "monospace" }}>
                  ✅ Apply Fix
                </button>
                <button onClick={() => handleApproval("reject")}
                  style={{ padding: "12px 28px", borderRadius: "8px",
                    border: "none", background: "#ef4444", color: "white",
                    cursor: "pointer", fontSize: "15px",
                    fontWeight: "bold", fontFamily: "monospace" }}>
                  ❌ Reject
                </button>
              </div>
            </div>
          )}

          {/* Final Status */}
          {(status.status === "approved" || status.status === "rejected") && (
            <div style={{ marginTop: "16px", padding: "20px",
              borderRadius: "12px", textAlign: "center",
              background: status.status === "approved" ? "#052e16" : "#1c0a09",
              border: `2px solid ${status.status === "approved" ? "#22c55e" : "#ef4444"}` }}>
              <p style={{ fontSize: "20px", margin: 0,
                color: status.status === "approved" ? "#86efac" : "#fca5a5" }}>
                {status.status === "approved"
                  ? "🎉 System Self-Healed Successfully!"
                  : "❌ Patch Rejected — Manual intervention required"}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Diagnosis Tab */}
      {activeTab === "diagnosis" && (
        <div style={{ background: "#0f172a", borderRadius: "12px",
          padding: "20px", border: "1px solid #1e293b" }}>
          <h3 style={{ color: "#a5b4fc", marginTop: 0 }}>🤖 Sentry Diagnosis</h3>
          <pre style={{ color: "#94a3b8", whiteSpace: "pre-wrap",
            fontSize: "13px", lineHeight: "1.6" }}>
            {status.diagnosis || "No diagnosis yet — run the pipeline first"}
          </pre>
        </div>
      )}

      {/* Patch Tab */}
      {activeTab === "patch" && (
        <div style={{ background: "#0f172a", borderRadius: "12px",
          padding: "20px", border: "1px solid #1e293b" }}>
          <h3 style={{ color: "#a5b4fc", marginTop: 0 }}>
            🔧 Generated Patch
            {status.patch_path && (
              <span style={{ color: "#475569", fontSize: "13px",
                marginLeft: "12px" }}>
                {status.patch_path}
              </span>
            )}
          </h3>
          <pre style={{ color: "#86efac", whiteSpace: "pre-wrap",
            fontSize: "12px", lineHeight: "1.6", overflowX: "auto" }}>
            {status.patch_code || "No patch generated yet"}
          </pre>
        </div>
      )}

      {/* Logs Tab */}
      {activeTab === "logs" && (
        <div style={{ background: "#0f172a", borderRadius: "12px",
          padding: "20px", border: "1px solid #1e293b" }}>
          <h3 style={{ color: "#a5b4fc", marginTop: 0 }}>📋 Server Logs</h3>
          <pre style={{ color: "#fbbf24", whiteSpace: "pre-wrap",
            fontSize: "12px", lineHeight: "1.6", maxHeight: "400px",
            overflowY: "auto" }}>
            {status.logs || "No logs yet"}
          </pre>
        </div>
      )}

    </div>
  )
}