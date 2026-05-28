from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, date

from database import get_db
from models import Lead, EmailLog, ScheduledEmail, AppSettings

router = APIRouter()


@router.get("/stats", response_model=dict)
def get_stats(db: Session = Depends(get_db)):
    total_leads = db.query(Lead).count()

    # By status
    status_rows = db.query(Lead.status, func.count(Lead.id)).group_by(Lead.status).all()
    by_status = {row[0]: row[1] for row in status_rows if row[0]}

    # Emails sent this week
    week_start = datetime.utcnow() - timedelta(days=7)
    emails_sent_this_week = db.query(EmailLog).filter(
        EmailLog.status == "sent",
        EmailLog.sent_at >= week_start
    ).count()

    # Reply rate
    total_contacted = db.query(Lead).filter(
        Lead.status.in_(["Contacted", "Replied", "Feature Confirmed", "Not Interested", "No Response"])
    ).count()
    total_replied = db.query(Lead).filter(
        Lead.status.in_(["Replied", "Feature Confirmed"])
    ).count()
    reply_rate = round(total_replied / total_contacted, 4) if total_contacted > 0 else 0.0

    # Follow-ups due today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    followups_due = db.query(ScheduledEmail).filter(
        ScheduledEmail.status == "pending",
        ScheduledEmail.scheduled_for >= today_start,
        ScheduledEmail.scheduled_for < today_end,
    ).all()

    followups_list = []
    for s in followups_due:
        lead = db.query(Lead).get(s.lead_id)
        if lead:
            followups_list.append({
                "scheduled_id": s.id,
                "lead_id": lead.id,
                "lead_name": lead.name,
                "lead_email": lead.email,
                "newsletter_name": lead.newsletter_name,
                "email_type": s.email_type,
                "scheduled_for": s.scheduled_for.isoformat() if s.scheduled_for else None,
            })

    # Recent activity (last 10 email logs)
    recent_logs = (
        db.query(EmailLog)
        .order_by(EmailLog.sent_at.desc())
        .limit(10)
        .all()
    )

    recent_activity = []
    for log in recent_logs:
        lead = db.query(Lead).get(log.lead_id)
        recent_activity.append({
            "id": log.id,
            "lead_id": log.lead_id,
            "lead_name": lead.name if lead else "Unknown",
            "email_type": log.email_type,
            "sent_at": log.sent_at.isoformat() if log.sent_at else None,
            "subject": log.subject,
            "status": log.status,
        })

    return {
        "data": {
            "total_leads": total_leads,
            "by_status": by_status,
            "emails_sent_this_week": emails_sent_this_week,
            "reply_rate": reply_rate,
            "followups_due_today": followups_list,
            "recent_activity": recent_activity,
        },
        "message": "ok",
    }


@router.get("/schedule", response_model=dict)
def get_schedule(db: Session = Depends(get_db)):
    """
    Returns a 3-day advance send plan starting from the next Monday.
    Each day's batch is the next slice of the priority queue (viable leads first).
    The autopilot re-ranks at actual send time, so this is a live preview.
    """
    from services.prioritizer import get_daily_queue

    settings = db.query(AppSettings).first()
    daily_limit = (settings.daily_send_limit if settings else 20) or 20

    # Schedule starts from today — always show the next 3 days from now
    today = date.today()
    start_date = today

    # Pull enough leads for 3 days — personal emails only (exclude generic/junk)
    from routers.leads import _GENERIC_PREFIXES
    from models import Lead as LeadModel
    full_queue_raw = get_daily_queue(db, limit=daily_limit * 10)  # fetch extra, then filter
    full_queue = [
        item for item in full_queue_raw
        if item[0].email and not any(item[0].email.lower().startswith(p) for p in _GENERIC_PREFIXES)
    ][:daily_limit * 3]

    def _lead_dict(lead, score, asmi_users, viable, rank):
        return {
            "rank":                 rank,
            "lead_id":              lead.id,
            "name":                 lead.name,
            "newsletter":           lead.newsletter_name,
            "email":                lead.email,
            "audience":             lead.estimated_audience,
            "category":             lead.category,
            "timezone":             getattr(lead, "lead_timezone", "America/New_York") or "America/New_York",
            "priority":             bool(getattr(lead, "priority", False)),
            "score":                score,
            "estimated_asmi_users": asmi_users,
            "viable":               viable,
            "status":               lead.status,
        }

    schedule = []
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    for i in range(3):
        day_date  = start_date + timedelta(days=i)
        slice_    = full_queue[i * daily_limit : (i + 1) * daily_limit]
        leads_out = [
            _lead_dict(lead, score, asmi_users, viable, rank=j + 1)
            for j, (lead, score, asmi_users, viable) in enumerate(slice_)
        ]
        schedule.append({
            "date":      day_date.isoformat(),
            "day_label": f"{day_names[day_date.weekday()]}, {day_date.strftime('%b %d')}",
            "is_today":  day_date == today,
            "leads":     leads_out,
        })

    return {"data": schedule, "message": "ok"}
