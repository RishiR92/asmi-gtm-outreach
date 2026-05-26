import base64
import smtplib
import os
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy import func
from datetime import date, datetime

_RAILWAY_URL = os.environ.get("RAILWAY_SYNC_URL", "").rstrip("/")

def _mirror_status_to_railway(email: str, status: str):
    """Fire-and-forget: mark this email as Contacted on Railway too."""
    if not _RAILWAY_URL or not email:
        return
    try:
        requests.post(
            f"{_RAILWAY_URL}/api/leads/bulk-status",
            json={"emails": [email], "status": status},
            timeout=5,
        )
    except Exception:
        pass  # never block a local send over a sync failure


def _first_name(full_name: str) -> str:
    """Extract first name — handles 'First Last', 'Last, First', single names."""
    if not full_name:
        return ""
    name = full_name.strip()
    if "," in name:
        name = name.split(",", 1)[1].strip()
    first = name.split()[0] if name.split() else name
    return first.capitalize()


def render_template(body: str, lead, custom_line: str = "") -> str:
    if not body:
        return ""
    fname = _first_name(lead.name or "")
    result = body.replace("{{name}}", fname)
    result = result.replace("{{first_name}}", fname)
    result = result.replace("{{full_name}}", lead.name or "")
    result = result.replace("{{newsletter}}", lead.newsletter_name or "")
    result = result.replace("{{audience}}", str(lead.estimated_audience) if lead.estimated_audience else "")
    result = result.replace("{{custom_line}}", custom_line or "")
    return result


# ── Send backends ──────────────────────────────────────────────────────────────

def _send_via_gmail_api(to_email: str, subject: str, body: str,
                         from_email: str, from_name: str,
                         client_id: str, client_secret: str, refresh_token: str):
    """
    Send via Gmail API over HTTPS — works on Railway (no SMTP ports needed).
    Uses OAuth2 refresh token to get a short-lived access token per send.
    Emails appear in Gmail Sent folder automatically.
    """
    # 1. Exchange refresh token for access token
    token_resp = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id":     client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "grant_type":    "refresh_token",
        },
        timeout=15,
    )
    if token_resp.status_code != 200:
        raise Exception(f"Gmail OAuth token refresh failed: {token_resp.text}")
    access_token = token_resp.json().get("access_token")
    if not access_token:
        raise Exception("Gmail OAuth returned no access_token")

    # 2. Build MIME message
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"{from_name} <{from_email}>"
    msg["To"]      = to_email
    msg.attach(MIMEText(body, "plain"))
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()

    # 3. POST to Gmail API
    send_resp = requests.post(
        "https://gmail.googleapis.com/gmail/v1/users/me/messages/send",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type":  "application/json",
        },
        json={"raw": raw},
        timeout=30,
    )
    if send_resp.status_code not in (200, 201):
        raise Exception(f"Gmail API send failed ({send_resp.status_code}): {send_resp.text}")


def _send_via_resend(to_email: str, subject: str, body: str,
                     from_email: str, from_name: str, api_key: str):
    """Send via Resend HTTPS API."""
    resp = requests.post(
        "https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"from": f"{from_name} <{from_email}>", "to": [to_email],
              "subject": subject, "text": body},
        timeout=30,
    )
    if resp.status_code not in (200, 201):
        raise Exception(f"Resend error {resp.status_code}: {resp.text}")


def _send_via_smtp(to_email: str, subject: str, body: str,
                   from_email: str, from_name: str, password: str):
    """Gmail SMTP fallback — may be blocked on Railway."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"{from_name} <{from_email}>"
    msg["To"]      = to_email
    msg.attach(MIMEText(body, "plain"))

    last_err = None
    for port, use_ssl in [(587, False), (465, True)]:
        try:
            if use_ssl:
                with smtplib.SMTP_SSL("smtp.gmail.com", port, timeout=30) as s:
                    s.login(from_email, password)
                    s.sendmail(from_email, to_email, msg.as_string())
            else:
                with smtplib.SMTP("smtp.gmail.com", port, timeout=30) as s:
                    s.ehlo(); s.starttls(); s.ehlo()
                    s.login(from_email, password)
                    s.sendmail(from_email, to_email, msg.as_string())
            return   # success
        except Exception as e:
            last_err = e
    raise last_err


# ── Public API ────────────────────────────────────────────────────────────────

def send_email(lead_id: int, subject: str, body: str, db, email_type: str = "initial"):
    from models import AppSettings, EmailLog, Lead

    settings = db.query(AppSettings).first()
    if not settings:
        raise Exception("No settings configured")

    lead = db.query(Lead).get(lead_id)
    if not lead:
        raise Exception(f"Lead {lead_id} not found")
    if not lead.email:
        raise Exception(f"Lead {lead.name} has no email address")

    # Daily limit guard
    today_count = db.query(EmailLog).filter(
        EmailLog.status == "sent",
        func.date(EmailLog.sent_at) == date.today()
    ).count()
    if today_count >= (settings.daily_send_limit or 20):
        raise Exception(f"Daily send limit of {settings.daily_send_limit} reached")

    from_email = settings.gmail_email or ""
    from_name  = settings.sender_name or "Rishi"

    # ── Priority 1: Gmail API (OAuth2) — HTTPS, works on Railway ─────────────
    client_id     = getattr(settings, "gmail_client_id",     None) or ""
    client_secret = getattr(settings, "gmail_client_secret", None) or ""
    refresh_token = getattr(settings, "gmail_refresh_token", None) or ""

    if client_id and client_secret and refresh_token:
        _do_send = lambda: _send_via_gmail_api(
            lead.email, subject, body, from_email, from_name,
            client_id, client_secret, refresh_token
        )
        method = "gmail_api"

    # ── Priority 2: Resend API — HTTPS ────────────────────────────────────────
    elif (getattr(settings, "resend_api_key", None) or ""):
        resend_key = settings.resend_api_key
        _do_send = lambda: _send_via_resend(
            lead.email, subject, body, from_email, from_name, resend_key
        )
        method = "resend"

    # ── Priority 3: SMTP — fallback (Railway often blocks) ───────────────────
    elif settings.gmail_app_password:
        _do_send = lambda: _send_via_smtp(
            lead.email, subject, body, from_email, from_name, settings.gmail_app_password
        )
        method = "smtp"

    else:
        raise Exception(
            "No send method configured. "
            "Add Gmail OAuth credentials (recommended) in Settings → Gmail API."
        )

    try:
        _do_send()
    except Exception as err:
        db.add(EmailLog(
            lead_id=lead_id, email_type=email_type,
            sent_at=datetime.utcnow(), subject=subject, body=body,
            status="failed", error_msg=f"[{method}] {err}",
        ))
        db.commit()
        raise

    db.add(EmailLog(
        lead_id=lead_id, email_type=email_type,
        sent_at=datetime.utcnow(), subject=subject, body=body,
        status="sent",
    ))
    db.commit()

    # ── Mirror status to Railway so both DBs stay in sync ─────────────────────
    _mirror_status_to_railway(lead.email, "Contacted")
