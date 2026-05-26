from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, List
import io
import csv
from datetime import datetime

from database import get_db
from models import Lead
from schemas import LeadCreate, LeadUpdate, LeadResponse, LeadStatusUpdate, BulkEmailStatusUpdate

router = APIRouter()


@router.get("", response_model=dict)
def list_leads(
    status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Lead)

    if status:
        query = query.filter(Lead.status == status)
    if category:
        query = query.filter(Lead.category == category)
    if search:
        query = query.filter(
            or_(
                Lead.name.ilike(f"%{search}%"),
                Lead.newsletter_name.ilike(f"%{search}%"),
                Lead.email.ilike(f"%{search}%"),
                Lead.url.ilike(f"%{search}%"),
            )
        )

    total = query.count()
    leads = query.order_by(Lead.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()

    return {
        "data": [LeadResponse.model_validate(l).model_dump() for l in leads],
        "total": total,
        "page": page,
        "per_page": per_page,
        "message": "ok",
    }


@router.post("", response_model=dict)
def create_lead(lead_in: LeadCreate, db: Session = Depends(get_db)):
    lead = Lead(**lead_in.model_dump())
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return {"data": LeadResponse.model_validate(lead).model_dump(), "message": "Lead created"}


@router.get("/export")
def export_leads(db: Session = Depends(get_db)):
    leads = db.query(Lead).order_by(Lead.created_at.desc()).all()

    fieldnames = [
        "id", "name", "newsletter_name", "url", "estimated_audience",
        "category", "contact_method", "email", "linkedin_url",
        "twitter_handle", "notes", "status", "date_contacted",
        "follow_up_due", "template_id", "ab_variant", "created_at", "updated_at",
    ]

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    for lead in leads:
        row = {}
        for f in fieldnames:
            val = getattr(lead, f, "")
            if isinstance(val, datetime):
                val = val.isoformat()
            row[f] = val if val is not None else ""
        writer.writerow(row)

    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=leads_export.csv"},
    )


@router.post("/import", response_model=dict)
async def import_leads(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        import pandas as pd
    except ImportError:
        raise HTTPException(status_code=500, detail="pandas not installed")

    content = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not parse CSV: {e}")

    # Normalize column names
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    existing_urls = {l.url for l in db.query(Lead.url).all() if l.url}
    imported = 0
    skipped = 0

    for _, row in df.iterrows():
        url = str(row.get("url", "")).strip()
        if url and url in existing_urls:
            skipped += 1
            continue

        email_val = str(row.get("email", "")).strip()
        status = "Email Found" if email_val and email_val.lower() != "nan" else "New"

        def safe(col):
            val = row.get(col, None)
            if val is None or (isinstance(val, float) and str(val) == "nan"):
                return None
            return str(val).strip() or None

        def safe_int(col):
            val = row.get(col, None)
            try:
                return int(val)
            except (TypeError, ValueError):
                return None

        lead = Lead(
            name=safe("name") or "Unknown",
            newsletter_name=safe("newsletter_name"),
            url=url or None,
            estimated_audience=safe_int("estimated_audience"),
            category=safe("category"),
            contact_method=safe("contact_method"),
            email=email_val if email_val and email_val.lower() != "nan" else None,
            linkedin_url=safe("linkedin_url"),
            twitter_handle=safe("twitter_handle"),
            notes=safe("notes"),
            status=safe("status") or status,
            ab_variant=safe("ab_variant"),
        )
        db.add(lead)
        if url:
            existing_urls.add(url)
        imported += 1

    db.commit()
    return {"data": {"imported": imported, "skipped": skipped}, "message": f"Imported {imported} leads, skipped {skipped} duplicates"}


@router.post("/bulk-status", response_model=dict)
def bulk_update_status(payload: BulkEmailStatusUpdate, db: Session = Depends(get_db)):
    """
    Given a list of email addresses, set all matching leads to the given status.
    Useful for marking leads as Contacted after a send whose logs were lost.
    Returns how many were matched and updated.
    """
    if not payload.emails:
        raise HTTPException(status_code=400, detail="No emails provided")

    # Normalise (strip whitespace, lower-case) so matching is lenient
    normalised = [e.strip().lower() for e in payload.emails if e.strip()]

    updated = 0
    not_found = []
    for email_addr in normalised:
        lead = db.query(Lead).filter(Lead.email.ilike(email_addr)).first()
        if lead:
            lead.status = payload.status
            if payload.status == "Contacted" and not lead.date_contacted:
                lead.date_contacted = datetime.utcnow()
            lead.updated_at = datetime.utcnow()
            updated += 1
        else:
            not_found.append(email_addr)

    db.commit()
    return {
        "data": {"updated": updated, "not_found": not_found},
        "message": f"Updated {updated} leads to '{payload.status}'. {len(not_found)} emails not matched.",
    }


@router.get("/{lead_id}", response_model=dict)
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(Lead).get(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return {"data": LeadResponse.model_validate(lead).model_dump(), "message": "ok"}


@router.put("/{lead_id}", response_model=dict)
def update_lead(lead_id: int, lead_in: LeadUpdate, db: Session = Depends(get_db)):
    lead = db.query(Lead).get(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    for field, value in lead_in.model_dump(exclude_unset=True).items():
        setattr(lead, field, value)

    lead.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(lead)
    return {"data": LeadResponse.model_validate(lead).model_dump(), "message": "Lead updated"}


@router.delete("/{lead_id}", response_model=dict)
def delete_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(Lead).get(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    db.delete(lead)
    db.commit()
    return {"data": None, "message": "Lead deleted"}


@router.patch("/{lead_id}/status", response_model=dict)
def update_lead_status(lead_id: int, status_in: LeadStatusUpdate, db: Session = Depends(get_db)):
    lead = db.query(Lead).get(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    lead.status = status_in.status
    lead.updated_at = datetime.utcnow()
    db.commit()
    return {"data": LeadResponse.model_validate(lead).model_dump(), "message": "Status updated"}


@router.post("/scout/run-now", response_model=dict)
def scout_communities_now(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Manually trigger an immediate community scouting cycle.
    Useful for testing without waiting 3 days.
    Runs in background; returns immediately.
    """
    try:
        from services.lead_scout import run_lead_scout

        # Schedule scout to run in background (synchronous)
        background_tasks.add_task(run_lead_scout)
        return {
            "data": None,
            "message": "Community scouting initiated (runs in background)",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scout error: {e}")
    db.refresh(lead)
    return {"data": LeadResponse.model_validate(lead).model_dump(), "message": f"Status updated to {status_in.status}"}
