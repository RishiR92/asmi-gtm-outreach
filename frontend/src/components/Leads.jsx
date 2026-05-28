import { useState, useEffect } from 'react'
import api from '../api.js'
import LeadModal from './LeadModal.jsx'

function fmt(n) {
  if (!n) return '—'
  if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M'
  if (n >= 1000) return Math.round(n / 1000) + 'K'
  return n
}

function timeAgo(iso) {
  if (!iso) return '—'
  const d = Math.floor((Date.now() - new Date(iso + 'Z')) / 86400000)
  return d === 0 ? 'Today' : d === 1 ? 'Yesterday' : `${d}d ago`
}

const GENERIC = ['contact@','hello@','info@','admin@','team@','support@','editor@','newsletter@','hi@','mail@','press@','media@']

function isGeneric(email) {
  return email && GENERIC.some(p => email.toLowerCase().startsWith(p))
}

function Pagination({ page, total, per, onChange }) {
  const pages = Math.ceil(total / per)
  if (pages <= 1) return null
  return (
    <div style={{ display: 'flex', gap: 8, padding: '12px 0', justifyContent: 'center', alignItems: 'center' }}>
      <button onClick={() => onChange(page - 1)} disabled={page === 1} className="btn btn-ghost" style={{ padding: '4px 12px', fontSize: 13 }}>← Prev</button>
      <span style={{ fontSize: 13, color: '#64748b' }}>Page {page} of {pages} ({total} total)</span>
      <button onClick={() => onChange(page + 1)} disabled={page === pages} className="btn btn-ghost" style={{ padding: '4px 12px', fontSize: 13 }}>Next →</button>
    </div>
  )
}

// ── Contacted Tab ─────────────────────────────────────────────────────────────
function ContactedTab() {
  const [leads, setLeads] = useState([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const PER = 25

  async function load() {
    setLoading(true)
    try {
      const p = { page, per_page: PER, status: 'Contacted,Replied,Feature Confirmed' }
      if (search) p.search = search
      const r = await api.get('/leads', { params: p })
      setLeads(r.data.data || [])
      setTotal(r.data.total || 0)
    } finally { setLoading(false) }
  }

  useEffect(() => { load() }, [page])
  useEffect(() => { const t = setTimeout(() => { setPage(1); load() }, 350); return () => clearTimeout(t) }, [search])

  return (
    <div>
      <div style={{ display: 'flex', gap: 12, marginBottom: 16, alignItems: 'center' }}>
        <input className="form-input" placeholder="Search…" value={search}
          onChange={e => setSearch(e.target.value)} style={{ maxWidth: 260 }} />
        <span style={{ color: '#64748b', fontSize: 13 }}>{total} leads contacted</span>
      </div>
      {loading ? <div className="loading-spinner"><div className="spinner" /></div> : (
        <div className="table-wrapper">
          <table>
            <thead><tr><th>Name</th><th>Newsletter</th><th>Email</th><th>Status</th><th>Contacted</th><th>Audience</th></tr></thead>
            <tbody>
              {leads.map(l => (
                <tr key={l.id}>
                  <td><strong>{l.name}</strong></td>
                  <td style={{ color: '#64748b', fontSize: 13 }}>{l.newsletter_name || '—'}</td>
                  <td style={{ fontSize: 12 }}>{l.email || '—'}</td>
                  <td>
                    <span style={{
                      fontSize: 11, fontWeight: 600, padding: '2px 8px', borderRadius: 4,
                      background: l.status === 'Replied' ? '#dcfce7' : l.status === 'Feature Confirmed' ? '#bbf7d0' : '#fef9c3',
                      color: l.status === 'Replied' ? '#15803d' : l.status === 'Feature Confirmed' ? '#14532d' : '#854d0e',
                    }}>{l.status}</span>
                  </td>
                  <td style={{ fontSize: 12, color: '#64748b' }}>{timeAgo(l.date_contacted)}</td>
                  <td style={{ fontSize: 12, color: '#64748b' }}>{fmt(l.estimated_audience)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <Pagination page={page} total={total} per={PER} onChange={setPage} />
        </div>
      )}
    </div>
  )
}

// ── Bounced Tab ───────────────────────────────────────────────────────────────
function BouncedTab() {
  const [leads, setLeads] = useState([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const PER = 25

  async function load() {
    setLoading(true)
    try {
      const r = await api.get('/leads', { params: { page, per_page: PER, status: 'Bounced' } })
      setLeads(r.data.data || [])
      setTotal(r.data.total || 0)
    } finally { setLoading(false) }
  }

  useEffect(() => { load() }, [page])

  return (
    <div>
      <div style={{ background: '#fef2f2', border: '1px solid #fecaca', borderRadius: 8, padding: '10px 16px', fontSize: 13, color: '#991b1b', marginBottom: 16 }}>
        ⚠️ Hard bounces (550 errors) are detected automatically at send time. These addresses no longer exist — update them with a correct email.
      </div>
      <div style={{ color: '#64748b', fontSize: 13, marginBottom: 12 }}>{total} bounced</div>
      {loading ? <div className="loading-spinner"><div className="spinner" /></div> : total === 0 ? (
        <div className="empty-state" style={{ padding: 40 }}>
          <div className="empty-icon">✅</div><p>No bounces detected yet</p>
        </div>
      ) : (
        <div className="table-wrapper">
          <table>
            <thead><tr><th>Name</th><th>Email</th><th>Newsletter</th><th>Bounced</th></tr></thead>
            <tbody>
              {leads.map(l => (
                <tr key={l.id}>
                  <td><strong>{l.name}</strong></td>
                  <td style={{ fontSize: 12, color: '#dc2626' }}>{l.email}</td>
                  <td style={{ fontSize: 13, color: '#64748b' }}>{l.newsletter_name || '—'}</td>
                  <td style={{ fontSize: 12, color: '#64748b' }}>{timeAgo(l.bounced_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <Pagination page={page} total={total} per={PER} onChange={setPage} />
        </div>
      )}
    </div>
  )
}

// ── To Be Contacted Tab ───────────────────────────────────────────────────────
function LeadRow({ lead, onSaved }) {
  const [editing, setEditing] = useState(false)
  const [emailVal, setEmailVal] = useState(lead.email || '')
  const gen = isGeneric(lead.email)

  async function saveEmail() {
    try {
      await api.put(`/leads/${lead.id}`, { email: emailVal, status: emailVal ? 'Email Found' : 'New' })
      setEditing(false)
      onSaved()
    } catch (e) { alert(e.message) }
  }

  async function skip() {
    if (!window.confirm(`Skip ${lead.name}?`)) return
    try { await api.put(`/leads/${lead.id}`, { status: 'Not Interested' }); onSaved() }
    catch (e) { alert(e.message) }
  }

  return (
    <tr>
      <td><strong>{lead.name}</strong></td>
      <td style={{ fontSize: 13, color: '#64748b' }}>{lead.newsletter_name || '—'}</td>
      <td>
        {editing ? (
          <div style={{ display: 'flex', gap: 6 }}>
            <input value={emailVal} onChange={e => setEmailVal(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && saveEmail()}
              style={{ fontSize: 12, padding: '3px 8px', border: '1px solid #93c5fd', borderRadius: 4, width: 200 }} />
            <button onClick={saveEmail} style={{ fontSize: 11, padding: '2px 8px', background: '#2563eb', color: '#fff', border: 'none', borderRadius: 4, cursor: 'pointer' }}>✓</button>
            <button onClick={() => setEditing(false)} style={{ fontSize: 11, padding: '2px 6px', background: '#f1f5f9', border: 'none', borderRadius: 4, cursor: 'pointer' }}>✕</button>
          </div>
        ) : (
          <span style={{ cursor: 'pointer', color: gen ? '#d97706' : lead.email ? '#334155' : '#dc2626', fontSize: 12 }}
            onClick={() => setEditing(true)} title="Click to edit">
            {lead.email || '+ Add email'}
            {gen && <span style={{ fontSize: 10, marginLeft: 4, opacity: .7 }}>generic</span>}
          </span>
        )}
      </td>
      <td><span style={{ fontSize: 11, background: '#eff6ff', color: '#2563eb', padding: '2px 6px', borderRadius: 4 }}>{lead.category || '—'}</span></td>
      <td style={{ fontSize: 12, color: '#64748b' }}>{fmt(lead.estimated_audience)}</td>
      <td>
        <div style={{ display: 'flex', gap: 6 }}>
          <button onClick={() => setEditing(true)} style={{ fontSize: 11, padding: '3px 10px', background: '#eff6ff', color: '#2563eb', border: '1px solid #bfdbfe', borderRadius: 4, cursor: 'pointer' }}>✏️ Email</button>
          <button onClick={skip} style={{ fontSize: 11, padding: '3px 10px', background: '#fef2f2', color: '#dc2626', border: '1px solid #fecaca', borderRadius: 4, cursor: 'pointer' }}>Skip</button>
        </div>
      </td>
    </tr>
  )
}

function ToBeContactedTab() {
  const [leads, setLeads] = useState([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [emailFilter, setEmailFilter] = useState('personal')
  const [loading, setLoading] = useState(true)
  const PER = 25

  async function load() {
    setLoading(true)
    try {
      const p = { page, per_page: PER, status: 'New,Email Found' }
      if (search) p.search = search
      if (emailFilter !== 'all') p.email_quality = emailFilter
      const r = await api.get('/leads', { params: p })
      setLeads(r.data.data || [])
      setTotal(r.data.total || 0)
    } finally { setLoading(false) }
  }

  useEffect(() => { load() }, [page, emailFilter])
  useEffect(() => { const t = setTimeout(() => { setPage(1); load() }, 350); return () => clearTimeout(t) }, [search])

  const filters = [
    { key: 'personal', label: '👤 Personal', sub: 'Ready to send' },
    { key: 'generic',  label: '📧 Generic',  sub: 'Need updating' },
    { key: 'none',     label: '❌ No email',  sub: 'Need finding' },
    { key: 'all',      label: '📋 All',       sub: '' },
  ]

  return (
    <div>
      <div style={{ display: 'flex', gap: 8, marginBottom: 16, flexWrap: 'wrap', alignItems: 'center' }}>
        {filters.map(f => (
          <button key={f.key} onClick={() => { setEmailFilter(f.key); setPage(1) }} style={{
            padding: '7px 16px', borderRadius: 20, fontSize: 12, fontWeight: 600, border: 'none', cursor: 'pointer',
            background: emailFilter === f.key ? '#2563eb' : '#f1f5f9',
            color: emailFilter === f.key ? '#fff' : '#475569',
          }}>
            {f.label} {f.sub && <span style={{ opacity: .7, fontWeight: 400, fontSize: 11 }}>{f.sub}</span>}
          </button>
        ))}
        <input className="form-input" placeholder="Search…" value={search}
          onChange={e => setSearch(e.target.value)} style={{ marginLeft: 'auto', maxWidth: 220, fontSize: 13 }} />
        <span style={{ color: '#64748b', fontSize: 13 }}>{total} leads</span>
      </div>

      {loading ? <div className="loading-spinner"><div className="spinner" /></div> : total === 0 ? (
        <div className="empty-state" style={{ padding: 40 }}>
          <div className="empty-icon">{emailFilter === 'personal' ? '🎉' : '✅'}</div>
          <p>{emailFilter === 'personal' ? 'No personal contacts queued — add emails above' : 'None here'}</p>
        </div>
      ) : (
        <div className="table-wrapper">
          <table>
            <thead><tr><th>Name</th><th>Newsletter</th><th>Email</th><th>Category</th><th>Audience</th><th>Actions</th></tr></thead>
            <tbody>{leads.map(l => <LeadRow key={l.id} lead={l} onSaved={() => { setPage(1); load() }} />)}</tbody>
          </table>
          <Pagination page={page} total={total} per={PER} onChange={setPage} />
        </div>
      )}
    </div>
  )
}

// ── Main ──────────────────────────────────────────────────────────────────────
const TABS = [
  { key: 'to-contact', label: '📋 To Be Contacted' },
  { key: 'contacted',  label: '✅ Contacted' },
  { key: 'bounced',    label: '⚠️ Bounced' },
]

export default function Leads() {
  const [tab, setTab] = useState('to-contact')
  return (
    <div>
      <div className="page-header">
        <div><h2>Leads</h2><p>Manage your outreach pipeline</p></div>
      </div>
      <div style={{ display: 'flex', gap: 4, marginBottom: 24, borderBottom: '2px solid #e2e8f0' }}>
        {TABS.map(t => (
          <button key={t.key} onClick={() => setTab(t.key)} style={{
            padding: '10px 20px', border: 'none', background: 'none', cursor: 'pointer',
            fontSize: 14, fontWeight: 600, marginBottom: -2,
            color: tab === t.key ? '#2563eb' : '#64748b',
            borderBottom: tab === t.key ? '2px solid #2563eb' : '2px solid transparent',
          }}>{t.label}</button>
        ))}
      </div>
      {tab === 'to-contact' && <ToBeContactedTab />}
      {tab === 'contacted'  && <ContactedTab />}
      {tab === 'bounced'    && <BouncedTab />}
    </div>
  )
}
