import base64
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy import func
from datetime import date, datetime


def render_template(body: str, lead, custom_line: str = "") -> str:
    if not body:
        return ""
    result = body.replace("{{name}}", lead.name or "")
    result = result.replace("{{newsletter}}", lead.newsletter_name or "")
    result = result.replace("{{audience}}", str(lead.estimated_audience) if lead.estimated_audience else "")
    result = result.replace("{{custom_line}}", custom_line or "")
    return result


def _send_via_gmail_api(from_email: str, to_email: str, subject: str, body: str, sender_name: str = ""):
    """Send via Gmail API over HTTPS — works on Railway (no SMTP ports needed)."""
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    client_id     = os.environ.get("GMAIL_CLIENT_ID", "")
    client_secret = os.environ.get("GMAIL_CLIENT_SECRET", "")
    refresh_token = os.environ.get("GMAIL_REFRESH_TOKEN", "")

    if not all([client_id, client_secret, refresh_token]):
        raise Exception("Gmail API credentials missing — set GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET, GMAIL_REFRESH_TOKEN in Railway environment variables.")

    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        client_id=client_id,
        client_secret=client_secret,
        token_uri="https://oauth2.googleapis.com/token",
    )

    service = build("gmail", "v1", credentials=creds, cache_discovery=False)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"{sender_name} <{from_email}>" if sender_name else from_email
    msg["To"]      = to_email
    msg.attach(MIMEText(body, "plain"))

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    service.users().messages().send(userId="me", body={"raw": raw}).execute()


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

    if not settings.gmail_email:
        raise Exception("Gmail address not configured. Please update Settings.")

    # Check daily limit
    today_count = db.query(EmailLog).filter(
        EmailLog.status == "sent",
        func.date(EmailLog.sent_at) == date.today()
    ).count()
    if today_count >= settings.daily_send_limit:
        raise Exception(f"Daily send limit of {settings.daily_send_limit} reached")

    # Send via Gmail API (HTTPS — works on any host)
    try:
        _send_via_gmail_api(
            from_email=settings.gmail_email,
            to_email=lead.email,
            subject=subject,
            body=body,
            sender_name=settings.sender_name or "",
        )
    except Exception as e:
        log = EmailLog(
            lead_id=lead_id,
            email_type=email_type,
            sent_at=datetime.utcnow(),
            subject=subject,
            body=body,
            status="failed",
            error_msg=str(e),
        )
        db.add(log)
        db.commit()
        raise

    # Log success
    log = EmailLog(
        lead_id=lead_id,
        email_type=email_type,
        sent_at=datetime.utcnow(),
        subject=subject,
        body=body,
        status="sent",
    )
    db.add(log)
    db.commit()
