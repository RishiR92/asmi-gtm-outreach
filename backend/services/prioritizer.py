"""
Lead prioritization engine.
Scores each eligible lead and returns the top N for today's send batch.

Score (0–100):
  40pts  Audience size (log-normalized, bigger = higher)
  30pts  Manual priority flag set by user
  20pts  Category fit (AI Tools / Startup-Founder most relevant for Asmi)
   5pts  Has email readily available
   5pts  Not yet attempted (pure New > Email Found > no-email)
"""

import math
import pytz
from datetime import datetime

# Best open-rate window: 9am–11am in lead's local timezone
SEND_WINDOW_START = 9
SEND_WINDOW_END   = 11

# Categories sorted by relevance to Asmi GTM
CATEGORY_SCORE = {
    "AI Tools":        20,
    "Startup-Founder": 18,
    "Productivity":    14,
    "Indian-Origin":   12,
    "Business Owner":  10,
    "Niche":            6,
}


def _audience_score(audience: int) -> float:
    """Log-normalized audience → 0–40 pts."""
    if not audience or audience <= 0:
        return 0
    # max realistic audience ~2M → log10(2_000_000) ≈ 6.3
    return min(40, (math.log10(audience) / 6.3) * 40)


def _tz_in_window(tz_name: str) -> bool:
    """Returns True if right now is in the 9–11am window for the given timezone."""
    try:
        tz = pytz.timezone(tz_name)
        local_hour = datetime.now(tz).hour
        return SEND_WINDOW_START <= local_hour < SEND_WINDOW_END
    except Exception:
        return False


def score_lead(lead) -> float:
    s = 0.0
    s += _audience_score(lead.estimated_audience or 0)
    s += 30 if getattr(lead, "priority", False) else 0
    s += CATEGORY_SCORE.get(lead.category or "", 6)
    s += 5 if lead.email else 0
    s += 5 if lead.status == "New" else 3 if lead.status == "Email Found" else 0
    return round(s, 2)


def get_daily_queue(db, limit: int = 20):
    """
    Returns up to `limit` leads eligible for today's initial outreach,
    sorted by score descending.

    Eligible = has email + not yet contacted (status in New / Email Found).
    """
    from models import Lead

    candidates = (
        db.query(Lead)
        .filter(
            Lead.email != None,
            Lead.email != "",
            Lead.status.in_(["New", "Email Found"]),
        )
        .all()
    )

    scored = [(lead, score_lead(lead)) for lead in candidates]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:limit]


def get_tz_optimised_batch(db, limit: int = 20):
    """
    Same as get_daily_queue but only returns leads whose local timezone
    is currently inside the 9–11am open-rate window.
    Falls back to full priority order if no tz-window leads are available.
    """
    from models import Lead

    candidates = (
        db.query(Lead)
        .filter(
            Lead.email != None,
            Lead.email != "",
            Lead.status.in_(["New", "Email Found"]),
        )
        .all()
    )

    scored = [(lead, score_lead(lead)) for lead in candidates]
    scored.sort(key=lambda x: x[1], reverse=True)

    # Prefer leads whose timezone is currently in morning window
    in_window  = [x for x in scored if _tz_in_window(getattr(x[0], "lead_timezone", "") or "America/New_York")]
    out_window = [x for x in scored if x not in in_window]

    combined = in_window + out_window
    return combined[:limit]
