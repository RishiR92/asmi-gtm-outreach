import smtplib
import requests
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

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
    if not settings:
        raise HTTPException(status_code=400, detail="No settings configured")

    resend_key = getattr(settings, "resend_api_key", None) or ""

    # ── Test Gmail API OAuth2 (preferred) ────────────────────────────────────
    client_id     = getattr(settings, "gmail_client_id",     None) or ""
    client_secret = getattr(settings, "gmail_client_secret", None) or ""
    refresh_token = getattr(settings, "gmail_refresh_token", None) or ""

    if client_id and client_secret and refresh_token:
        try:
            resp = requests.post(
                "https://oauth2.googleapis.com/token",
                data={"client_id": client_id, "client_secret": client_secret,
                      "refresh_token": refresh_token, "grant_type": "refresh_token"},
                timeout=10,
            )
            if resp.status_code == 200 and resp.json().get("access_token"):
                return {"data": {"success": True, "method": "gmail_api"},
                        "message": "✓ Gmail API credentials valid — ready to send via HTTPS."}
            raise HTTPException(status_code=400,
                detail=f"Gmail OAuth failed: {resp.json().get('error_description', resp.text)}")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Gmail API test failed: {e}")

    # ── Test Resend if key is configured ──────────────────────────────────────
    if resend_key:
        try:
            resp = requests.get(
                "https://api.resend.com/domains",
                headers={"Authorization": f"Bearer {resend_key}"},
                timeout=10,
            )
            if resp.status_code == 200:
                domains = [d.get("name") for d in resp.json().get("data", [])]
                return {
                    "data": {"success": True, "method": "resend"},
                    "message": f"✓ Resend API key valid. Verified domains: {', '.join(domains) or 'none yet'}",
                }
            else:
                raise HTTPException(status_code=400, detail=f"Resend API key invalid: {resp.text}")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Resend connection failed: {e}")

    # ── Fall back to SMTP test ────────────────────────────────────────────────
    if not settings.gmail_email or not settings.gmail_app_password:
        raise HTTPException(
            status_code=400,
            detail="No Resend API key and no Gmail credentials. Add a Resend API key in Settings (recommended) or Gmail App Password.",
        )
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as server:
            server.login(settings.gmail_email, settings.gmail_app_password)
        return {"data": {"success": True, "method": "smtp"}, "message": "✓ Gmail SMTP connection successful."}
    except smtplib.SMTPAuthenticationError:
        raise HTTPException(status_code=400, detail="Gmail authentication failed — use an App Password, not your account password.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"SMTP failed (Railway often blocks SMTP — use Resend instead): {e}")
