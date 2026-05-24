#!/usr/bin/env python3
"""
Standalone daily send script — for GitHub Actions (no FastAPI server needed).

Usage:
    python backend/run_daily_send.py

Env vars required (set as GitHub Secrets):
    GMAIL_EMAIL
    GMAIL_APP_PASSWORD
    SENDER_NAME          (optional, default: Rishi)
    DAILY_SEND_LIMIT     (optional, default: 20)
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

# Override from env vars (GitHub Secrets inject these)
GMAIL_EMAIL       = os.environ.get("GMAIL_EMAIL", "")
GMAIL_APP_PASSWORD= os.environ.get("GMAIL_APP_PASSWORD", "")
SENDER_NAME       = os.environ.get("SENDER_NAME", "Rishi")
DAILY_LIMIT       = int(os.environ.get("DAILY_SEND_LIMIT", "20"))


def main():
    from database import SessionLocal, engine, Base
    from models import AppSettings, Lead, Template, EmailLog, ScheduledEmail

    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Ensure settings are correct
        settings = db.query(AppSettings).first()
        if not settings:
            settings = AppSettings(id=1)
            db.add(settings)

        if GMAIL_EMAIL:
            settings.gmail_email = GMAIL_EMAIL
        if GMAIL_APP_PASSWORD:
            settings.gmail_app_password = GMAIL_APP_PASSWORD
        settings.sender_name      = SENDER_NAME
        settings.daily_send_limit = DAILY_LIMIT
        settings.autopilot_enabled= True
        db.commit()

        print(f"[run_daily_send] Using account: {settings.gmail_email}")
        print(f"[run_daily_send] Daily limit: {settings.daily_send_limit}")

        from services.auto_pilot import run_autopilot_cycle
        run_autopilot_cycle()

    finally:
        db.close()

    print("[run_daily_send] Done.")


if __name__ == "__main__":
    main()
