import { useState, useEffect } from 'react'
import api from '../api.js'

const CATEGORIES = ['AI Tools', 'Productivity', 'Indian-Origin', 'Startup-Founder', 'Business Owner', 'Niche']
const CONTACT_METHODS = ['Email', 'X DM', 'LinkedIn', 'Submission Form']
const STATUSES = ['New', 'Email Found', 'Contacted', 'Replied', 'Feature Confirmed', 'Not Interested', 'No Response']

const EMPTY_LEAD = {
  name: '', newsletter_name: '', url: '', estimated_audience: '',
  category: 'AI Tools', contact_method: 'Email', email: '',
  linkedin_url: '', twitter_handle: '', notes: '', status: 'New',
  template_id: '', ab_variant: 'A',
}

export default function LeadModal({ lead, onClose, onSave }) {
  const [form, setForm] = useState(EMPTY_LEAD)
  const [templates, setTemplates] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  const [showSendSection, setShowSendSection] = useState(false)
  const [sendForm, setSendForm] = useState({ template_id: '', ab_variant: 'A', custom_line: '' })
  const [sending, setSending] = useState(false)
  const [sendMsg, setSendMsg] = useState(null)
  const [preview, setPreview] = useState({ subject: '', body: '' })

  const isEdit = !!lead?.id

  useEffect(() => {
    if (lead) {
      setForm({
        name: lead.name || '',
        newsletter_name: lead.newsletter_name || '',
        url: lead.url || '',
        estimated_audience: lead.estimated_audience || '',
        category: lead.category || 'AI Tools',
        contact_method: lead.contact_method || 'Email',
        email: lead.email || '',
        linkedin_url: lead.linkedin_url || '',
        twitter_handle: lead.twitter_handle || '',
        notes: lead.notes || '',
        status: lead.status || 'New',
        template_id: lead.template_id || '',
        ab_variant: lead.ab_variant || 'A',
      })
    }
  }, [lead])

  useEffect(() => {
    api.get('/templates').then(res => setTemplates(res.data.data || [])).catch(() => {})
  }, [])

  // Update preview when send form changes
  useEffect(() => {
    if (!sendForm.template_id || !templates.length) return
    const tmpl = templates.find(t => t.id === Number(sendForm.template_id))
    if (!tmpl) return
    const subject = sendForm.ab_variant === 'A' ? tmpl.subject_a : tmpl.subject_b
    const body = tmpl.body || ''
    const name = form.name || '{{name}}'
    const newsletter = form.newsletter_name || '{{newsletter}}'
    const audience = form.estimated_audience || '{{audience}}'
    const custom = sendForm.custom_line || ''
    const render = (str) => (str || '')
      .replace(/\{\{name\}\}/g, name)
      .replace(/\{\{newsletter\}\}/g, newsletter)
      .replace(/\{\{audience\}\}/g, String(audience))
      .replace(/\{\{custom_line\}\}/g, custom)
    setPreview({ subject: render(subject), body: render(body) })
  }, [sendForm, templates, form])

  function set(field) {
    return e => setForm(f => ({ ...f, [field]: e.target.value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setSuccess(null)
    try {
      const payload = {
        ...form,
        estimated_audience: form.estimated_audience ? Number(form.estimated_audience) : null,
        template_id: form.template_id ? Number(form.template_id) : null,
      }
      if (isEdit) {
        await api.put(`/leads/${lead.id}`, payload)
      } else {
        await api.post('/leads', payload)
      }
      setSuccess(isEdit ? 'Lead updated!' : 'Lead created!')
      setTimeout(() => { onSave(); onClose() }, 800)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  async function handleSend() {
    if (!sendForm.template_id) { setSendMsg({ type: 'error', text: 'Select a template' }); return }
    if (!lead?.id) { setSendMsg({ type: 'error', text: 'Save lead first' }); return }
    setSending(true)
    setSendMsg(null)
    try {
      const res = await api.post('/emails/send', {
        lead_id: lead.id,
        template_id: Number(sendForm.template_id),
        ab_variant: sendForm.ab_variant,
        custom_line: sendForm.custom_line,
      })
      setSendMsg({ type: 'success', text: res.data.message })
      setTimeout(() => { onSave(); }, 1500)
    } catch (e) {
      setSendMsg({ type: 'error', text: e.message })
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={e => { if (e.target === e.currentTarget) onClose() }}>
      <div className="modal modal-lg">
        <div className="modal-header">
          <h3>{isEdit ? `Edit: ${lead.name}` : 'Add New Lead'}</h3>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        <div className="modal-body">
          {error && <div className="alert alert-error mb-16">{error}</div>}
          {success && <div className="alert alert-success mb-16">{success}</div>}

          <form onSubmit={handleSubmit} id="lead-form">
            <div className="form-row">
              <div className="form-group">
                <label>Name *</label>
                <input className="form-control" value={form.name} onChange={set('name')} required />
              </div>
              <div className="form-group">
                <label>Newsletter Name</label>
                <input className="form-control" value={form.newsletter_name} onChange={set('newsletter_name')} />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Website URL</label>
                <input className="form-control" value={form.url} onChange={set('url')} placeholder="example.com" />
              </div>
              <div className="form-group">
                <label>Est. Audience Size</label>
                <input className="form-control" type="number" value={form.estimated_audience} onChange={set('estimated_audience')} placeholder="50000" />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Category</label>
                <select className="form-control" value={form.category} onChange={set('category')}>
                  {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>
              <div className="form-group">
                <label>Contact Method</label>
                <select className="form-control" value={form.contact_method} onChange={set('contact_method')}>
                  {CONTACT_METHODS.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Email</label>
                <input className="form-control" type="email" value={form.email} onChange={set('email')} placeholder="contact@newsletter.com" />
              </div>
              <div className="form-group">
                <label>Status</label>
                <select className="form-control" value={form.status} onChange={set('status')}>
                  {STATUSES.map(s => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>LinkedIn URL</label>
                <input className="form-control" value={form.linkedin_url} onChange={set('linkedin_url')} placeholder="linkedin.com/in/username" />
              </div>
              <div className="form-group">
                <label>Twitter Handle</label>
                <input className="form-control" value={form.twitter_handle} onChange={set('twitter_handle')} placeholder="@handle" />
              </div>
            </div>

            <div className="form-group">
              <label>Notes</label>
              <textarea className="form-control" value={form.notes} onChange={set('notes')} rows={3} placeholder="Any notes about this lead..." />
            </div>
          </form>

          {/* Send Email Section (only for existing leads) */}
          {isEdit && (
            <>
              <div className="section-divider" />
              <div className="flex-between mb-12">
                <div className="section-title" style={{ margin: 0 }}>Send Email</div>
                <button
                  className="btn btn-sm btn-ghost"
                  onClick={() => setShowSendSection(s => !s)}
                >
                  {showSendSection ? 'Hide' : 'Compose & Send'}
                </button>
              </div>

              {showSendSection && (
                <div>
                  {sendMsg && (
                    <div className={`alert alert-${sendMsg.type === 'success' ? 'success' : 'error'} mb-16`}>
                      {sendMsg.text}
                    </div>
                  )}

                  <div className="form-row">
                    <div className="form-group">
                      <label>Template</label>
                      <select
                        className="form-control"
                        value={sendForm.template_id}
                        onChange={e => setSendForm(f => ({ ...f, template_id: e.target.value }))}
                      >
                        <option value="">Select template...</option>
                        {templates.map(t => (
                          <option key={t.id} value={t.id}>{t.name} ({t.category})</option>
                        ))}
                      </select>
                    </div>
                    <div className="form-group">
                      <label>A/B Variant</label>
                      <select
                        className="form-control"
                        value={sendForm.ab_variant}
                        onChange={e => setSendForm(f => ({ ...f, ab_variant: e.target.value }))}
                      >
                        <option value="A">A — {templates.find(t => t.id === Number(sendForm.template_id))?.subject_a?.slice(0, 40) || 'Subject A'}</option>
                        <option value="B">B — {templates.find(t => t.id === Number(sendForm.template_id))?.subject_b?.slice(0, 40) || 'Subject B'}</option>
                      </select>
                    </div>
                  </div>

                  <div className="form-group">
                    <label>Custom Line (replaces {'{{custom_line}}'})</label>
                    <input
                      className="form-control"
                      value={sendForm.custom_line}
                      onChange={e => setSendForm(f => ({ ...f, custom_line: e.target.value }))}
                      placeholder="I noticed your recent post on AI tools..."
                    />
                  </div>

                  {preview.subject && (
                    <div className="form-group">
                      <label>Preview</label>
                      <div style={{ fontWeight: 700, marginBottom: 8, fontSize: 13 }}>Subject: {preview.subject}</div>
                      <div className="preview-pane">{preview.body}</div>
                    </div>
                  )}

                  <button
                    className="btn btn-primary"
                    onClick={handleSend}
                    disabled={sending || !sendForm.template_id || !lead.email}
                  >
                    {sending ? 'Sending...' : '📤 Send Email'}
                  </button>
                  {!lead.email && (
                    <span className="text-danger" style={{ marginLeft: 10, fontSize: 12 }}>Lead has no email address</span>
                  )}
                </div>
              )}
            </>
          )}
        </div>

        <div className="modal-footer">
          <button className="btn btn-ghost" onClick={onClose} disabled={loading}>Cancel</button>
          <button className="btn btn-primary" type="submit" form="lead-form" disabled={loading}>
            {loading ? 'Saving...' : isEdit ? 'Save Changes' : 'Create Lead'}
          </button>
        </div>
      </div>
    </div>
  )
}
