# Cold Outreach System

A complete newsletter outreach management system for Asmi. Manage leads, send personalized emails via Gmail, auto-schedule follow-ups, and detect replies — all running locally with no paid APIs.

---

## Prerequisites

- **Python 3.9+** — [python.org/downloads](https://www.python.org/downloads/)
- **Node.js 18+** — [nodejs.org](https://nodejs.org/)
- A **Gmail account** with 2-Factor Authentication enabled

---

## Quick Start

```bash
cd cold-outreach
chmod +x start.sh
./start.sh
```

Then open **http://localhost:3000** in your browser.

On first run, the script:
1. Creates a Python virtual environment and installs dependencies
2. Installs Node.js frontend dependencies
3. Seeds the database with 35 leads and 5 templates
4. Starts both servers (backend on :8000, frontend on :3000)

---

## Gmail App Password Setup

You **cannot** use your regular Gmail password. You need a 16-character App Password.

### Step-by-step:

1. Go to **myaccount.google.com**
2. Click **Security** in the left sidebar
3. Under "How you sign in to Google", click **2-Step Verification** (must be enabled)
4. Scroll to the bottom and click **App passwords**
   - Direct link: **myaccount.google.com/apppasswords**
5. In the "App name" field, type `Cold Outreach`
6. Click **Create**
7. Copy the 16-character password shown (e.g., `abcd efgh ijkl mnop`)

### Add to .env:

Open `backend/.env` and fill in:

```env
GMAIL_EMAIL=yourname@gmail.com
GMAIL_APP_PASSWORD=abcd efgh ijkl mnop
SENDER_NAME=Rishi
```

Then go to the **Settings** page in the app and click **Test Connection** to verify.

---

## Features

### Dashboard
- Pipeline overview — see lead counts by status at a glance
- Reply rate and weekly send count metrics
- Follow-ups due today with one-click "Send Now"
- Recent activity feed (last 10 emails)

### Leads
- Full CRUD for leads with all fields
- Search by name, newsletter, email, or URL
- Filter by status and category
- Import leads from CSV (auto-detects email presence to set status)
- Export all leads to CSV
- Click any row to edit
- Quick-mark as Replied or Not Interested from the table
- Send email directly from the lead modal with template selector and live preview

### Email Finder
- **Pattern Guesser** — enter first name, last name, and domain to generate 9 email patterns (first@, first.last@, f.last@, etc.)
- Copy patterns to clipboard or select + save directly to a lead
- **Hunter.io Quick Lookup** — opens Hunter.io for the domain in a new tab (25 free searches/month)

### Templates
- 5 pre-seeded templates (AI Tools, Productivity, Indian-Origin, Startup/PM, Business Owners)
- Each template has: Subject A + Subject B (A/B testing), body, follow-up 1, follow-up 2
- Full editor with tab navigation between Initial / Follow-up 1 / Follow-up 2
- Live preview with sample values
- Template variables: `{{name}}`, `{{newsletter}}`, `{{audience}}`, `{{custom_line}}`

### Send Queue
- View all scheduled follow-up emails (pending)
- Filter: Today / This Week / All Pending
- Send any follow-up immediately with "Send Now"
- Cancel scheduled emails
- Email log with status (sent/failed) and error messages

### Settings
- Gmail credentials (sender name, email, app password with show/hide toggle)
- Daily send limit (default: 20)
- Send hours (only sends between 9am–5pm in your timezone)
- Follow-up timing (default: Day 4 and Day 9 after initial)
- Timezone selection
- IMAP reply detection toggle
- **Test Connection** button — verifies SMTP without sending any email

---

## CSV Import Format

Import leads via CSV with any of these column headers (case-insensitive, underscores or spaces):

| Column | Description |
|--------|-------------|
| `name` | Contact name (required) |
| `newsletter_name` | Name of the newsletter |
| `url` | Website URL (used to detect duplicates) |
| `estimated_audience` | Integer audience size |
| `category` | AI Tools / Productivity / Indian-Origin / Startup-Founder / Business Owner / Niche |
| `contact_method` | Email / X DM / LinkedIn / Submission Form |
| `email` | Email address (if present, status auto-sets to "Email Found") |
| `linkedin_url` | LinkedIn profile URL |
| `twitter_handle` | Twitter/X handle |
| `notes` | Any notes |
| `status` | Override status manually |

**Duplicate detection:** Rows with the same `url` as an existing lead are skipped.

**Example CSV:**
```csv
name,newsletter_name,url,estimated_audience,category,email
Jane Doe,The AI Weekly,aiweekly.com,45000,AI Tools,jane@aiweekly.com
```

---

## How Reply Detection Works

When IMAP is enabled in Settings:

1. Every **2 hours**, the backend connects to Gmail via IMAP
2. It fetches emails received in the last 24 hours
3. For each email, it checks if the sender's address matches any lead with status "Contacted"
4. If a match is found:
   - Lead status is updated to **"Replied"**
   - All pending scheduled follow-ups for that lead are **cancelled**
5. This runs automatically in the background — no action required

**To enable IMAP in Gmail:** Settings → See all settings → Forwarding and POP/IMAP → IMAP Access → Enable IMAP

---

## Daily Sending Limits

Gmail has sending limits to prevent spam flagging:

- **Free Gmail accounts:** ~500 emails/day hard limit
- **Google Workspace accounts:** ~2,000 emails/day
- **Recommended:** Start at **20/day** (the default) and ramp up slowly

The app enforces the limit set in Settings. Once the daily limit is reached, no more emails send until the next calendar day (UTC).

**Best practices:**
- Send during business hours (the scheduler respects your configured hours)
- Personalize the `{{custom_line}}` for each lead — increases reply rates significantly
- Use A/B subject testing to find what resonates with each audience category

---

## Architecture

```
cold-outreach/
├── backend/          FastAPI + SQLite (SQLAlchemy)
│   ├── main.py       App entry point, startup tasks
│   ├── database.py   SQLAlchemy engine + session
│   ├── models.py     Lead, EmailLog, ScheduledEmail, Template, AppSettings
│   ├── schemas.py    Pydantic request/response models
│   ├── seed_data.py  Initial 35 leads + 5 templates
│   ├── routers/      API endpoints
│   └── services/     Email sender, IMAP checker, scheduler
└── frontend/         React + Vite SPA
    └── src/
        └── components/  Dashboard, Leads, Templates, etc.
```

**Background tasks (auto-start on boot):**
- **Scheduler** — runs every 15 minutes, fires any due scheduled emails within configured send hours
- **Reply Checker** — runs every 2 hours, checks Gmail inbox for replies (if IMAP enabled)

---

## API Reference

Interactive API docs available at **http://localhost:8000/docs** when the backend is running.

Key endpoints:
- `GET /api/dashboard/stats` — all dashboard metrics
- `GET/POST/PUT/DELETE /api/leads` — lead management
- `POST /api/leads/import` — CSV import
- `GET /api/leads/export` — CSV export
- `POST /api/emails/send` — send initial email + schedule follow-ups
- `GET /api/emails/queue` — pending scheduled emails
- `GET /api/emails/logs` — sent email history
- `POST /api/emails/guess-pattern` — email pattern guesser
- `GET/PUT /api/settings` — app settings
- `GET /api/settings/test` — test SMTP connection
