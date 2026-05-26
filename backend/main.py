import os
from dotenv import load_dotenv

# Load .env before anything else
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from database import engine, Base
from routers import leads, emails, templates, settings_router, dashboard
from routers import autopilot
from services.scheduler import start_scheduler
from services.reply_checker import start_reply_checker
from services.auto_pilot import start_autopilot
from services.lead_scout import start_lead_scout_loop
import asyncio

app = FastAPI(title="Cold Outreach System", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Create tables
Base.metadata.create_all(bind=engine)

# ── Safe column migrations (AUTOCOMMIT — no lock held between steps) ──────────
def _run_migrations():
    from sqlalchemy import text
    # All columns that might be missing from older deployments
    NEW_COLS = [
        # app_settings — email provider fields
        ("app_settings", "resend_api_key",      "VARCHAR(255)"),
        ("app_settings", "gmail_client_id",     "VARCHAR(512)"),
        ("app_settings", "gmail_client_secret", "VARCHAR(512)"),
        ("app_settings", "gmail_refresh_token", "TEXT"),
        # app_settings — feature flags (added in system hardening)
        ("app_settings", "imap_enabled",        "BOOLEAN DEFAULT FALSE"),
        ("app_settings", "autopilot_enabled",   "BOOLEAN DEFAULT FALSE"),
        # leads — priority + timezone optimisation
        ("leads", "priority",       "BOOLEAN DEFAULT FALSE"),
        ("leads", "lead_timezone",  "VARCHAR(80) DEFAULT 'America/New_York'"),
    ]

    from database import DATABASE_URL
    is_sqlite = DATABASE_URL.startswith("sqlite")

    if is_sqlite:
        # SQLite: use PRAGMA to check columns
        with engine.connect() as conn:
            for table, col, col_type in NEW_COLS:
                try:
                    rows = conn.execute(text(f"PRAGMA table_info({table})")).fetchall()
                    col_names = [r[1] for r in rows]
                    if col not in col_names:
                        # SQLite doesn't support DEFAULT in ADD COLUMN with some types
                        simple_type = col_type.split(" DEFAULT")[0]
                        conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {simple_type}"))
                        conn.commit()
                        print(f"[migration] added {table}.{col} (sqlite)")
                except Exception as e:
                    print(f"[migration] {table}.{col} (sqlite): {e}")
        return

    # PostgreSQL: AUTOCOMMIT so each DDL releases its lock immediately
    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        for table, col, col_type in NEW_COLS:
            try:
                exists = conn.execute(text(
                    "SELECT 1 FROM information_schema.columns "
                    "WHERE table_schema='public' AND table_name=:t AND column_name=:c"
                ), {"t": table, "c": col}).fetchone()
                if not exists:
                    conn.execute(text(f'ALTER TABLE "{table}" ADD COLUMN "{col}" {col_type}'))
                    print(f"[migration] added {table}.{col}")
                else:
                    print(f"[migration] {table}.{col} already exists")
            except Exception as e:
                print(f"[migration] {table}.{col}: {e}")

try:
    _run_migrations()
except Exception as _me:
    print(f"[migration] error: {_me}")

# Include routers
app.include_router(leads.router, prefix="/api/leads", tags=["leads"])
app.include_router(emails.router, prefix="/api/emails", tags=["emails"])
app.include_router(templates.router, prefix="/api/templates", tags=["templates"])
app.include_router(settings_router.router, prefix="/api/settings", tags=["settings"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(autopilot.router, prefix="/api/autopilot", tags=["autopilot"])


@app.on_event("startup")
async def startup():
    from seed_data import seed
    seed()

    # One-time recovery: mark May 25 historical sends as Contacted (SQLite logs gone)
    from database import SessionLocal
    from services.auto_pilot import sync_historical_sends_once
    _db = SessionLocal()
    try:
        sync_historical_sends_once(_db)
    except Exception as _e:
        print(f"[startup] Historical sync error (non-fatal): {_e}")
    finally:
        _db.close()

    asyncio.create_task(start_scheduler())
    asyncio.create_task(start_reply_checker())
    asyncio.create_task(start_autopilot())
    asyncio.create_task(start_lead_scout_loop())


@app.get("/api/health")
def health():
    return {"status": "ok", "message": "Cold Outreach System is running"}


@app.get("/api/debug/db")
def debug_db():
    """Show exact DB error — remove after fixing. Never exposes secrets."""
    from database import SessionLocal
    from sqlalchemy import text
    db = SessionLocal()
    result = {}
    try:
        # 1. Check what columns exist in app_settings
        try:
            rows = db.execute(text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_schema='public' AND table_name='app_settings' "
                "ORDER BY ordinal_position"
            )).fetchall()
            result["app_settings_cols"] = [r[0] for r in rows]
        except Exception as e:
            result["app_settings_cols_error"] = str(e)

        # 2. Try querying AppSettings ORM
        try:
            from models import AppSettings
            s = db.query(AppSettings).first()
            result["settings_query"] = "ok" if s else "no row"
        except Exception as e:
            result["settings_query_error"] = str(e)

        # 3. Check leads columns
        try:
            rows2 = db.execute(text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_schema='public' AND table_name='leads' "
                "ORDER BY ordinal_position"
            )).fetchall()
            result["leads_cols"] = [r[0] for r in rows2]
        except Exception as e:
            result["leads_cols_error"] = str(e)

    finally:
        db.close()
    return result


# ── Serve React frontend in production ──────────────────────────────────────
_DIST = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.exists(_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(_DIST, "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_spa(full_path: str):
        """Catch-all: return index.html so React Router handles navigation."""
        return FileResponse(os.path.join(_DIST, "index.html"))
