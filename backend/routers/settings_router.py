import smtplib
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from database import get_db
from models import AppSettings
from schemas import AppSettingsUpdate, AppSettingsResponse

router = APIRouter()


@router.get("", response_model=dict)
def get_settings(db: Session = Depends(get_db)):
    settings = db.query(AppSettings).first()
    if not settings:
        settings = AppSettings(id=1)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return {"data": AppSettingsResponse.model_validate(settings).model_dump(), "message": "ok"}


@router.put("", response_model=dict)
def update_settings(settings_in: AppSettingsUpdate, db: Session = Depends(get_db)):
    settings = db.query(AppSettings).first()
    if not settings:
        settings = AppSettings(id=1)
        db.add(settings)
        db.flush()

    for field, value in settings_in.model_dump(exclude_unset=True).items():
        setattr(settings, field, value)

    db.commit()
    db.refresh(settings)
    return {"data": AppSettingsResponse.model_validate(settings).model_dump(), "message": "Settings saved"}


@router.get("/test", response_model=dict)
def test_connection(db: Session = Depends(get_db)):
    settings = db.query(AppSettings).first()
    if not settings or not settings.gmail_email or not settings.gmail_app_password:
        raise HTTPException(status_code=400, detail="Gmail credentials not configured")

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(settings.gmail_email, settings.gmail_app_password)
        return {"data": {"success": True}, "message": "SMTP connection successful! Your Gmail credentials are working."}
    except smtplib.SMTPAuthenticationError:
        raise HTTPException(
            status_code=400,
            detail="Authentication failed. Make sure you're using a Gmail App Password (not your regular password). Enable 2FA first, then generate an App Password at myaccount.google.com/apppasswords"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Connection failed: {str(e)}")
