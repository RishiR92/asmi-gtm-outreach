"""
Autopilot engine.

Runs every 30 minutes via the background task.
When autopilot is enabled it:
  1. Calls the prioritizer to get today's ranked queue
  2. Checks how many emails have already been sent today
  3. Sends remaining slots using the frozen template
  4. Respects daily_send_limit from AppSettings
  5. Records everything in EmailLog and updates lead status
"""

import asyncio
from datetime import datetime, timedelta, date

from sqlalchemy import func

# ── Send-start gate ───────────────────────────────────────────────────────────
# Autopilot will not send any emails before this date.
# Set to the Monday the campaign launches; remove/backdate once ongoing.
SEND_START_DATE = date(2026, 5, 25)   # Monday 25 May 2026


async def start_autopilot():
    # Wait 30 minutes before first cycle — deploys must NOT trigger sends
    while True:
        await asyncio.sleep(1800)
        try:
            await asyncio.to_thread(run_autopilot_cycle)
        except Exception as e:
            print(f"[autopilot] cycle error: {e}")


def run_autopilot_cycle():
    from database import SessionLocal
    from models import AppSettings, EmailLog, Template, ScheduledEmail
    from services.prioritizer import get_tz_optimised_batch
    from services.email_sender import send_email, render_template

    db = SessionLocal()
    try:
        settings = db.query(AppSettings).first()
        if not settings:
            return
        if not getattr(settings, "autopilot_enabled", False):
            return
        if date.today() < SEND_START_DATE:
            print(f"[autopilot] Campaign starts {SEND_START_DATE} — today is {date.today()}, skipping")
            return
        if not settings.gmail_email or not settings.gmail_app_password:
            print("[autopilot] Gmail credentials missing — skipping")
            return

        # How many sent today already?
        today_sent = db.query(EmailLog).filter(
            EmailLog.status == "sent",
            func.date(EmailLog.sent_at) == date.today()
        ).count()

        remaining = (settings.daily_send_limit or 20) - today_sent
        if remaining <= 0:
            print(f"[autopilot] Daily limit reached ({settings.daily_send_limit}), skipping")
            return

        # Get the single frozen template
        template = db.query(Template).first()
        if not template:
            print("[autopilot] No template found — skipping")
            return

        queue = get_tz_optimised_batch(db, limit=remaining)
        if not queue:
            print("[autopilot] No eligible leads in queue")
            return

        sent_count = 0
        for lead, score, asmi_users, viable in queue:
            if sent_count >= remaining:
                break
            try:
                subject = render_template(template.subject_a or "", lead)
                body    = render_template(template.body or "", lead)

                send_email(lead.id, subject, body, db, email_type="initial")

                # Update lead state
                lead.status       = "Contacted"
                lead.date_contacted = datetime.utcnow()
                lead.template_id  = template.id
                lead.ab_variant   = "A"

                # Cancel any stale pending follow-ups
                db.query(ScheduledEmail).filter(
                    ScheduledEmail.lead_id == lead.id,
                    ScheduledEmail.status  == "pending"
                ).update({"status": "cancelled"})

                # Schedule follow-ups
                fu1_days = settings.followup1_days or 4
                fu2_days = settings.followup2_days or 9
                now = datetime.utcnow()

                db.add(ScheduledEmail(
                    lead_id      = lead.id,
                    email_type   = "followup1",
                    scheduled_for= now + timedelta(days=fu1_days),
                    status       = "pending",
                    template_id  = template.id,
                    ab_variant   = "A",
                ))
                db.add(ScheduledEmail(
                    lead_id      = lead.id,
                    email_type   = "followup2",
                    scheduled_for= now + timedelta(days=fu2_days),
                    status       = "pending",
                    template_id  = template.id,
                    ab_variant   = "A",
                ))
                lead.follow_up_due = now + timedelta(days=fu1_days)
                db.commit()

                sent_count += 1
                print(f"[autopilot] ✓ Sent to {lead.name} ({lead.email}) score={score}")

            except Exception as e:
                print(f"[autopilot] ✗ Failed {lead.name}: {e}")
                db.rollback()

        print(f"[autopilot] Cycle complete — sent {sent_count} emails")

    except Exception as e:
        print(f"[autopilot] Fatal error: {e}")
        db.rollback()
    finally:
        db.close()
