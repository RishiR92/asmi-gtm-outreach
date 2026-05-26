import { useState, useEffect, useRef } from 'react'
import api from '../api.js'
import LeadModal from './LeadModal.jsx'

const STATUS_BADGE = {
  'New': 'badge-new',
  'Email Found': 'badge-email-found',
  'Contacted': 'badge-contacted',
  'Replied': 'badge-replied',
  'Feature Confirmed': 'badge-feature-confirmed',
  'Not Interested': 'badge-not-interested',
  'No Response': 'badge-no-response',
}

const STATUSES = ['', 'New', 'Email Found', 'Contacted', 'Replied', 'Feature Confirmed', 'Not Interested', 'No Response']
const CATEGORIES = ['', 'AI Tools', 'Productivity', 'Indian-Origin', 'Startup-Founder', 'Business Owner', 'Niche']

function formatNum(n) {
  if (!n) return '—'
  if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M'
  if (n >= 1000) return (n / 1000).toFixed(0) + 'K'
  return n
}

export default function Leads() {
  const [leads, setLeads] = useState([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [categoryFilter, setCategoryFilter] = useState('')
  const [modal, setModal] = useState(null) // null | 'create' | lead object
  const [actionMsg, setActionMsg] = useState(null)
  const [bulkModal, setBulkModal] = useState(false)
  const [bulkEmails, setBulkEmails] = useState('')
  const [bulkLoading, setBulkLoading] = useState(false)
  const [bulkResult, setBulkResult] = useState(null)
  const fileInputRef = useRef()
  const PER_PAGE = 25

  async function fetchLeads() {
    setLoading(true)
    setError(null)
    try {
      const params = { page, per_page: PER_PAGE }
      if (search) params.search = search
      if (statusFilter) params.status = statusFilter
      if (categoryFilter) params.category = categoryFilter
      const res = await api.get('/leads', { params })
      setLeads(res.data.data || [])
      setTotal(res.data.total || 0)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchLeads() }, [page, statusFilter, categoryFilter])

  // Debounce search
  useEffect(() => {
    const t = setTimeout(() => { setPage(1); fetchLeads() }, 350)
    return () => clearTimeout(t)
  }, [search])

  async function quickStatus(leadId, status) {
    try {
      await api.patch(`/leads/${leadId}/status`, { status })
      setActionMsg({ type: 'success', text: `Marked as ${status}` })
      setTimeout(() => setActionMsg(null), 2000)
      fetchLeads()
    } catch (e) {
      setActionMsg({ type: 'error', text: e.message })
    }
  }

  async function deleteLead(lead) {
    if (!window.confirm(`Delete "${lead.name}"? This cannot be undone.`)) return
    try {
      await api.delete(`/leads/${lead.id}`)
      fetchLeads()
    } catch (e) {
      setActionMsg({ type: 'error', text: e.message })
    }
  }

  async function handleImport(e) {
    const file = e.target.files[0]
    if (!file) return
    const fd = new FormData()
    fd.append('file', file)
    try {
      const res = await api.post('/leads/import', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
      setActionMsg({ type: 'success', text: res.data.message })
      fetchLeads()
    } catch (e) {
      setActionMsg({ type: 'error', text: e.message })
    } finally {
      e.target.value = ''
    }
  }

  async function handleExport() {
    try {
      const res = await api.get('/leads/export', { responseType: 'blob' })
      const url = URL.createObjectURL(res.data)
      const a = document.createElement('a')
      a.href = url
      a.download = 'leads_export.csv'
      a.click()
      URL.revokeObjectURL(url)
    } catch (e) {
      setActionMsg({ type: 'error', text: e.message })
    }
  }

  async function handleBulkContacted() {
    const emails = bulkEmails
      .split(/[\n,;]+/)
      .map(e => e.trim())
      .filter(Boolean)
    if (!emails.length) return
    setBulkLoading(true)
    setBulkResult(null)
    try {
      const res = await api.post('/leads/bulk-status', { emails, status: 'Contacted' })
      setBulkResult(res.data)
      fetchLeads()
    } catch (e) {
      setBulkResult({ message: e.message })
    } finally {
      setBulkLoading(false)
    }
  }

  const totalPages = Math.ceil(total / PER_PAGE)

  return (
    <div>
      <div className="page-header">
        <div>
          <h2>Leads</h2>
          <p>{total} total leads</p>
        </div>
        <div className="btn-row">
          <button className="btn btn-secondary btn-sm" onClick={() => fileInputRef.current.click()}>
            📥 Import CSV
          </button>
          <input ref={fileInputRef} type="file" accept=".csv" style={{ display: 'none' }} onChange={handleImport} />
          <button className="btn btn-secondary btn-sm" onClick={handleExport}>
            📤 Export CSV
          </button>
          <button className="btn btn-secondary btn-sm" onClick={() => { setBulkModal(true); setBulkResult(null); setBulkEmails('') }}>
            ✅ Mark Contacted
          </button>
          <button className="btn btn-primary" onClick={() => setModal('create')}>
            + Add Lead
          </button>
        </div>
      </div>

      {actionMsg && (
        <div className={`alert alert-${actionMsg.type === 'success' ? 'success' : 'error'}`}>
          {actionMsg.text}
        </div>
      )}

      {/* Filters */}
      <div className="search-bar">
        <div className="search-input-wrapper" style={{ flex: 2 }}>
          <span className="search-icon">🔍</span>
          <input
            className="form-control"
            placeholder="Search leads, newsletters, emails..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>
        <select className="form-control" style={{ width: 180 }} value={statusFilter} onChange={e => { setStatusFilter(e.target.value); setPage(1) }}>
          <option value="">All Statuses</option>
          {STATUSES.filter(Boolean).map(s => <option key={s} value={s}>{s}</option>)}
        </select>
        <select className="form-control" style={{ width: 180 }} value={categoryFilter} onChange={e => { setCategoryFilter(e.target.value); setPage(1) }}>
          <option value="">All Categories</option>
          {CATEGORIES.filter(Boolean).map(c => <option key={c} value={c}>{c}</option>)}
        </select>
      </div>

      {/* Table */}
      {loading ? (
        <div className="loading-spinner"><div className="spinner" /> Loading leads...</div>
      ) : error ? (
        <div className="alert alert-error">{error}</div>
      ) : leads.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">👥</div>
          <h3>No leads found</h3>
          <p>Add your first lead or import a CSV file</p>
        </div>
      ) : (
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Newsletter</th>
                <th>Audience</th>
                <th>Category</th>
                <th>Status</th>
                <th>Email</th>
                <th>Follow-up Due</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {leads.map(lead => (
                <tr key={lead.id} onClick={() => setModal(lead)} style={{ cursor: 'pointer' }}>
                  <td>
                    <strong>{lead.name}</strong>
                    {lead.twitter_handle && <div className="td-muted">{lead.twitter_handle}</div>}
                  </td>
                  <td>
                    {lead.newsletter_name && <span className="truncate">{lead.newsletter_name}</span>}
                    {lead.url && <div className="td-muted">{lead.url}</div>}
                  </td>
                  <td className="td-muted">{formatNum(lead.estimated_audience)}</td>
                  <td className="td-muted">{lead.category}</td>
                  <td>
                    <span className={`badge ${STATUS_BADGE[lead.status] || 'badge-new'}`}>
                      {lead.status}
                    </span>
                  </td>
                  <td className="td-muted">
                    {lead.email
                      ? <span className="truncate">{lead.email}</span>
                      : <span style={{ color: '#f59e0b' }}>{lead.contact_method}</span>
                    }
                  </td>
                  <td className="td-muted">
                    {lead.follow_up_due
                      ? new Date(lead.follow_up_due).toLocaleDateString()
                      : '—'}
                  </td>
                  <td onClick={e => e.stopPropagation()}>
                    <div className="td-actions">
                      <button className="btn btn-xs btn-ghost" onClick={() => setModal(lead)}>Edit</button>
                      {lead.status !== 'Replied' && (
                        <button className="btn btn-xs btn-success" onClick={() => quickStatus(lead.id, 'Replied')}>Replied</button>
                      )}
                      {lead.status !== 'Not Interested' && (
                        <button className="btn btn-xs btn-danger" onClick={() => quickStatus(lead.id, 'Not Interested')}>✗</button>
                      )}
                      <button
                        className="btn btn-xs btn-danger"
                        style={{ opacity: 0.7 }}
                        onClick={() => deleteLead(lead)}
                        title="Delete lead permanently"
                      >🗑</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="pagination">
          <span className="pagination-info">
            {(page - 1) * PER_PAGE + 1}–{Math.min(page * PER_PAGE, total)} of {total}
          </span>
          <button className="btn btn-sm btn-ghost" disabled={page === 1} onClick={() => setPage(p => p - 1)}>← Prev</button>
          <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>Page {page} of {totalPages}</span>
          <button className="btn btn-sm btn-ghost" disabled={page === totalPages} onClick={() => setPage(p => p + 1)}>Next →</button>
        </div>
      )}

      {/* Lead Modal */}
      {modal && (
        <LeadModal
          lead={modal === 'create' ? null : modal}
          onClose={() => setModal(null)}
          onSave={fetchLeads}
        />
      )}

      {/* Bulk Mark Contacted Modal */}
      {bulkModal && (
        <div className="modal-overlay" onClick={() => setBulkModal(false)}>
          <div className="modal" style={{ maxWidth: 520 }} onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>✅ Mark Emails as Contacted</h3>
              <button className="modal-close" onClick={() => setBulkModal(false)}>×</button>
            </div>
            <div className="modal-body">
              <p style={{ marginBottom: 8, color: 'var(--text-muted)', fontSize: 13 }}>
                Paste email addresses (one per line, or comma-separated). All matching leads will be marked as <strong>Contacted</strong>.
              </p>
              <p style={{ marginBottom: 12, color: 'var(--text-muted)', fontSize: 12 }}>
                💡 Get the list from Railway → Logs → search <code>[autopilot] ✓ Sent</code>
              </p>
              <textarea
                className="form-control"
                rows={10}
                placeholder={"newsletter@example.com\nanother@domain.com\n..."}
                value={bulkEmails}
                onChange={e => setBulkEmails(e.target.value)}
                style={{ fontFamily: 'monospace', fontSize: 12 }}
              />
              {bulkResult && (
                <div className={`alert alert-${bulkResult.data?.updated > 0 ? 'success' : 'error'}`} style={{ marginTop: 10 }}>
                  {bulkResult.message}
                  {bulkResult.data?.not_found?.length > 0 && (
                    <details style={{ marginTop: 6, fontSize: 11 }}>
                      <summary>Unmatched ({bulkResult.data.not_found.length})</summary>
                      <pre style={{ marginTop: 4 }}>{bulkResult.data.not_found.join('\n')}</pre>
                    </details>
                  )}
                </div>
              )}
            </div>
            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={() => setBulkModal(false)}>Cancel</button>
              <button
                className="btn btn-primary"
                onClick={handleBulkContacted}
                disabled={bulkLoading || !bulkEmails.trim()}
              >
                {bulkLoading ? 'Updating…' : 'Mark as Contacted'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
