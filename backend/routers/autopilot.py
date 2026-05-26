"""
Autopilot API routes.

GET  /api/autopilot/status          — current status, today's count, next run
GET  /api/autopilot/queue           — today's prioritised queue with scores
POST /api/autopilot/toggle          — enable / disable autopilot
POST /api/autopilot/run-now         — trigger an immediate send cycle
POST /api/autopilot/quick-add       — add / update an email on a lead & mark priority
"""

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime
from pydantic import BaseModel
from typing import Optional

from database import get_db
from models import Lead, AppSettings, EmailLog

router = APIRouter()


# ---------- schemas ----------

class QuickAddRequest(BaseModel):
    email: str
    lead_id: Optional[int] = None   # if known
    name: Optional[str] = None      # if creating new lead

class ToggleRequest(BaseModel):
    enabled: bool


# ---------- helpers ----------

def _today_sent(db) -> int:
    return db.query(EmailLog).filter(
        EmailLog.status == "sent",
        func.date(EmailLog.sent_at) == date.today()
    ).count()


# ---------- routes ----------

@router.get("/status")
def get_status(db: Session = Depends(get_db)):
    settings = db.query(AppSettings).first()
    if not settings:
        return {"data": {"autopilot_enabled": False}, "message": "ok"}

    from services.prioritizer import get_daily_queue
    daily_limit = settings.daily_send_limit or 20

    # Get actual total eligible count (not capped)
    total_eligible = db.query(Lead).filter(
        Lead.email != None,
        Lead.email != "",
        Lead.status.in_(["New", "Email Found"]),
    ).count()

    queue = get_daily_queue(db, limit=daily_limit)

    sent_today = _today_sent(db)
    remaining  = max(0, daily_limit - sent_today)

    return {
        "data": {
            "autopilot_enabled": bool(getattr(settings, "autopilot_enabled", False)),
            "daily_limit":       daily_limit,
            "sent_today":        sent_today,
            "remaining_today":   remaining,
            "eligible_leads":    total_eligible,   # real count, not capped
            "today_queue_size":  len(queue),        # today's actual send queue
        },
        "message": "ok",
    }


@router.get("/queue")
def get_queue(db: Session = Depends(get_db)):
    from services.prioritizer import get_daily_queue
    settings = db.query(AppSettings).first()
    limit = (settings.daily_send_limit if settings else 20) or 20

    queue = get_daily_queue(db, limit=limit)

    results = []
    for lead, score, asmi_users, viable in queue:
        results.append({
            "lead_id":              lead.id,
            "name":                 lead.name,
            "newsletter":           lead.newsletter_name,
            "email":                lead.email,
            "audience":             lead.estimated_audience,
            "category":             lead.category,
            "timezone":             getattr(lead, "lead_timezone", "America/New_York") or "America/New_York",
            "priority":             bool(getattr(lead, "priority", False)),
            "score":                score,
            "status":               lead.status,
            "estimated_asmi_users": asmi_users,
            "viable":               viable,
        })

    return {"data": results, "message": "ok"}


@router.post("/toggle")
def toggle_autopilot(req: ToggleRequest, db: Session = Depends(get_db)):
    settings = db.query(AppSettings).first()
    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")

    settings.autopilot_enabled = req.enabled
    db.commit()

    return {
        "data": {"autopilot_enabled": req.enabled},
        "message": f"Autopilot {'enabled' if req.enabled else 'disabled'}",
    }


@router.post("/run-now")
def run_now(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Trigger one immediate autopilot cycle in the background (non-blocking)."""
    settings = db.query(AppSettings).first()
    if not settings:
        raise HTTPException(status_code=500, detail="Settings missing")

    def _run():
        from services.auto_pilot import run_autopilot_cycle
        run_autopilot_cycle(force=True)   # bypass autopilot_enabled gate

    background_tasks.add_task(_run)
    return {"data": {}, "message": "Autopilot cycle triggered — sending in background"}


@router.post("/quick-add")
def quick_add_email(req: QuickAddRequest, db: Session = Depends(get_db)):
    """
    Assign an email address to a lead (by ID or auto-match by domain)
    and mark them as Priority so they jump to the top of tomorrow's queue.
    """
    lead = None

    if req.lead_id:
        lead = db.query(Lead).get(req.lead_id)

    if not lead and req.email:
        # Try to match by domain
        domain = req.email.split("@")[-1].lower() if "@" in req.email else ""
        if domain:
            all_leads = db.query(Lead).filter(
                Lead.status.in_(["New", "Email Found"])
            ).all()
            for candidate in all_leads:
                url = (candidate.url or "").lower().replace("www.", "")
                if domain in url or url in domain:
                    lead = candidate
                    break

    if not lead:
        # Create a minimal new lead
        if not req.name and not req.email:
            raise HTTPException(status_code=400, detail="Provide lead_id or email (and optionally name)")
        lead = Lead(
            name    = req.name or req.email.split("@")[0],
            email   = req.email,
            status  = "Email Found",
            priority= True,
            lead_timezone = "America/New_York",
        )
        db.add(lead)
        db.commit()
        db.refresh(lead)
        return {
            "data": {"lead_id": lead.id, "name": lead.name, "action": "created"},
            "message": f"New lead created and marked priority: {lead.name}",
        }

    # Update existing lead
    if req.email:
        lead.email = req.email
        if lead.status == "New":
            lead.status = "Email Found"
    lead.priority = True
    db.commit()

    return {
        "data": {"lead_id": lead.id, "name": lead.name, "action": "updated"},
        "message": f"{lead.name} updated with email and marked Priority",
    }


@router.delete("/priority/{lead_id}")
def remove_priority(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(Lead).get(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    lead.priority = False
    db.commit()
    return {"data": None, "message": f"{lead.name} priority cleared"}
