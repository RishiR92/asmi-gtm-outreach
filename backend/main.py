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
