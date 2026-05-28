"""
railway_sync.py
---------------
Bidirectional sync between local SQLite and Railway (PostgreSQL).

Railway → Local  (sync_from_railway):
  - Updates email addresses your team changed on Railway dashboard
  - Imports leads your team added on Railway
  - Mirrors Contacted / Replied / Bounced statuses

Local → Railway  (push_new_leads_to_railway):
  - Pushes leads the scout found locally up to Railway
  - Called automatically after every scout run

Both directions run before every send cycle so local is always current.
"""

import os
import requests
from datetime import datetime
from typing import Optional, List

_RAILWAY_URL = os.environ.get("RAILWAY_SYNC_URL", "").rstrip("/")

_SKIP_STATUSES = {"Contacted", "Replied", "Not Interested", "Feature Confirmed", "Bounced"}
_SYNC_STATUSES = list(_SKIP_STATUSES)   # statuses we pull back for local mirroring

_GENERIC_PREFIXES = (
    "contact@", "hello@", "info@", "admin@", "team@", "support@", "editor@",
    "newsletter@", "hi@", "mail@", "press@", "media@", "marketing@",
    "organizer@", "manager@", "group@", "community@", "members@",
)

_LEAD_FIELDS = [
    "name", "newsletter_name", "url", "email", "estimated_audience",
    "category", "contact_method", "linkedin_url", "twitter_handle", "notes",
]


def _fetch_railway_leads(status: Optional[str] = None, limit: int = 500) -> List[dict]:
    """Fetch leads from Railway, paginating if necessary."""
    if not _RAILWAY_URL:
        return []
    all_leads = []
    page = 1
    while True:
        try:
            params = {"per_page": 100, "page": page}
            if status:
                params["status"] = status
            resp = requests.get(f"{_RAILWAY_URL}/api/leads", params=params, timeout=10)
            if resp.status_code != 200:
                break
            data = resp.json()
            batch = data.get("data") or []
            all_leads.extend(batch)
            if len(all_leads) >= (data.get("total") or 0) or not batch:
                break
            page += 1
        except Exception as e:
            print(f"[sync] Railway fetch error (page {page}): {e}")
            break
    return all_leads


def sync_from_railway(db) -> dict:
    """
    Pull Railway state into local DB.
    Returns a summary dict: {updated, imported, status_synced}
    """
    if not _RAILWAY_URL:
        print("[sync] RAILWAY_SYNC_URL not set — skipping sync")
        return {"updated": 0, "imported": 0, "status_synced": 0}

    from models import Lead

    print("[sync] Starting Railway → local sync…")

    # ── Step 1: pull ALL Railway leads and update/import locally ─────────────
    railway_leads = _fetch_railway_leads(limit=1000)
    print(f"[sync] Fetched {len(railway_leads)} leads from Railway")

    updated = imported = 0
    now = datetime.utcnow()

    for r in railway_leads:
        r_email = (r.get("email") or "").strip().lower()

        # Try to find existing local lead by email first, then by name
        local = None
        if r_email:
            local = db.query(Lead).filter(Lead.email.ilike(r_email)).first()
        if not local and r.get("name"):
            local = db.query(Lead).filter(Lead.name == r["name"]).first()

        if local:
            changed = False
            # Update email if Railway has a fresher/better one
            if r_email and (not local.email or local.email.lower() != r_email):
                local.email = r["email"].strip()
                changed = True
            # Sync status if Railway is further along the funnel
            r_status = r.get("status") or ""
            funnel_rank = {
                "New": 0, "Email Found": 1, "Contacted": 2,
                "Replied": 3, "Feature Confirmed": 4,
                "Not Interested": 5, "No Response": 2,
                "Bounced": 6,
            }
            local_rank = funnel_rank.get(local.status or "", 0)
            railway_rank = funnel_rank.get(r_status, 0)
            if railway_rank > local_rank:
                local.status = r_status
                if r_status == "Contacted" and not local.date_contacted:
                    local.date_contacted = now
                if r_status == "Bounced" and not local.bounced_at:
                    local.bounced_at = now
                changed = True
            if changed:
                local.updated_at = now
                updated += 1
        else:
            # New lead on Railway — import it locally
            r_status = r.get("status") or "New"
            payload = {f: r.get(f) for f in _LEAD_FIELDS}
            payload["status"] = r_status
            if r_status == "Contacted":
                payload["date_contacted"] = now
            if r_status == "Bounced":
                payload["bounced_at"] = now
            new_lead = Lead(**payload)
            db.add(new_lead)
            imported += 1

    db.commit()
    print(f"[sync] Email/data update: {updated} updated, {imported} imported")

    # ── Step 2: pull each non-New status explicitly and mirror locally ───────
    # (belt-and-suspenders: catches leads that slipped through step 1)
    status_synced = 0
    for status in _SYNC_STATUSES:
        status_leads = _fetch_railway_leads(status=status)
        emails = [l["email"] for l in status_leads if l.get("email")]
        if not emails:
            continue
        rows = db.query(Lead).filter(Lead.email.in_(emails)).all()
        funnel_rank = {
            "New": 0, "Email Found": 1, "Contacted": 2,
            "Replied": 3, "Feature Confirmed": 4,
            "Not Interested": 5, "No Response": 2,
            "Bounced": 6,
        }
        target_rank = funnel_rank.get(status, 0)
        for row in rows:
            local_rank = funnel_rank.get(row.status or "", 0)
            if local_rank < target_rank:
                row.status = status
                row.updated_at = now
                if status == "Contacted" and not row.date_contacted:
                    row.date_contacted = now
                if status == "Bounced" and not row.bounced_at:
                    row.bounced_at = now
                status_synced += 1
        db.commit()

    print(f"[sync] Status mirror: {status_synced} leads updated")
    print(f"[sync] ✅ Sync complete — {updated} updated, {imported} imported, {status_synced} statuses fixed")
    return {"updated": updated, "imported": imported, "status_synced": status_synced}


def push_new_leads_to_railway(db, leads: list) -> dict:
    """
    Push a list of newly-scouted local Lead objects up to Railway.
    Called by the lead scout after it inserts new leads into local DB.
    Skips leads that already exist on Railway (matched by email or name).
    Returns {pushed, skipped}.
    """
    if not _RAILWAY_URL:
        return {"pushed": 0, "skipped": 0}

    # Fetch current Railway emails so we don't duplicate
    existing = _fetch_railway_leads(limit=2000)
    railway_emails = {(l.get("email") or "").lower() for l in existing if l.get("email")}
    railway_names  = {(l.get("name") or "").lower() for l in existing if l.get("name")}

    pushed = skipped = 0
    for lead in leads:
        email_key = (lead.email or "").lower()
        name_key  = (lead.name  or "").lower()
        if email_key and email_key in railway_emails:
            skipped += 1
            continue
        if name_key and name_key in railway_names:
            skipped += 1
            continue

        payload = {f: getattr(lead, f, None) for f in _LEAD_FIELDS}
        payload["status"] = lead.status or "New"
        try:
            resp = requests.post(
                f"{_RAILWAY_URL}/api/leads",
                json={k: v for k, v in payload.items() if v is not None},
                timeout=8,
            )
            if resp.status_code in (200, 201):
                pushed += 1
                if email_key:
                    railway_emails.add(email_key)
                print(f"[sync→railway] ✓ {lead.name} ({lead.email or 'no email'})")
            else:
                print(f"[sync→railway] ✗ {lead.name}: HTTP {resp.status_code}")
        except Exception as e:
            print(f"[sync→railway] ✗ {lead.name}: {e}")

    print(f"[sync→railway] Pushed {pushed} new leads to Railway ({skipped} already there)")
    return {"pushed": pushed, "skipped": skipped}
