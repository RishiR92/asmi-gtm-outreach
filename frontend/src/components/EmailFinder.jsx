import { useState, useEffect } from 'react'
import api from '../api.js'

export default function EmailFinder() {
  const [form, setForm] = useState({ first_name: '', last_name: '', domain: '' })
  const [patterns, setPatterns] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [copied, setCopied] = useState(null)
  const [leads, setLeads] = useState([])
  const [selectedLead, setSelectedLead] = useState('')
  const [selectedEmail, setSelectedEmail] = useState('')
  const [saveMsg, setSaveMsg] = useState(null)
  const [hunterDomain, setHunterDomain] = useState('')

  useEffect(() => {
    api.get('/leads', { params: { per_page: 100 } })
      .then(res => setLeads(res.data.data || []))
      .catch(() => {})
  }, [])

  async function handleGenerate(e) {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setPatterns([])
    try {
      const res = await api.post('/emails/guess-pattern', {
        first_name: form.first_name,
        last_name: form.last_name,
        domain: form.domain.replace(/^https?:\/\//, '').replace(/\/.*$/, ''),
      })
      setPatterns(res.data.data || [])
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  function copyEmail(email) {
    navigator.clipboard.writeText(email).then(() => {
      setCopied(email)
      setTimeout(() => setCopied(null), 1500)
    })
  }

  async function saveToLead() {
    if (!selectedLead || !selectedEmail) {
      setSaveMsg({ type: 'error', text: 'Select a lead and an email pattern' })
      return
    }
    try {
      await api.put(`/leads/${selectedLead}`, { email: selectedEmail, status: 'Email Found' })
      setSaveMsg({ type: 'success', text: `Saved ${selectedEmail} to lead` })
      setTimeout(() => setSaveMsg(null), 2500)
    } catch (e) {
      setSaveMsg({ type: 'error', text: e.message })
    }
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <h2>Email Finder</h2>
          <p>Generate email patterns and find newsletter contact emails</p>
        </div>
      </div>

      <div className="finder-panels">
        {/* Panel 1: Email Pattern Guesser */}
        <div className="card">
          <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 16 }}>
            Email Pattern Guesser
          </h3>

          <form onSubmit={handleGenerate}>
            <div className="form-row">
              <div className="form-group">
                <label>First Name</label>
                <input
                  className="form-control"
                  value={form.first_name}
                  onChange={e => setForm(f => ({ ...f, first_name: e.target.value }))}
                  placeholder="Matt"
                  required
                />
              </div>
              <div className="form-group">
                <label>Last Name</label>
                <input
                  className="form-control"
                  value={form.last_name}
                  onChange={e => setForm(f => ({ ...f, last_name: e.target.value }))}
                  placeholder="Wolfe"
                />
              </div>
            </div>
            <div className="form-group">
              <label>Domain</label>
              <input
                className="form-control"
                value={form.domain}
                onChange={e => setForm(f => ({ ...f, domain: e.target.value }))}
                placeholder="futuretools.io"
                required
              />
            </div>
            {error && <div className="alert alert-error mb-12">{error}</div>}
            <button className="btn btn-primary" type="submit" disabled={loading}>
              {loading ? 'Generating...' : '✨ Generate Patterns'}
            </button>
          </form>

          {patterns.length > 0 && (
            <>
              <div className="pattern-list">
                {patterns.map(p => (
                  <div className="pattern-item" key={p}>
                    <span
                      style={{ cursor: 'pointer' }}
                      onClick={() => setSelectedEmail(p)}
                    >
                      {selectedEmail === p && <span style={{ color: 'var(--accent)', marginRight: 6 }}>✓</span>}
                      {p}
                    </span>
                    <div className="btn-row">
                      <button className="btn btn-xs btn-ghost" onClick={() => copyEmail(p)}>
                        {copied === p ? <span className="copy-feedback">Copied!</span> : 'Copy'}
                      </button>
                      <button
                        className={`btn btn-xs ${selectedEmail === p ? 'btn-primary' : 'btn-secondary'}`}
                        onClick={() => setSelectedEmail(p)}
                      >
                        {selectedEmail === p ? '✓ Selected' : 'Select'}
                      </button>
                    </div>
                  </div>
                ))}
              </div>

              <div className="section-divider" />

              <div style={{ fontWeight: 700, fontSize: 13, marginBottom: 12 }}>
                Save to Lead
              </div>
              {saveMsg && (
                <div className={`alert alert-${saveMsg.type === 'success' ? 'success' : 'error'} mb-12`}>
                  {saveMsg.text}
                </div>
              )}
              <div className="form-group">
                <label>Selected email</label>
                <input
                  className="form-control"
                  value={selectedEmail}
                  onChange={e => setSelectedEmail(e.target.value)}
                  placeholder="Select from list above or type..."
                />
              </div>
              <div className="form-group">
                <label>Lead</label>
                <select
                  className="form-control"
                  value={selectedLead}
                  onChange={e => setSelectedLead(e.target.value)}
                >
                  <option value="">Select lead...</option>
                  {leads.map(l => (
                    <option key={l.id} value={l.id}>
                      {l.name} {l.newsletter_name ? `— ${l.newsletter_name}` : ''}
                    </option>
                  ))}
                </select>
              </div>
              <button
                className="btn btn-success"
                onClick={saveToLead}
                disabled={!selectedLead || !selectedEmail}
              >
                💾 Save Email to Lead
              </button>
            </>
          )}
        </div>

        {/* Panel 2: Hunter.io */}
        <div>
          <div className="card mb-16">
            <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 16 }}>
              Hunter.io Quick Lookup
            </h3>
            <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 16 }}>
              Free tier allows 25 domain searches/month. Hunter finds verified email addresses associated with a domain.
            </p>
            <div className="form-group">
              <label>Domain</label>
              <input
                className="form-control"
                value={hunterDomain}
                onChange={e => setHunterDomain(e.target.value)}
                placeholder="futuretools.io"
              />
            </div>
            <button
              className="btn btn-primary"
              disabled={!hunterDomain}
              onClick={() => {
                const domain = hunterDomain.replace(/^https?:\/\//, '').replace(/\/.*$/, '')
                window.open(`https://hunter.io/find?domain=${domain}`, '_blank')
              }}
            >
              🔍 Open in Hunter.io
            </button>
          </div>

          <div className="card">
            <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 16 }}>
              Tips for Finding Emails
            </h3>
            <div style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.8 }}>
              <p style={{ marginBottom: 10 }}>
                <strong>1. Pattern Guesser</strong> — Try common patterns above. The most common is{' '}
                <code style={{ background: '#f1f5f9', padding: '1px 5px', borderRadius: 3 }}>first@domain.com</code>
              </p>
              <p style={{ marginBottom: 10 }}>
                <strong>2. Hunter.io</strong> — Best for verified emails. Free tier gives 25 searches/month.
              </p>
              <p style={{ marginBottom: 10 }}>
                <strong>3. Check the site</strong> — Look for About, Contact, or Team pages.
              </p>
              <p style={{ marginBottom: 10 }}>
                <strong>4. LinkedIn</strong> — Contact info sometimes visible on profiles.
              </p>
              <p>
                <strong>5. Submission forms</strong> — Use the newsletter's own submission/sponsorship form.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
