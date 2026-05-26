import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy import func
from datetime import date, datetime


def _first_name(full_name: str) -> str:
    """Extract first name from a full name — handles 'First Last', 'Last, First', etc."""
    if not full_name:
        return ""
    name = full_name.strip()
    # Handle "Last, First" format
    if "," in name:
        name = name.split(",", 1)[1].strip()
    # Take the first word
    first = name.split()[0] if name.split() else name
    return first.capitalize()


def render_template(body: str, lead, custom_line: str = "") -> str:
    if not body:
        return ""
    fname = _first_name(lead.name or "")
    # {{name}} now renders first name only (natural, human-friendly)
    result = body.replace("{{name}}", fname)
    result = result.replace("{{first_name}}", fname)          # explicit alias
    result = result.replace("{{full_name}}", lead.name or "")  # opt-in for full name
    result = result.replace("{{newsletter}}", lead.newsletter_name or "")
    result = result.replace("{{audience}}", str(lead.estimated_audience) if lead.estimated_audience else "")
    result = result.replace("{{custom_line}}", custom_line or "")
    return result


def _send_via_resend(to_email: str, subject: str, body: str,
                     from_email: str, from_name: str, api_key: str):
    """Send via Resend HTTPS API — works on Railway (no SMTP ports needed)."""
    resp = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "from": f"{from_name} <{from_email}>",
            "to": [to_email],
            "subject": subject,
            "text": body,
        },
        timeout=30,
    )
    if resp.status_code not in (200, 201):
        raise Exception(f"Resend API error {resp.status_code}: {resp.text}")


def _send_via_smtp(to_email: str, subject: str, body: str,
                   from_email: str, from_name: str, password: str):
    """Send via Gmail SMTP — fallback if Resend not configured."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{from_name} <{from_email}>"
    msg["To"] = to_email
    msg.attach(MIMEText(body, "plain"))

    last_err = None
    for port, use_ssl in [(587, False), (465, True)]:
        try:
            if use_ssl:
                with smtplib.SMTP_SSL("smtp.gmail.com", port, timeout=30) as server:
                    server.login(from_email, password)
                    server.sendmail(from_email, to_email, msg.as_string())
            else:
                with smtplib.SMTP("smtp.gmail.com", port, timeout=30) as server:
                    server.ehlo()
                    server.starttls()
                    server.ehlo()
                    server.login(from_email, password)
                    server.sendmail(from_email, to_email, msg.as_string())
            last_err = None
            break
        except Exception as e:
            last_err = e
            continue

    if last_err:
        raise last_err


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

    # Check daily limit
    today_count = db.query(EmailLog).filter(
        EmailLog.status == "sent",
        func.date(EmailLog.sent_at) == date.today()
    ).count()
    if today_count >= settings.daily_send_limit:
        raise Exception(f"Daily send limit of {settings.daily_send_limit} reached")

    from_email  = settings.gmail_email or ""
    from_name   = settings.sender_name or "Rishi"
    resend_key  = getattr(settings, "resend_api_key", None) or ""

    try:
        if resend_key:
            # ── Preferred: Resend HTTPS (works on Railway, no SMTP port needed) ──
            _send_via_resend(lead.email, subject, body, from_email, from_name, resend_key)
        else:
            # ── Fallback: Gmail SMTP ──
            if not settings.gmail_app_password:
                raise Exception("No Resend API key and no Gmail app password — configure one in Settings.")
            _send_via_smtp(lead.email, subject, body, from_email, from_name, settings.gmail_app_password)
    except Exception as last_err:
        log = EmailLog(
            lead_id=lead_id, email_type=email_type,
            sent_at=datetime.utcnow(), subject=subject, body=body,
            status="failed", error_msg=str(last_err),
        )
        db.add(log)
        db.commit()
        raise last_err

    # Log success
    log = EmailLog(
        lead_id=lead_id, email_type=email_type,
        sent_at=datetime.utcnow(), subject=subject, body=body,
        status="sent",
    )
    db.add(log)
    db.commit()
