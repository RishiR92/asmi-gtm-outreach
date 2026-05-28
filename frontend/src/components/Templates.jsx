import { useState, useEffect } from 'react'
import api from '../api.js'
import TemplateModal from './TemplateModal.jsx'

export default function Templates() {
  const [templates, setTemplates] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [modal, setModal] = useState(null) // null | template object

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

  // The single active template is always the first one
  const activeTemplate = templates[0] || null

  return (
    <div>
      <div className="page-header">
        <div>
          <h2>Outreach Template</h2>
          <p>Single finalised template used for all outreach — edit subject lines, body, and follow-ups here</p>
        </div>
        {activeTemplate && (
          <button className="btn btn-primary" onClick={() => setModal(activeTemplate)}>
            ✏️ Edit Template
          </button>
        )}
      </div>

      {loading ? (
        <div className="loading-spinner"><div className="spinner" /> Loading template...</div>
      ) : error ? (
        <div className="alert alert-error">{error}</div>
      ) : !activeTemplate ? (
        <div className="empty-state">
          <div className="empty-icon">✉️</div>
          <h3>No template yet</h3>
          <p>Contact support to initialise the default template</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>

          {/* Header card */}
          <div className="card" style={{ border: '2px solid #2563eb', cursor: 'pointer' }} onClick={() => setModal(activeTemplate)}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 16 }}>
              <div>
                <h3 style={{ margin: 0, color: '#1e293b' }}>{activeTemplate.name}</h3>
                <div className="template-category" style={{ marginTop: 4 }}>{activeTemplate.category}</div>
              </div>
              <span style={{
                background: '#eff6ff', color: '#2563eb', border: '1px solid #bfdbfe',
                borderRadius: 20, padding: '3px 12px', fontSize: 11, fontWeight: 700,
              }}>ACTIVE</span>
            </div>

            {/* Subject lines */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 16 }}>
              <div style={{ background: '#f8fafc', borderRadius: 8, padding: 12 }}>
                <div style={{ fontSize: 10, fontWeight: 700, color: '#64748b', textTransform: 'uppercase', marginBottom: 4 }}>Subject A</div>
                <div style={{ fontSize: 13, color: '#1e293b' }}>{activeTemplate.subject_a || '—'}</div>
              </div>
              <div style={{ background: '#f8fafc', borderRadius: 8, padding: 12 }}>
                <div style={{ fontSize: 10, fontWeight: 700, color: '#64748b', textTransform: 'uppercase', marginBottom: 4 }}>Subject B</div>
                <div style={{ fontSize: 13, color: '#1e293b' }}>{activeTemplate.subject_b || '—'}</div>
              </div>
            </div>

            {/* Body preview */}
            <div style={{ marginBottom: 16 }}>
              <div style={{ fontSize: 10, fontWeight: 700, color: '#64748b', textTransform: 'uppercase', marginBottom: 6 }}>Body</div>
              <div style={{
                background: '#f8fafc', borderRadius: 8, padding: 14,
                fontSize: 13, color: '#334155', whiteSpace: 'pre-wrap', lineHeight: 1.6,
                maxHeight: 200, overflow: 'auto',
              }}>
                {activeTemplate.body || '—'}
              </div>
            </div>

            {/* Follow-ups */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <div style={{ background: '#fefce8', borderRadius: 8, padding: 12, border: '1px solid #fde68a' }}>
                <div style={{ fontSize: 10, fontWeight: 700, color: '#92400e', textTransform: 'uppercase', marginBottom: 4 }}>Follow-up 1</div>
                <div style={{ fontSize: 12, fontWeight: 600, color: '#1e293b', marginBottom: 4 }}>{activeTemplate.followup1_subject || '—'}</div>
                <div style={{ fontSize: 12, color: '#64748b', whiteSpace: 'pre-wrap', maxHeight: 100, overflow: 'auto' }}>
                  {activeTemplate.followup1_body || '—'}
                </div>
              </div>
              <div style={{ background: '#fefce8', borderRadius: 8, padding: 12, border: '1px solid #fde68a' }}>
                <div style={{ fontSize: 10, fontWeight: 700, color: '#92400e', textTransform: 'uppercase', marginBottom: 4 }}>Follow-up 2</div>
                <div style={{ fontSize: 12, fontWeight: 600, color: '#1e293b', marginBottom: 4 }}>{activeTemplate.followup2_subject || '—'}</div>
                <div style={{ fontSize: 12, color: '#64748b', whiteSpace: 'pre-wrap', maxHeight: 100, overflow: 'auto' }}>
                  {activeTemplate.followup2_body || '—'}
                </div>
              </div>
            </div>

            <div style={{ marginTop: 12, fontSize: 11, color: '#94a3b8' }}>
              Last updated {activeTemplate.updated_at ? new Date(activeTemplate.updated_at).toLocaleDateString() : '—'} · Click anywhere to edit
            </div>
          </div>

          {/* Channel-ask preview */}
          <div className="card">
            <div style={{ fontWeight: 700, fontSize: 13, color: '#1e293b', marginBottom: 4 }}>
              {'{{channel_ask}}'} — auto-fills based on lead category
            </div>
            <p style={{ fontSize: 12, color: '#64748b', marginBottom: 12 }}>
              The line <em>"Would love to {'{{channel_ask}}'}"</em> gets personalised per contact type at send time.
            </p>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: 8 }}>
              {[
                { cat: 'Newsletter',  icon: '✉️',  ask: 'feature Asmi for your readers' },
                { cat: 'Creator',     icon: '🎥',  ask: 'feature Asmi in a video or post' },
                { cat: 'Community',   icon: '💬',  ask: 'share Asmi with your community' },
                { cat: 'Podcast',     icon: '🎙️', ask: 'mention Asmi on your show — happy to come on as a guest too' },
                { cat: 'University',  icon: '🎓',  ask: 'share Asmi with your club members' },
                { cat: 'Accelerator', icon: '🚀',  ask: 'share Asmi with your founders and portfolio' },
                { cat: 'Directory',   icon: '📂',  ask: 'list Asmi on your platform' },
              ].map(({ cat, icon, ask }) => (
                <div key={cat} style={{
                  background: '#f8fafc', borderRadius: 8, padding: '10px 12px',
                  border: '1px solid #e2e8f0', fontSize: 12,
                }}>
                  <div style={{ fontWeight: 700, color: '#334155', marginBottom: 4 }}>{icon} {cat}</div>
                  <div style={{ color: '#475569', fontStyle: 'italic' }}>"{ask}"</div>
                </div>
              ))}
            </div>
          </div>

          {/* Available tokens */}
          <div className="card">
            <div style={{ fontWeight: 700, fontSize: 13, color: '#1e293b', marginBottom: 10 }}>All template variables</div>
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              {['{{name}}', '{{newsletter}}', '{{audience}}', '{{channel_ask}}', '{{custom_line}}'].map(token => (
                <code key={token} style={{
                  background: '#f1f5f9', border: '1px solid #e2e8f0',
                  borderRadius: 6, padding: '3px 10px', fontSize: 12, color: '#0f172a',
                }}>{token}</code>
              ))}
            </div>
          </div>
        </div>
      )}

      {modal && (
        <TemplateModal
          template={modal}
          onClose={() => setModal(null)}
          onSave={fetchTemplates}
        />
      )}
    </div>
  )
}
