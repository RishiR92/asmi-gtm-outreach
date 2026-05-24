import { useState, useEffect } from 'react'
import api from '../api.js'

const CATEGORIES = ['AI Tools', 'Productivity', 'Indian-Origin', 'Startup-Founder', 'Business Owner', 'Niche']
const VARS = ['{{name}}', '{{newsletter}}', '{{audience}}', '{{custom_line}}']

const SAMPLE = {
  name: 'Matt Wolfe',
  newsletter: 'Future Tools',
  audience: '230,000',
  custom_line: 'I loved your recent breakdown of Cursor vs. Copilot.',
}

function renderPreview(str) {
  if (!str) return ''
  return str
    .replace(/\{\{name\}\}/g, SAMPLE.name)
    .replace(/\{\{newsletter\}\}/g, SAMPLE.newsletter)
    .replace(/\{\{audience\}\}/g, SAMPLE.audience)
    .replace(/\{\{custom_line\}\}/g, SAMPLE.custom_line)
}

const EMPTY = {
  name: '', category: 'AI Tools',
  subject_a: '', subject_b: '', body: '',
  followup1_subject: '', followup1_body: '',
  followup2_subject: '', followup2_body: '',
}

export default function TemplateModal({ template, onClose, onSave }) {
  const [form, setForm] = useState(EMPTY)
  const [activeTab, setActiveTab] = useState('initial')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  const [showPreview, setShowPreview] = useState(false)

  const isEdit = !!template?.id

  useEffect(() => {
    if (template) {
      setForm({
        name: template.name || '',
        category: template.category || 'AI Tools',
        subject_a: template.subject_a || '',
        subject_b: template.subject_b || '',
        body: template.body || '',
        followup1_subject: template.followup1_subject || '',
        followup1_body: template.followup1_body || '',
        followup2_subject: template.followup2_subject || '',
        followup2_body: template.followup2_body || '',
      })
    }
  }, [template])

  function set(field) {
    return e => setForm(f => ({ ...f, [field]: e.target.value }))
  }

  function insertVar(v, field) {
    setForm(f => {
      const val = f[field] || ''
      return { ...f, [field]: val + v }
    })
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setSuccess(null)
    try {
      if (isEdit) {
        await api.put(`/templates/${template.id}`, form)
      } else {
        await api.post('/templates', form)
      }
      setSuccess(isEdit ? 'Template updated!' : 'Template created!')
      setTimeout(() => { onSave(); onClose() }, 700)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const previewSubject = activeTab === 'initial' ? form.subject_a :
    activeTab === 'followup1' ? form.followup1_subject : form.followup2_subject
  const previewBody = activeTab === 'initial' ? form.body :
    activeTab === 'followup1' ? form.followup1_body : form.followup2_body

  return (
    <div className="modal-overlay" onClick={e => { if (e.target === e.currentTarget) onClose() }}>
      <div className="modal modal-lg">
        <div className="modal-header">
          <h3>{isEdit ? `Edit: ${template.name}` : 'New Template'}</h3>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        <div className="modal-body">
          {error && <div className="alert alert-error mb-16">{error}</div>}
          {success && <div className="alert alert-success mb-16">{success}</div>}

          <form onSubmit={handleSubmit} id="template-form">
            <div className="form-row">
              <div className="form-group">
                <label>Template Name *</label>
                <input className="form-control" value={form.name} onChange={set('name')} required placeholder="AI Tools Newsletter" />
              </div>
              <div className="form-group">
                <label>Category</label>
                <select className="form-control" value={form.category} onChange={set('category')}>
                  {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>
            </div>

            {/* Variable Reference */}
            <div className="form-group">
              <label>Template Variables (click to insert into active field)</label>
              <div>
                {VARS.map(v => (
                  <span
                    key={v}
                    className="var-chip"
                    onClick={() => {
                      const fieldMap = {
                        initial: 'body', followup1: 'followup1_body', followup2: 'followup2_body'
                      }
                      insertVar(v, fieldMap[activeTab])
                    }}
                  >
                    {v}
                  </span>
                ))}
                <span style={{ fontSize: 11, color: 'var(--text-muted)', marginLeft: 8 }}>
                  Preview uses sample values
                </span>
              </div>
            </div>

            {/* Tabs */}
            <div className="tabs">
              {[['initial', 'Initial Email'], ['followup1', 'Follow-up 1'], ['followup2', 'Follow-up 2']].map(([key, label]) => (
                <button
                  key={key}
                  type="button"
                  className={`tab-btn ${activeTab === key ? 'active' : ''}`}
                  onClick={() => setActiveTab(key)}
                >
                  {label}
                </button>
              ))}
            </div>

            {activeTab === 'initial' && (
              <>
                <div className="form-group">
                  <label>Subject A</label>
                  <input className="form-control" value={form.subject_a} onChange={set('subject_a')} placeholder="Feature opportunity for {{newsletter}} readers" />
                </div>
                <div className="form-group">
                  <label>Subject B</label>
                  <input className="form-control" value={form.subject_b} onChange={set('subject_b')} placeholder="Your {{audience}} readers would love this" />
                </div>
                <div className="form-group">
                  <label>Email Body</label>
                  <textarea className="form-control" rows={10} value={form.body} onChange={set('body')} />
                </div>
              </>
            )}

            {activeTab === 'followup1' && (
              <>
                <div className="form-group">
                  <label>Subject</label>
                  <input className="form-control" value={form.followup1_subject} onChange={set('followup1_subject')} />
                </div>
                <div className="form-group">
                  <label>Body</label>
                  <textarea className="form-control" rows={8} value={form.followup1_body} onChange={set('followup1_body')} />
                </div>
              </>
            )}

            {activeTab === 'followup2' && (
              <>
                <div className="form-group">
                  <label>Subject</label>
                  <input className="form-control" value={form.followup2_subject} onChange={set('followup2_subject')} />
                </div>
                <div className="form-group">
                  <label>Body</label>
                  <textarea className="form-control" rows={8} value={form.followup2_body} onChange={set('followup2_body')} />
                </div>
              </>
            )}
          </form>

          {/* Preview Toggle */}
          <div style={{ marginTop: 16 }}>
            <button className="btn btn-ghost btn-sm" onClick={() => setShowPreview(s => !s)}>
              {showPreview ? 'Hide Preview' : '👁 Show Preview'}
            </button>
            {showPreview && (
              <div style={{ marginTop: 12 }}>
                <div style={{ fontWeight: 700, fontSize: 13, marginBottom: 6 }}>
                  Subject: {renderPreview(previewSubject) || '(empty)'}
                </div>
                <div className="preview-pane">{renderPreview(previewBody) || '(empty)'}</div>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 6 }}>
                  Previewing with sample values: name="{SAMPLE.name}", newsletter="{SAMPLE.newsletter}", audience="{SAMPLE.audience}"
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="modal-footer">
          <button className="btn btn-ghost" onClick={onClose} disabled={loading}>Cancel</button>
          <button className="btn btn-primary" type="submit" form="template-form" disabled={loading}>
            {loading ? 'Saving...' : isEdit ? 'Save Changes' : 'Create Template'}
          </button>
        </div>
      </div>
    </div>
  )
}
