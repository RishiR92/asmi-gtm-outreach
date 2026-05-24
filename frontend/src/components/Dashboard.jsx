import { useState, useEffect, useRef } from 'react'
import api from '../api.js'

const STATUS_COLORS = {
  'New':              '#64748b',
  'Email Found':      '#2563eb',
  'Contacted':        '#d97706',
  'Replied':          '#059669',
  'Feature Confirmed':'#047857',
  'Not Interested':   '#dc2626',
  'No Response':      '#ea580c',
}

function timeAgo(isoStr) {
  if (!isoStr) return ''
  const diff = Date.now() - new Date(isoStr + 'Z').getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1)  return 'just now'
  if (mins < 60) return `${mins}m ago`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24)  return `${hrs}h ago`
  return `${Math.floor(hrs / 24)}d ago`
}

function fmtAudience(n) {
  if (!n) return '—'
  if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M'
  if (n >= 1000)    return Math.round(n / 1000) + 'K'
  return n
}

function ScoreBadge({ score }) {
  const pct  = Math.min(100, Math.round((score / 95) * 100))
  const color = pct >= 70 ? '#059669' : pct >= 45 ? '#d97706' : '#64748b'
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 4,
      fontSize: 11, fontWeight: 700, color,
      background: color + '18', borderRadius: 6, padding: '2px 7px',
    }}>
      {score}
    </span>
  )
}

// ─── Autopilot Status Banner ─────────────────────────────────────────────────
function AutopilotBanner({ apStatus, onToggle, onRunNow, running }) {
  const on = apStatus?.autopilot_enabled
  return (
    <div style={{
      background:   on ? 'linear-gradient(135deg,#064e3b,#065f46)' : 'linear-gradient(135deg,#1e293b,#334155)',
      borderRadius: 12, padding: '20px 24px', marginBottom: 20,
      display: 'flex', alignItems: 'center', gap: 20, flexWrap: 'wrap',
      border: on ? '1px solid #059669' : '1px solid #475569',
    }}>
      {/* Status dot + label */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, flex: 1 }}>
        <div style={{
          width: 12, height: 12, borderRadius: '50%',
          background: on ? '#34d399' : '#64748b',
          boxShadow:  on ? '0 0 8px #34d399' : 'none',
        }} />
        <div>
          <div style={{ color: '#f1f5f9', fontWeight: 700, fontSize: 15 }}>
            Autopilot {on ? 'ON' : 'OFF'}
          </div>
          <div style={{ color: '#94a3b8', fontSize: 12, marginTop: 2 }}>
            {on
              ? `Sending up to ${apStatus?.daily_limit ?? 20} emails/day · ${apStatus?.sent_today ?? 0} sent today · ${apStatus?.remaining_today ?? 0} remaining`
              : 'Enable to automatically send prioritised outreach every day'}
          </div>
        </div>
      </div>

      {/* Stats pills */}
      {on && (
        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
          {[
            ['Eligible leads', apStatus?.eligible_leads ?? 0],
            ['Sent today',     apStatus?.sent_today     ?? 0],
            ['Remaining',      apStatus?.remaining_today?? 0],
          ].map(([label, val]) => (
            <div key={label} style={{
              background: 'rgba(255,255,255,0.08)', borderRadius: 8,
              padding: '6px 14px', textAlign: 'center',
            }}>
              <div style={{ color: '#f1f5f9', fontWeight: 700, fontSize: 18 }}>{val}</div>
              <div style={{ color: '#94a3b8', fontSize: 11 }}>{label}</div>
            </div>
          ))}
        </div>
      )}

      {/* Actions */}
      <div style={{ display: 'flex', gap: 10 }}>
        <button
          className={`btn ${on ? 'btn-danger' : 'btn-primary'}`}
          style={{ minWidth: 110 }}
          onClick={() => onToggle(!on)}
        >
          {on ? '⏸ Pause' : '▶ Enable'}
        </button>
        {on && (
          <button
            className="btn btn-secondary"
            onClick={onRunNow}
            disabled={running}
            style={{ minWidth: 100 }}
          >
            {running ? '⏳ Sending…' : '⚡ Send Now'}
          </button>
        )}
      </div>
    </div>
  )
}

// ─── Quick Add Email ─────────────────────────────────────────────────────────
function QuickAddPanel({ onAdded }) {
  const [email, setEmail]   = useState('')
  const [name,  setName]    = useState('')
  const [msg,   setMsg]     = useState(null)
  const [loading, setLoad]  = useState(false)

  async function handleAdd(e) {
    e.preventDefault()
    if (!email.trim()) return
    setLoad(true); setMsg(null)
    try {
      const res = await api.post('/autopilot/quick-add', { email: email.trim(), name: name.trim() || undefined })
      setMsg({ type: 'success', text: `✓ ${res.data.message}` })
      setEmail(''); setName('')
      onAdded()
    } catch (err) {
      setMsg({ type: 'error', text: err.response?.data?.detail || err.message })
    } finally {
      setLoad(false)
    }
  }

  return (
    <div className="card mb-20" style={{ border: '1px solid #e2e8f0' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
        <span style={{ fontSize: 18 }}>⚡</span>
        <span style={{ fontWeight: 700, fontSize: 14, color: '#1e293b' }}>Quick Add Email</span>
        <span style={{ fontSize: 12, color: '#64748b', marginLeft: 4 }}>
          Paste an email → jumps to top of next send batch
        </span>
      </div>
      <form onSubmit={handleAdd} style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
        <input
          type="email"
          placeholder="influencer@newsletter.com"
          value={email}
          onChange={e => setEmail(e.target.value)}
          className="form-input"
          style={{ flex: 2, minWidth: 220 }}
          required
        />
        <input
          type="text"
          placeholder="Name (optional — auto-matched)"
          value={name}
          onChange={e => setName(e.target.value)}
          className="form-input"
          style={{ flex: 2, minWidth: 180 }}
        />
        <button type="submit" className="btn btn-primary" disabled={loading} style={{ minWidth: 90 }}>
          {loading ? '…' : '+ Add'}
        </button>
      </form>
      {msg && (
        <div style={{
          marginTop: 10, fontSize: 13, fontWeight: 500,
          color: msg.type === 'success' ? '#059669' : '#dc2626',
        }}>
          {msg.text}
        </div>
      )}
    </div>
  )
}

// ─── Today's Priority Queue ───────────────────────────────────────────────────
function TodaysQueue({ queue, loading }) {
  if (loading) return <div className="loading-spinner"><div className="spinner" /> Loading queue…</div>
  if (!queue?.length) return (
    <div className="empty-state" style={{ padding: 20 }}>
      <div className="empty-icon">✅</div>
      <p>All eligible leads have been contacted</p>
    </div>
  )
  return (
    <div className="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>Lead</th>
            <th>Audience</th>
            <th>Category</th>
            <th>Timezone</th>
            <th>Score</th>
            <th>Flag</th>
          </tr>
        </thead>
        <tbody>
          {queue.map((item, i) => (
            <tr key={item.lead_id}>
              <td style={{ color: '#94a3b8', fontWeight: 600 }}>{i + 1}</td>
              <td>
                <strong>{item.name}</strong>
                <div style={{ fontSize: 11, color: '#64748b' }}>{item.email}</div>
              </td>
              <td style={{ color: '#334155' }}>{fmtAudience(item.audience)}</td>
              <td>
                <span className="badge badge-new" style={{ fontSize: 10 }}>{item.category}</span>
              </td>
              <td style={{ fontSize: 12, color: '#64748b' }}>{item.timezone?.replace('America/', '').replace('_', ' ')}</td>
              <td><ScoreBadge score={item.score} /></td>
              <td>
                {item.priority
                  ? <span style={{ fontSize: 13 }} title="Manually prioritised">⚡</span>
                  : <span style={{ fontSize: 13, color: '#e2e8f0' }}>·</span>}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

// ─── Main Dashboard ───────────────────────────────────────────────────────────
export default function Dashboard() {
  const [stats,    setStats]    = useState(null)
  const [apStatus, setApStatus] = useState(null)
  const [queue,    setQueue]    = useState([])
  const [loading,  setLoading]  = useState(true)
  const [queueLoading, setQL]   = useState(true)
  const [error,    setError]    = useState(null)
  const [runMsg,   setRunMsg]   = useState(null)
  const [running,  setRunning]  = useState(false)

  async function fetchAll() {
    setLoading(true); setError(null)
    try {
      const [sRes, apRes] = await Promise.all([
        api.get('/dashboard/stats'),
        api.get('/autopilot/status'),
      ])
      setStats(sRes.data.data)
      setApStatus(apRes.data.data)
    } catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }

  async function fetchQueue() {
    setQL(true)
    try {
      const res = await api.get('/autopilot/queue')
      setQueue(res.data.data || [])
    } catch (_) {}
    finally { setQL(false) }
  }

  useEffect(() => { fetchAll(); fetchQueue() }, [])

  async function handleToggle(enabled) {
    try {
      await api.post('/autopilot/toggle', { enabled })
      await fetchAll()
    } catch (e) { alert(e.message) }
  }

  async function handleRunNow() {
    setRunning(true); setRunMsg(null)
    try {
      const res = await api.post('/autopilot/run-now')
      setRunMsg({ type: 'success', text: res.data.message })
      await fetchAll(); await fetchQueue()
    } catch (e) {
      setRunMsg({ type: 'error', text: e.response?.data?.detail || e.message })
    } finally {
      setRunning(false)
      setTimeout(() => setRunMsg(null), 4000)
    }
  }

  if (loading) return <div className="loading-spinner"><div className="spinner" /> Loading…</div>
  if (error)   return <div className="alert alert-error">{error}</div>
  if (!stats)  return null

  const byStatus = stats.by_status || {}
  const totalReach = (queue || []).reduce((s, l) => s + (l.audience || 0), 0)

  return (
    <div>
      {/* Header */}
      <div className="page-header">
        <div>
          <h2>Asmi GTM Dashboard</h2>
          <p>Autopilot cold outreach — prioritised by audience, timezone & score</p>
        </div>
        <button className="btn btn-secondary" onClick={() => { fetchAll(); fetchQueue() }}>🔄 Refresh</button>
      </div>

      {runMsg && (
        <div className={`alert ${runMsg.type === 'success' ? 'alert-success' : 'alert-error'} mb-16`}>
          {runMsg.text}
        </div>
      )}

      {/* Autopilot Banner */}
      <AutopilotBanner
        apStatus={apStatus}
        onToggle={handleToggle}
        onRunNow={handleRunNow}
        running={running}
      />

      {/* Quick Add */}
      <QuickAddPanel onAdded={() => { fetchAll(); fetchQueue() }} />

      {/* GTM Reach Metrics */}
      <div className="metrics-row mb-20">
        <div className="stat-card">
          <div className="stat-label">Total Audience Reach</div>
          <div className="stat-value" style={{ color: '#2563eb' }}>
            {fmtAudience(
              Object.values(byStatus).includes(0) ? 0 :
              queue.reduce((s, l) => s + (l.audience || 0), 0) +
              (stats.total_leads * 50000) // rough estimate for contacted
            )}
          </div>
          <div className="stat-sub">across all contacted + queued leads</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Emails Sent This Week</div>
          <div className="stat-value">{stats.emails_sent_this_week}</div>
          <div className="stat-sub">initial + follow-ups combined</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Reply Rate</div>
          <div className="stat-value" style={{ color: '#059669' }}>
            {(stats.reply_rate * 100).toFixed(1)}%
          </div>
          <div className="stat-sub">
            {(byStatus['Replied'] || 0) + (byStatus['Feature Confirmed'] || 0)} replied
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-label">In Queue Today</div>
          <div className="stat-value" style={{ color: '#d97706' }}>
            {apStatus?.eligible_leads ?? queue.length}
          </div>
          <div className="stat-sub">eligible leads with emails</div>
        </div>
      </div>

      {/* Pipeline */}
      <div className="section-title">Pipeline</div>
      <div className="status-grid mb-20">
        {['New','Email Found','Contacted','Replied','Feature Confirmed','Not Interested','No Response'].map(s => (
          <div className="status-card" key={s}>
            <div className="status-count" style={{ color: STATUS_COLORS[s] || '#334155' }}>
              {byStatus[s] || 0}
            </div>
            <div className="status-label">{s}</div>
          </div>
        ))}
        <div className="status-card">
          <div className="status-count" style={{ color: '#334155' }}>{stats.total_leads}</div>
          <div className="status-label">Total Leads</div>
        </div>
      </div>

      {/* Today's Queue */}
      <div className="card mb-20">
        <div className="section-title" style={{ marginBottom: 14 }}>
          🎯 Today's Priority Queue
          <span style={{
            marginLeft: 'auto', fontSize: 11, fontWeight: 600,
            color: '#2563eb', background: '#eff6ff',
            padding: '2px 8px', borderRadius: 6,
          }}>
            {queue.length} leads · sorted by score
          </span>
        </div>
        <TodaysQueue queue={queue} loading={queueLoading} />
      </div>

      {/* Follow-ups Due */}
      <div className="card mb-20">
        <div className="section-title">
          📅 Follow-ups Due Today
          <span className="badge badge-contacted" style={{ marginLeft: 'auto' }}>
            {stats.followups_due_today?.length || 0}
          </span>
        </div>
        {(!stats.followups_due_today?.length) ? (
          <div className="empty-state" style={{ padding: 20 }}>
            <div className="empty-icon">✅</div>
            <p>No follow-ups due today</p>
          </div>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr><th>Lead</th><th>Newsletter</th><th>Email</th><th>Type</th><th>Scheduled</th><th>Actions</th></tr>
              </thead>
              <tbody>
                {stats.followups_due_today.map(f => (
                  <tr key={f.scheduled_id}>
                    <td><strong>{f.lead_name}</strong></td>
                    <td className="td-muted">{f.newsletter_name}</td>
                    <td className="td-muted">{f.lead_email || '—'}</td>
                    <td>
                      <span className="badge badge-contacted">
                        {f.email_type === 'followup1' ? 'FU 1' : 'FU 2'}
                      </span>
                    </td>
                    <td className="td-muted">
                      {f.scheduled_for ? new Date(f.scheduled_for + 'Z').toLocaleString() : '—'}
                    </td>
                    <td><SendNowBtn scheduledId={f.scheduled_id} onDone={fetchAll} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Recent Activity */}
      <div className="card">
        <div className="section-title">Recent Activity</div>
        {(!stats.recent_activity?.length) ? (
          <div className="empty-state" style={{ padding: 20 }}>
            <div className="empty-icon">📭</div>
            <p>No emails sent yet</p>
          </div>
        ) : (
          <div className="activity-feed">
            {stats.recent_activity.map(item => (
              <div className="activity-item" key={item.id}>
                <div className={`activity-icon ${item.status}`}>
                  {item.status === 'sent' ? '✉️' : item.status === 'failed' ? '❌' : '📨'}
                </div>
                <div className="activity-info">
                  <strong>{item.lead_name}</strong>
                  <span>
                    {item.email_type === 'initial'   ? 'Initial email' :
                     item.email_type === 'followup1' ? 'Follow-up 1'   : 'Follow-up 2'}
                    {item.subject ? ` — "${item.subject}"` : ''}
                  </span>
                </div>
                <div className="activity-time">{timeAgo(item.sent_at)}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function SendNowBtn({ scheduledId, onDone }) {
  const [loading, setLoading] = useState(false)
  const [msg,     setMsg]     = useState(null)
  async function handleSend() {
    setLoading(true); setMsg(null)
    try {
      await api.post('/emails/send-followup', { scheduled_email_id: scheduledId })
      setMsg({ type: 'success', text: 'Sent!' })
      setTimeout(() => { onDone(); setMsg(null) }, 1200)
    } catch (e) { setMsg({ type: 'error', text: e.message }) }
    finally { setLoading(false) }
  }
  if (msg) return <span style={{ fontSize: 12, color: msg.type === 'success' ? '#059669' : '#dc2626' }}>{msg.text}</span>
  return <button className="btn btn-sm btn-primary" onClick={handleSend} disabled={loading}>{loading ? '…' : 'Send Now'}</button>
}
