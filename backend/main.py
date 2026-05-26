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

# ── Safe column migrations (works on all PostgreSQL versions) ─────────────────
def _add_column_if_missing(conn, table: str, column: str, col_type: str):
    """Add a column only if it doesn't already exist — checks information_schema."""
    from sqlalchemy import text
    exists = conn.execute(text(
        "SELECT 1 FROM information_schema.columns "
        "WHERE table_name=:t AND column_name=:c"
    ), {"t": table, "c": column}).fetchone()
    if not exists:
        conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}"))
        conn.commit()
        print(f"[migration] added column {table}.{column}")

def _run_migrations():
    NEW_COLS = [
        ("app_settings", "resend_api_key",    "VARCHAR(255)"),
        ("app_settings", "gmail_client_id",   "VARCHAR(512)"),
        ("app_settings", "gmail_client_secret","VARCHAR(512)"),
        ("app_settings", "gmail_refresh_token","TEXT"),
    ]
    with engine.connect() as conn:
        for table, col, col_type in NEW_COLS:
            try:
                _add_column_if_missing(conn, table, col, col_type)
            except Exception as e:
                print(f"[migration] could not add {table}.{col}: {e}")

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


# ── Serve React frontend in production ──────────────────────────────────────
_DIST = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.exists(_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(_DIST, "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_spa(full_path: str):
        """Catch-all: return index.html so React Router handles navigation."""
        return FileResponse(os.path.join(_DIST, "index.html"))
