from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional

from database import get_db
from models import Lead, Template, ScheduledEmail, EmailLog, AppSettings
from schemas import (
    SendEmailRequest, SendFollowupRequest, GuessPatternRequest,
    EmailLogResponse, ScheduledEmailResponse,
)
from services.email_sender import send_email, render_template

router = APIRouter()


def guess_emails(first_name: str, last_name: str, domain: str):
    first = first_name.lower().strip()
    last = last_name.lower().strip() if last_name else ""
    patterns = [
        f"{first}@{domain}",
        f"{first}.{last}@{domain}" if last else None,
        f"{first[0]}{last}@{domain}" if last else None,
        f"{first[0]}.{last}@{domain}" if last else None,
        f"hi@{domain}",
        f"hello@{domain}",
        f"contact@{domain}",
        f"info@{domain}",
        f"newsletter@{domain}",
    ]
    return [p for p in patterns if p]


@router.post("/send", response_model=dict)
def send_initial_email(req: SendEmailRequest, db: Session = Depends(get_db)):
    lead = db.query(Lead).get(req.lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    if not lead.email:
        raise HTTPException(status_code=400, detail="Lead has no email address")

    template = db.query(Template).get(req.template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Pick subject based on A/B variant
    subject_raw = template.subject_a if req.ab_variant == "A" else template.subject_b
    subject = render_template(subject_raw or "", lead)
    body = render_template(template.body or "", lead, req.custom_line or "")

    try:
        send_email(lead.id, subject, body, db, email_type="initial")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Update lead
    lead.status = "Contacted"
    lead.date_contacted = datetime.utcnow()
    lead.template_id = req.template_id
    lead.ab_variant = req.ab_variant

    # Cancel any existing pending scheduled emails for this lead
    db.query(ScheduledEmail).filter(
        ScheduledEmail.lead_id == lead.id,
        ScheduledEmail.status == "pending"
    ).update({"status": "cancelled"})

    # Schedule follow-ups
    settings = db.query(AppSettings).first()
    followup1_days = settings.followup1_days if settings else 4
    followup2_days = settings.followup2_days if settings else 9

    now = datetime.utcnow()
    followup1 = ScheduledEmail(
        lead_id=lead.id,
        email_type="followup1",
        scheduled_for=now + timedelta(days=followup1_days),
        status="pending",
        template_id=req.template_id,
        ab_variant=req.ab_variant,
    )
    followup2 = ScheduledEmail(
        lead_id=lead.id,
        email_type="followup2",
        scheduled_for=now + timedelta(days=followup2_days),
        status="pending",
        template_id=req.template_id,
        ab_variant=req.ab_variant,
    )
    lead.follow_up_due = now + timedelta(days=followup1_days)

    db.add(followup1)
    db.add(followup2)
    db.commit()

    return {"data": {"lead_id": lead.id, "status": "sent"}, "message": f"Email sent to {lead.email}. Follow-ups scheduled."}


@router.post("/send-followup", response_model=dict)
def send_followup_now(req: SendFollowupRequest, db: Session = Depends(get_db)):
    scheduled = db.query(ScheduledEmail).get(req.scheduled_email_id)
    if not scheduled:
        raise HTTPException(status_code=404, detail="Scheduled email not found")
    if scheduled.status != "pending":
        raise HTTPException(status_code=400, detail=f"Scheduled email is already {scheduled.status}")

    lead = db.query(Lead).get(scheduled.lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    template = db.query(Template).get(scheduled.template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    if scheduled.email_type == "followup1":
        body_raw = template.followup1_body or ""
        subject_raw = template.followup1_subject or ""
    else:
        body_raw = template.followup2_body or ""
        subject_raw = template.followup2_subject or ""

    subject = render_template(subject_raw, lead)
    body = render_template(body_raw, lead)

    try:
        send_email(lead.id, subject, body, db, email_type=scheduled.email_type)
        scheduled.status = "sent"
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"data": {"scheduled_email_id": scheduled.id}, "message": f"Follow-up sent to {lead.email}"}


@router.get("/queue", response_model=dict)
def get_queue(db: Session = Depends(get_db)):
    scheduled = (
        db.query(ScheduledEmail)
        .filter(ScheduledEmail.status == "pending")
        .order_by(ScheduledEmail.scheduled_for)
        .all()
    )

    results = []
    for s in scheduled:
        lead = db.query(Lead).get(s.lead_id)
        results.append({
            "id": s.id,
            "lead_id": s.lead_id,
            "email_type": s.email_type,
            "scheduled_for": s.scheduled_for.isoformat() if s.scheduled_for else None,
            "status": s.status,
            "template_id": s.template_id,
            "ab_variant": s.ab_variant,
            "lead_name": lead.name if lead else None,
            "lead_email": lead.email if lead else None,
        })

    return {"data": results, "message": "ok"}


@router.get("/logs", response_model=dict)
def get_logs(limit: int = 50, db: Session = Depends(get_db)):
    logs = (
        db.query(EmailLog)
        .order_by(EmailLog.sent_at.desc())
        .limit(limit)
        .all()
    )

    results = []
    for log in logs:
        lead = db.query(Lead).get(log.lead_id)
        results.append({
            "id": log.id,
            "lead_id": log.lead_id,
            "email_type": log.email_type,
            "sent_at": log.sent_at.isoformat() if log.sent_at else None,
            "subject": log.subject,
            "body": log.body,
            "status": log.status,
            "error_msg": log.error_msg,
            "lead_name": lead.name if lead else None,
        })

    return {"data": results, "message": "ok"}


@router.delete("/scheduled/{scheduled_id}", response_model=dict)
def cancel_scheduled(scheduled_id: int, db: Session = Depends(get_db)):
    scheduled = db.query(ScheduledEmail).get(scheduled_id)
    if not scheduled:
        raise HTTPException(status_code=404, detail="Scheduled email not found")
    if scheduled.status != "pending":
        raise HTTPException(status_code=400, detail=f"Cannot cancel — status is {scheduled.status}")
    scheduled.status = "cancelled"
    db.commit()
    return {"data": None, "message": "Scheduled email cancelled"}


@router.post("/guess-pattern", response_model=dict)
def guess_email_pattern(req: GuessPatternRequest):
    patterns = guess_emails(req.first_name, req.last_name or "", req.domain)
    return {"data": patterns, "message": "ok"}
