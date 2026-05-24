import asyncio
from datetime import datetime


async def start_scheduler():
    while True:
        await asyncio.sleep(900)  # 15 minutes
        try:
            process_scheduled()
        except Exception as e:
            print(f"Scheduler error: {e}")


def process_scheduled():
    from database import SessionLocal
    from models import ScheduledEmail, Lead, Template, AppSettings
    from services.email_sender import send_email, render_template

    db = SessionLocal()
    try:
        settings = db.query(AppSettings).first()
        if not settings:
            return

        # Check sending hours in local timezone
        import pytz
        tz = pytz.timezone(settings.timezone if settings.timezone else "Asia/Kolkata")
        local_now = datetime.now(tz)
        if not (settings.send_hours_start <= local_now.hour < settings.send_hours_end):
            return

        now = datetime.utcnow()
        due = db.query(ScheduledEmail).filter(
            ScheduledEmail.status == "pending",
            ScheduledEmail.scheduled_for <= now
        ).all()

        for scheduled in due:
            lead = db.query(Lead).get(scheduled.lead_id)
            if not lead or lead.status in ("Replied", "Not Interested"):
                scheduled.status = "cancelled"
                db.commit()
                continue

            if not lead.email:
                scheduled.status = "cancelled"
                db.commit()
                continue

            template = db.query(Template).get(scheduled.template_id)
            if not template:
                scheduled.status = "cancelled"
                db.commit()
                continue

            if scheduled.email_type == "followup1":
                body = template.followup1_body or ""
                subject = template.followup1_subject or ""
            else:
                body = template.followup2_body or ""
                subject = template.followup2_subject or ""

            rendered_subject = render_template(subject, lead)
            rendered_body = render_template(body, lead)

            try:
                send_email(lead.id, rendered_subject, rendered_body, db, email_type=scheduled.email_type)
                scheduled.status = "sent"
                db.commit()
                print(f"Sent scheduled {scheduled.email_type} to {lead.name}")
            except Exception as e:
                print(f"Failed to send scheduled email to {lead.name}: {e}")
                scheduled.status = "sent"  # Mark as attempted to avoid infinite retry
                db.commit()
    except Exception as e:
        print(f"process_scheduled error: {e}")
    finally:
        db.close()
