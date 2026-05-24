import { useState, useEffect } from 'react'
import api from '../api.js'
import TemplateModal from './TemplateModal.jsx'

export default function Templates() {
  const [templates, setTemplates] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [modal, setModal] = useState(null) // null | 'create' | template object

  async function fetchTemplates() {
    setLoading(true)
    setError(null)
    try {
      const res = await api.get('/templates')
      setTemplates(res.data.data || [])
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchTemplates() }, [])

  async function deleteTemplate(e, id) {
    e.stopPropagation()
    if (!window.confirm('Delete this template?')) return
    try {
      await api.delete(`/templates/${id}`)
      fetchTemplates()
    } catch (e) {
      alert(e.message)
    }
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <h2>Templates</h2>
          <p>Email templates with A/B subject lines and follow-up sequences</p>
        </div>
        <button className="btn btn-primary" onClick={() => setModal('create')}>
          + New Template
        </button>
      </div>

      {loading ? (
        <div className="loading-spinner"><div className="spinner" /> Loading templates...</div>
      ) : error ? (
        <div className="alert alert-error">{error}</div>
      ) : templates.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">✉️</div>
          <h3>No templates yet</h3>
          <p>Create your first email template</p>
        </div>
      ) : (
        <div className="template-grid">
          {templates.map(t => (
            <div className="template-card" key={t.id} onClick={() => setModal(t)}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <h3>{t.name}</h3>
                  <div className="template-category">{t.category}</div>
                </div>
                <button
                  className="btn btn-xs btn-danger"
                  onClick={e => deleteTemplate(e, t.id)}
                  style={{ flexShrink: 0 }}
                >
                  ✕
                </button>
              </div>

              <div className="template-subject">
                <strong>Subject A:</strong> {t.subject_a ? t.subject_a.slice(0, 60) + (t.subject_a.length > 60 ? '…' : '') : '—'}
              </div>
              <div className="template-subject">
                <strong>Subject B:</strong> {t.subject_b ? t.subject_b.slice(0, 60) + (t.subject_b.length > 60 ? '…' : '') : '—'}
              </div>

              {t.followup1_subject && (
                <div className="template-subject" style={{ marginTop: 8 }}>
                  <strong>FU1:</strong> {t.followup1_subject.slice(0, 50) + (t.followup1_subject.length > 50 ? '…' : '')}
                </div>
              )}
              {t.followup2_subject && (
                <div className="template-subject">
                  <strong>FU2:</strong> {t.followup2_subject.slice(0, 50) + (t.followup2_subject.length > 50 ? '…' : '')}
                </div>
              )}

              <div style={{ marginTop: 12, fontSize: 11, color: 'var(--text-muted)' }}>
                Updated {t.updated_at ? new Date(t.updated_at).toLocaleDateString() : '—'}
              </div>
            </div>
          ))}
        </div>
      )}

      {modal && (
        <TemplateModal
          template={modal === 'create' ? null : modal}
          onClose={() => setModal(null)}
          onSave={fetchTemplates}
        />
      )}
    </div>
  )
}
