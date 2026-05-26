import { useState, useEffect } from 'react'
import api from '../api.js'

const TIMEZONES = [
  'Asia/Kolkata',
  'America/New_York',
  'America/Chicago',
  'America/Denver',
  'America/Los_Angeles',
  'Europe/London',
  'Europe/Berlin',
  'Europe/Paris',
  'Asia/Dubai',
  'Asia/Singapore',
  'Asia/Tokyo',
  'Australia/Sydney',
  'Pacific/Auckland',
]

export default function Settings() {
  const [form, setForm] = useState({
    sender_name: '',
    gmail_email: '',
    gmail_app_password: '',
    resend_api_key: '',
    gmail_client_id: '',
    gmail_client_secret: '',
    gmail_refresh_token: '',
    daily_send_limit: 20,
    followup1_days: 4,
    followup2_days: 9,
    send_hours_start: 9,
    send_hours_end: 17,
    timezone: 'America/Los_Angeles',
    imap_enabled: false,
  })
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [testing, setTesting] = useState(false)
  const [error, setError] = useState(null)
  const [saveMsg, setSaveMsg] = useState(null)
  const [testMsg, setTestMsg] = useState(null)

  async function fetchSettings() {
    setLoading(true)
    try {
      const res = await api.get('/settings')
      const d = res.data.data
      setForm({
        sender_name: d.sender_name || '',
        gmail_email: d.gmail_email || '',
        gmail_app_password: d.gmail_app_password || '',
        resend_api_key: d.resend_api_key || '',
        gmail_client_id: d.gmail_client_id || '',
        gmail_client_secret: d.gmail_client_secret || '',
        gmail_refresh_token: d.gmail_refresh_token || '',
        daily_send_limit: d.daily_send_limit ?? 20,
        followup1_days: d.followup1_days ?? 4,
        followup2_days: d.followup2_days ?? 9,
        send_hours_start: d.send_hours_start ?? 9,
        send_hours_end: d.send_hours_end ?? 17,
        timezone: d.timezone || 'America/Los_Angeles',
        imap_enabled: d.imap_enabled ?? false,
      })
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchSettings() }, [])

  function set(field) {
    return e => {
      const val = e.target.type === 'checkbox' ? e.target.checked :
        e.target.type === 'number' ? Number(e.target.value) : e.target.value
      setForm(f => ({ ...f, [field]: val }))
    }
  }

  async function handleSave(e) {
    e.preventDefault()
    setSaving(true)
    setSaveMsg(null)
    setError(null)
    try {
      await api.put('/settings', form)
      setSaveMsg({ type: 'success', text: 'Settings saved successfully!' })
      setTimeout(() => setSaveMsg(null), 3000)
    } catch (e) {
      setSaveMsg({ type: 'error', text: e.message })
    } finally {
      setSaving(false)
    }
  }

  async function testConnection() {
    setTesting(true)
    setTestMsg(null)
    try {
      const res = await api.get('/settings/test')
      setTestMsg({ type: 'success', text: res.data.message })
    } catch (e) {
      setTestMsg({ type: 'error', text: e.message })
    } finally {
      setTesting(false)
    }
  }

  if (loading) return <div className="loading-spinner"><div className="spinner" /> Loading settings...</div>

  return (
    <div>
      <div className="page-header">
        <div>
          <h2>Settings</h2>
          <p>Configure your Gmail account and sending preferences</p>
        </div>
      </div>

      {error && <div className="alert alert-error mb-16">{error}</div>}

      <form onSubmit={handleSave}>

        {/* Gmail API — Recommended */}
        <div className="settings-section">
          <h3>📧 Gmail API (OAuth2) <span style={{fontSize:12,background:'#dcfce7',color:'#166534',padding:'2px 8px',borderRadius:4,marginLeft:8}}>Recommended</span></h3>

          <div className="alert alert-info mb-16" style={{lineHeight:1.7}}>
            <strong>Railway blocks SMTP — use Gmail API instead (HTTPS, always works).</strong><br/>
            One-time 5-min setup:<br/>
            1. <a href="https://console.cloud.google.com/" target="_blank" rel="noreferrer">Google Cloud Console</a> → New project → <strong>Enable Gmail API</strong><br/>
            2. APIs &amp; Services → Credentials → <strong>Create OAuth 2.0 Client ID</strong> (type: Web app)<br/>
            &nbsp;&nbsp;&nbsp;Add <code>https://developers.google.com/oauthplayground</code> as Authorized Redirect URI<br/>
            3. <a href="https://developers.google.com/oauthplayground/" target="_blank" rel="noreferrer">OAuth Playground</a> → ⚙️ → check "Use your own OAuth credentials" → paste Client ID &amp; Secret<br/>
            4. Step 1: select <code>Gmail API v1 → .../auth/gmail.send</code> → Authorize<br/>
            5. Step 2: Exchange auth code for tokens → copy <strong>Refresh token</strong><br/>
            6. Paste Client ID, Client Secret, and Refresh Token below → Save
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>OAuth Client ID</label>
              <input className="form-control" type="password" value={form.gmail_client_id}
                onChange={set('gmail_client_id')} placeholder="xxxxx.apps.googleusercontent.com" />
            </div>
            <div className="form-group">
              <label>OAuth Client Secret</label>
              <input className="form-control" type="password" value={form.gmail_client_secret}
                onChange={set('gmail_client_secret')} placeholder="GOCSPX-..." />
            </div>
          </div>

          <div className="form-group">
            <label>Refresh Token</label>
            <input className="form-control" type="password" value={form.gmail_refresh_token}
              onChange={set('gmail_refresh_token')} placeholder="1//0g..." />
            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4 }}>
              Never expires. Emails send from your Gmail and appear in Sent folder.
            </div>
          </div>
        </div>

        {/* Gmail SMTP — Fallback */}
        <div className="settings-section">
          <h3>Gmail Configuration <span style={{fontSize:12,background:'#fef9c3',color:'#854d0e',padding:'2px 8px',borderRadius:4,marginLeft:8}}>Fallback (blocked on Railway)</span></h3>

          <div className="alert alert-info mb-16">
            Used only when Gmail API credentials above are not set. Railway blocks SMTP so this may not work.
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Sender Name</label>
              <input className="form-control" value={form.sender_name} onChange={set('sender_name')} placeholder="Rishi" />
            </div>
            <div className="form-group">
              <label>Gmail Address</label>
              <input className="form-control" type="email" value={form.gmail_email} onChange={set('gmail_email')} placeholder="you@gmail.com" />
            </div>
          </div>

          <div className="form-group">
            <label>Gmail App Password</label>
            <div className="password-input-wrapper">
              <input
                className="form-control"
                type={showPassword ? 'text' : 'password'}
                value={form.gmail_app_password}
                onChange={set('gmail_app_password')}
                placeholder="xxxx xxxx xxxx xxxx"
                style={{ paddingRight: 40 }}
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowPassword(s => !s)}
                title={showPassword ? 'Hide' : 'Show'}
              >
                {showPassword ? '🙈' : '👁'}
              </button>
            </div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4 }}>
              16-character app password from myaccount.google.com/apppasswords
            </div>
          </div>

          {testMsg && (
            <div className={`alert alert-${testMsg.type === 'success' ? 'success' : 'error'} mb-12`}>
              {testMsg.text}
            </div>
          )}

          <button
            type="button"
            className="btn btn-ghost"
            onClick={testConnection}
            disabled={testing || !form.gmail_email || !form.gmail_app_password}
          >
            {testing ? '⏳ Testing...' : '🔌 Test Connection'}
          </button>
        </div>

        {/* Sending Schedule */}
        <div className="settings-section">
          <h3>Sending Schedule</h3>

          <div className="form-row-3">
            <div className="form-group">
              <label>Daily Send Limit</label>
              <input className="form-control" type="number" min="1" max="100" value={form.daily_send_limit} onChange={set('daily_send_limit')} />
              <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4 }}>
                Recommended: 20/day for Gmail
              </div>
            </div>
            <div className="form-group">
              <label>Send Hours Start</label>
              <input className="form-control" type="number" min="0" max="23" value={form.send_hours_start} onChange={set('send_hours_start')} />
            </div>
            <div className="form-group">
              <label>Send Hours End</label>
              <input className="form-control" type="number" min="0" max="23" value={form.send_hours_end} onChange={set('send_hours_end')} />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Timezone</label>
              <select className="form-control" value={form.timezone} onChange={set('timezone')}>
                {TIMEZONES.map(tz => <option key={tz} value={tz}>{tz}</option>)}
              </select>
            </div>
            <div style={{ fontSize: 13, color: 'var(--text-secondary)', paddingTop: 28 }}>
              Emails only send between {form.send_hours_start}:00–{form.send_hours_end}:00 {form.timezone}
            </div>
          </div>
        </div>

        {/* Follow-up Schedule */}
        <div className="settings-section">
          <h3>Follow-up Schedule</h3>

          <div className="form-row">
            <div className="form-group">
              <label>Follow-up 1 (days after initial)</label>
              <input className="form-control" type="number" min="1" max="30" value={form.followup1_days} onChange={set('followup1_days')} />
            </div>
            <div className="form-group">
              <label>Follow-up 2 (days after initial)</label>
              <input className="form-control" type="number" min="1" max="60" value={form.followup2_days} onChange={set('followup2_days')} />
            </div>
          </div>
          <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
            Timeline: Initial → {form.followup1_days} days → Follow-up 1 → {form.followup2_days - form.followup1_days} days → Follow-up 2
          </div>
        </div>

        {/* IMAP Reply Detection */}
        <div className="settings-section">
          <h3>Reply Detection (IMAP)</h3>

          <div className="alert alert-warning mb-16">
            When enabled, the system checks your Gmail inbox every 2 hours for replies. If a replied lead is detected, their status is updated to "Replied" and pending follow-ups are cancelled automatically.
          </div>

          <div className="form-group">
            <label style={{ display: 'flex', alignItems: 'center', gap: 10, cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={form.imap_enabled}
                onChange={set('imap_enabled')}
                style={{ width: 16, height: 16, cursor: 'pointer' }}
              />
              <span>Enable IMAP Reply Checking</span>
            </label>
            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 6 }}>
              Requires Gmail IMAP to be enabled in your Gmail settings (Settings → See all settings → Forwarding and POP/IMAP → Enable IMAP)
            </div>
          </div>
        </div>

        {/* Save */}
        {saveMsg && (
          <div className={`alert alert-${saveMsg.type === 'success' ? 'success' : 'error'} mb-16`}>
            {saveMsg.text}
          </div>
        )}

        <button className="btn btn-primary btn-lg" type="submit" disabled={saving}>
          {saving ? 'Saving...' : '💾 Save Settings'}
        </button>
      </form>
    </div>
  )
}
