import smtplib
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

    if not settings.gmail_email or not settings.gmail_app_password:
        raise Exception("Gmail credentials not configured. Please update Settings.")

    # Check daily limit
    today_count = db.query(EmailLog).filter(
        EmailLog.status == "sent",
        func.date(EmailLog.sent_at) == date.today()
    ).count()
    if today_count >= settings.daily_send_limit:
        raise Exception(f"Daily send limit of {settings.daily_send_limit} reached")

    # Build email
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{settings.sender_name} <{settings.gmail_email}>"
    msg["To"] = lead.email
    msg.attach(MIMEText(body, "plain"))

    # Send via SMTP
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(settings.gmail_email, settings.gmail_app_password)
            server.sendmail(settings.gmail_email, lead.email, msg.as_string())
    except smtplib.SMTPAuthenticationError:
        log = EmailLog(
            lead_id=lead_id,
            email_type=email_type,
            sent_at=datetime.utcnow(),
            subject=subject,
            body=body,
            status="failed",
            error_msg="SMTP authentication failed. Check your Gmail app password.",
        )
        db.add(log)
        db.commit()
        raise Exception("SMTP authentication failed. Check your Gmail app password.")
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
