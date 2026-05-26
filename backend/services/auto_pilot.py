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
import pytz
from datetime import datetime, timedelta, date

from sqlalchemy import func

# ── Send-start gate ───────────────────────────────────────────────────────────
SEND_START_DATE = date(2026, 5, 26)   # Start fresh from Tuesday (today already sent 2x)

# ── Historical sync ───────────────────────────────────────────────────────────
# May 25 emails were sent from ephemeral SQLite containers (now gone).
# On the first Railway deploy after migrating to PostgreSQL, this runs once
# to mark those leads as Contacted so they are never re-emailed.
_HISTORICAL_SYNC_CUTOFF = date(2026, 5, 27)   # run through May 26 (deploy landed on 26th)


def sync_historical_sends_once(db):
    """
    One-time recovery: mark May 25 already-sent leads as Contacted.

    Fires on May 25 or May 26 (deploy landed on 26th) and only when
    0 leads are Contacted — meaning PostgreSQL is fresh and SQLite logs
    are gone. Uses the same prioritizer order the autopilot would have
    used. Safe no-op from May 27 onward or once any lead is Contacted.
    """
    from models import Lead, AppSettings
    from services.prioritizer import get_tz_optimised_batch

    if date.today() >= _HISTORICAL_SYNC_CUTOFF:
        return  # only relevant on May 25–26

    contacted_count = db.query(Lead).filter(Lead.status == "Contacted").count()
    if contacted_count > 0:
        print(f"[startup] Historical sync skipped — {contacted_count} leads already Contacted")
        return

    settings = db.query(AppSettings).first()
    daily_limit = (settings.daily_send_limit if settings else 20) or 20

    queue = get_tz_optimised_batch(db, limit=daily_limit)
    if not queue:
        print("[startup] Historical sync: no eligible leads found")
        return

    marked = 0
    for lead, score, asmi_users, viable in queue:
        lead.status = "Contacted"
        lead.date_contacted = datetime.utcnow()
        marked += 1

    db.commit()
    print(f"[startup] ✓ Historical sync: marked {marked} leads as Contacted (recovered from SQLite wipe)")


# ── Send window ───────────────────────────────────────────────────────────────
# Reads timezone / hours from AppSettings so the Settings UI is the source of truth.
# Falls back to PT 9am–6pm if settings are missing.
_FALLBACK_TZ         = "America/Los_Angeles"
_FALLBACK_HOUR_START = 9
_FALLBACK_HOUR_END   = 18


def _within_send_window(settings=None) -> bool:
    """Returns True if current time is within the allowed send window per settings."""
    tz_name    = (settings.timezone if settings and settings.timezone else _FALLBACK_TZ)
    hour_start = (settings.send_hours_start if settings and settings.send_hours_start is not None else _FALLBACK_HOUR_START)
    hour_end   = (settings.send_hours_end   if settings and settings.send_hours_end   is not None else _FALLBACK_HOUR_END)
    try:
        tz = pytz.timezone(tz_name)
    except Exception:
        tz = pytz.timezone(_FALLBACK_TZ)
    now_local = datetime.now(tz)
    return hour_start <= now_local.hour < hour_end


async def start_autopilot():
    # Wait 5 minutes after startup (lets Railway health-check pass; avoids deploy-time sends)
    await asyncio.sleep(300)
    while True:
        try:
            await asyncio.to_thread(run_autopilot_cycle)
        except Exception as e:
            print(f"[autopilot] cycle error: {e}")
        # Check every 15 minutes — sends only once per day (remaining=0 guard handles the rest)
        await asyncio.sleep(900)


def run_autopilot_cycle(force: bool = False):
    """
    Run one send cycle.
    force=True: skip the autopilot_enabled gate (used by manual Run Now).
    """
    from database import SessionLocal
    from models import AppSettings, EmailLog, Template, ScheduledEmail
    from services.prioritizer import get_tz_optimised_batch
    from services.email_sender import send_email, render_template

    db = SessionLocal()
    try:
        settings = db.query(AppSettings).first()
        if not settings:
            print("[autopilot] No settings found — skipping")
            return
        if not force and not getattr(settings, "autopilot_enabled", False):
            print("[autopilot] Autopilot disabled — skipping (use Run Now to force)")
            return
        if not force and not _within_send_window(settings):
            tz_name = settings.timezone or _FALLBACK_TZ
            h_start = settings.send_hours_start or _FALLBACK_HOUR_START
            h_end   = settings.send_hours_end   or _FALLBACK_HOUR_END
            print(f"[autopilot] Outside send window ({h_start}–{h_end} {tz_name}) — skipping")
            return

        # Check at least one send method is configured
        has_gmail_api = (getattr(settings, "gmail_client_id", None) and
                         getattr(settings, "gmail_client_secret", None) and
                         getattr(settings, "gmail_refresh_token", None))
        has_resend    = bool(getattr(settings, "resend_api_key", None) or "")
        has_smtp      = bool(settings.gmail_app_password)
        if not has_gmail_api and not has_resend and not has_smtp:
            print("[autopilot] No send method configured — add Gmail OAuth credentials in Settings")
            return

        # How many sent today already?
        today_sent = db.query(EmailLog).filter(
            EmailLog.status == "sent",
            func.date(EmailLog.sent_at) == date.today()
        ).count()

        daily_limit = settings.daily_send_limit or 20

        # Daily limit reached — done for the day (partial sends are OK, we send the remaining slots)
        if today_sent >= daily_limit and not force:
            print(f"[autopilot] Daily limit reached ({today_sent}/{daily_limit}) — done for today")
            return

        remaining = daily_limit - today_sent
        if remaining <= 0:
            print(f"[autopilot] Daily limit reached ({daily_limit}), skipping")
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
