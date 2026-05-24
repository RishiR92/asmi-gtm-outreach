import imaplib
import email
import email.utils
import asyncio
from datetime import datetime, timedelta


async def start_reply_checker():
    while True:
        await asyncio.sleep(7200)  # 2 hours
        try:
            check_replies()
        except Exception as e:
            print(f"Reply checker error: {e}")


def check_replies():
    from database import SessionLocal
    from models import AppSettings, Lead, ScheduledEmail

    db = SessionLocal()
    try:
        settings = db.query(AppSettings).first()
        if not settings or not settings.imap_enabled:
            return

        if not settings.gmail_email or not settings.gmail_app_password:
            print("IMAP: Gmail credentials not configured")
            return

        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(settings.gmail_email, settings.gmail_app_password)
        mail.select("inbox")

        # Search emails from last 24 hours
        since = (datetime.now() - timedelta(hours=24)).strftime("%d-%b-%Y")
        _, data = mail.search(None, f'(SINCE {since})')

        contacted_leads = db.query(Lead).filter(Lead.status == "Contacted").all()
        lead_emails = {l.email.lower(): l for l in contacted_leads if l.email}

        if not lead_emails:
            mail.logout()
            return

        for num in data[0].split():
            try:
                _, msg_data = mail.fetch(num, "(RFC822)")
                if not msg_data or not msg_data[0]:
                    continue
                msg = email.message_from_bytes(msg_data[0][1])
                from_addr = email.utils.parseaddr(msg["From"])[1].lower()

                if from_addr in lead_emails:
                    lead = lead_emails[from_addr]
                    lead.status = "Replied"
                    # Cancel pending follow-ups
                    db.query(ScheduledEmail).filter(
                        ScheduledEmail.lead_id == lead.id,
                        ScheduledEmail.status == "pending"
                    ).update({"status": "cancelled"})
                    db.commit()
                    print(f"Reply detected from {from_addr}, updated lead {lead.name} to Replied")
            except Exception as e:
                print(f"Error processing email {num}: {e}")
                continue

        mail.logout()
    except Exception as e:
        print(f"IMAP error: {e}")
    finally:
        db.close()
