import { useState, useEffect } from 'react'
import api from '../api.js'

function formatDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleString()
}

function isToday(iso) {
  if (!iso) return false
  const d = new Date(iso)
  const now = new Date()
  return d.getFullYear() === now.getFullYear() &&
    d.getMonth() === now.getMonth() &&
    d.getDate() === now.getDate()
}

function isThisWeek(iso) {
  if (!iso) return false
  const d = new Date(iso)
  const now = new Date()
  const weekFromNow = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000)
  return d >= now && d <= weekFromNow
}

const EMAIL_TYPE_LABELS = {
  initial: 'Initial',
  followup1: 'Follow-up 1',
  followup2: 'Follow-up 2',
}

export default function SendQueue() {
  const [queue, setQueue] = useState([])
  const [logs, setLogs] = useState([])
  const [loadingQueue, setLoadingQueue] = useState(true)
  const [loadingLogs, setLoadingLogs] = useState(true)
  const [filter, setFilter] = useState('all') // today | week | all
  const [actionMsgs, setActionMsgs] = useState({})
  const [error, setError] = useState(null)

  async function fetchQueue() {
    setLoadingQueue(true)
    try {
      const res = await api.get('/emails/queue')
      setQueue(res.data.data || [])
    } catch (e) {
      setError(e.message)
    } finally {
      setLoadingQueue(false)
    }
  }

  async function fetchLogs() {
    setLoadingLogs(true)
    try {
      const res = await api.get('/emails/logs')
      setLogs(res.data.data || [])
    } catch (e) {
      // silently fail
    } finally {
      setLoadingLogs(false)
    }
  }

  useEffect(() => { fetchQueue(); fetchLogs() }, [])

  function setMsg(id, msg) {
    setActionMsgs(m => ({ ...m, [id]: msg }))
    if (msg?.type === 'success') {
      setTimeout(() => {
        setActionMsgs(m => { const n = { ...m }; delete n[id]; return n })
        fetchQueue()
        fetchLogs()
      }, 1500)
    }
  }

  async function sendNow(item) {
    setMsg(item.id, { type: 'loading', text: 'Sending...' })
    try {
      const res = await api.post('/emails/send-followup', { scheduled_email_id: item.id })
      setMsg(item.id, { type: 'success', text: res.data.message })
    } catch (e) {
      setMsg(item.id, { type: 'error', text: e.message })
    }
  }

  async function cancelScheduled(item) {
    if (!window.confirm(`Cancel follow-up to ${item.lead_name}?`)) return
    setMsg(item.id, { type: 'loading', text: 'Cancelling...' })
    try {
      await api.delete(`/emails/scheduled/${item.id}`)
      setMsg(item.id, { type: 'success', text: 'Cancelled' })
    } catch (e) {
      setMsg(item.id, { type: 'error', text: e.message })
    }
  }

  const filteredQueue = queue.filter(item => {
    if (filter === 'today') return isToday(item.scheduled_for)
    if (filter === 'week') return isThisWeek(item.scheduled_for)
    return true
  })

  return (
    <div>
      <div className="page-header">
        <div>
          <h2>Send Queue</h2>
          <p>{queue.length} pending scheduled emails</p>
        </div>
        <button className="btn btn-secondary" onClick={() => { fetchQueue(); fetchLogs() }}>
          🔄 Refresh
        </button>
      </div>

      {error && <div className="alert alert-error mb-16">{error}</div>}

      {/* Queue */}
      <div className="card mb-24">
        <div className="flex-between mb-16">
          <div className="section-title" style={{ margin: 0 }}>Scheduled Emails</div>
          <div className="tabs" style={{ border: 'none', marginBottom: 0 }}>
            {[['all', 'All Pending'], ['today', 'Due Today'], ['week', 'This Week']].map(([key, label]) => (
              <button
                key={key}
                className={`tab-btn ${filter === key ? 'active' : ''}`}
                onClick={() => setFilter(key)}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        {loadingQueue ? (
          <div className="loading-spinner"><div className="spinner" /> Loading queue...</div>
        ) : filteredQueue.length === 0 ? (
          <div className="empty-state" style={{ padding: '32px' }}>
            <div className="empty-icon">📭</div>
            <h3>No scheduled emails</h3>
            <p>Send an initial email to a lead to schedule follow-ups</p>
          </div>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Lead</th>
                  <th>Email</th>
                  <th>Type</th>
                  <th>Scheduled For</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredQueue.map(item => {
                  const msg = actionMsgs[item.id]
                  return (
                    <tr key={item.id}>
                      <td><strong>{item.lead_name}</strong></td>
                      <td className="td-muted">{item.lead_email || '—'}</td>
                      <td>
                        <span className="badge badge-contacted">
                          {EMAIL_TYPE_LABELS[item.email_type] || item.email_type}
                        </span>
                      </td>
                      <td className="td-muted">
                        <span style={isToday(item.scheduled_for) ? { color: 'var(--warning)', fontWeight: 600 } : {}}>
                          {formatDate(item.scheduled_for)}
                        </span>
                      </td>
                      <td>
                        <span className="badge badge-new">{item.status}</span>
                      </td>
                      <td>
                        {msg ? (
                          <span className={`text-${msg.type === 'success' ? 'success' : msg.type === 'error' ? 'danger' : 'muted'}`} style={{ fontSize: 12 }}>
                            {msg.text}
                          </span>
                        ) : (
                          <div className="td-actions">
                            <button className="btn btn-xs btn-primary" onClick={() => sendNow(item)}>
                              Send Now
                            </button>
                            <button className="btn btn-xs btn-danger" onClick={() => cancelScheduled(item)}>
                              Cancel
                            </button>
                          </div>
                        )}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Logs */}
      <div className="card">
        <div className="section-title mb-16">Email Logs (Last 50)</div>

        {loadingLogs ? (
          <div className="loading-spinner"><div className="spinner" /> Loading logs...</div>
        ) : logs.length === 0 ? (
          <div className="empty-state" style={{ padding: '32px' }}>
            <div className="empty-icon">📝</div>
            <h3>No emails sent yet</h3>
          </div>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Lead</th>
                  <th>Type</th>
                  <th>Subject</th>
                  <th>Sent At</th>
                  <th>Status</th>
                  <th>Error</th>
                </tr>
              </thead>
              <tbody>
                {logs.map(log => (
                  <tr key={log.id}>
                    <td><strong>{log.lead_name}</strong></td>
                    <td>
                      <span className="badge badge-new">
                        {EMAIL_TYPE_LABELS[log.email_type] || log.email_type}
                      </span>
                    </td>
                    <td className="td-muted" style={{ maxWidth: 260 }}>
                      <span className="truncate" style={{ maxWidth: 260 }}>{log.subject}</span>
                    </td>
                    <td className="td-muted">{formatDate(log.sent_at)}</td>
                    <td>
                      <span className={`badge ${log.status === 'sent' ? 'badge-replied' : 'badge-not-interested'}`}>
                        {log.status}
                      </span>
                    </td>
                    <td className="td-muted" style={{ fontSize: 11, color: 'var(--danger)', maxWidth: 200 }}>
                      {log.error_msg ? <span className="truncate" style={{ maxWidth: 200 }}>{log.error_msg}</span> : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
