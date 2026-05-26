"""
Lead prioritization engine — conversion-based scoring.
Scores each eligible lead by how many Asmi users they're likely to bring
via a partnership, then surfaces leads above the 1,000-user viability bar.

Conversion funnel:
  estimated_asmi_users = lead.estimated_audience × CONVERSION_RATE[category]

Score (0–100):
  60 pts  Estimated Asmi users (log-normalized; reference: 10 000 users = 60 pts)
  25 pts  Category alignment (AI-native & founders convert best)
  10 pts  Manual priority flag
   5 pts  Contact readiness (has email + status)

Return type for queue functions: [(lead, score, estimated_asmi_users, is_viable), ...]
  is_viable = estimated_asmi_users >= MIN_VIABLE_ASMI_USERS
  Viable leads always sort before non-viable; ties broken by score descending.
"""

import math
import pytz
from datetime import datetime

# ── Conversion rates: followers → Asmi users ────────────────────────────────
# AI Tools newsletters have tech-forward audiences highly aligned with Asmi.
# Indian-Origin is cultural affinity only; lower product-market fit → low rate.
CONVERSION_RATE: dict[str, float] = {
    "AI Tools":        0.0100,   # 1.0%  — 1 in 100 followers becomes an Asmi user
    "Startup-Founder": 0.0060,   # 0.6%
    "Business Owner":  0.0030,   # 0.3%
    "Niche":           0.0020,   # 0.2%
    "Productivity":    0.0015,   # 0.15%
    "Indian-Origin":   0.0005,   # 0.05%
}
DEFAULT_CONVERSION_RATE = 0.0010   # fallback for unlisted categories

MIN_VIABLE_ASMI_USERS = 1_000      # minimum partnership threshold

# ── Category alignment scores (25 pts max) ──────────────────────────────────
CATEGORY_SCORE: dict[str, int] = {
    "AI Tools":        25,
    "Startup-Founder": 22,
    "Business Owner":  18,
    "Niche":           14,
    "Productivity":    12,
    "Indian-Origin":    8,
}

# ── Timezone window ──────────────────────────────────────────────────────────
SEND_WINDOW_START = 9
SEND_WINDOW_END   = 11


# ── Core helpers ─────────────────────────────────────────────────────────────

def _estimated_asmi_users(lead) -> float:
    """Followers × category conversion rate → projected Asmi users."""
    audience = lead.estimated_audience or 0
    if audience <= 0:
        return 0.0
    rate = CONVERSION_RATE.get(lead.category or "", DEFAULT_CONVERSION_RATE)
    return audience * rate


def _asmi_user_score(estimated: float) -> float:
    """
    Log-normalized score: 0–60 pts.
    Reference point: 10 000 Asmi users = 60 pts.
    """
    if estimated <= 0:
        return 0.0
    # log10(10_000) = 4.0  → used as the normalization ceiling
    return min(60.0, (math.log10(estimated) / 4.0) * 60.0)


def _tz_in_window(tz_name: str) -> bool:
    """True if it is currently 9–11 am in the given timezone."""
    try:
        tz = pytz.timezone(tz_name)
        local_hour = datetime.now(tz).hour
        return SEND_WINDOW_START <= local_hour < SEND_WINDOW_END
    except Exception:
        return False


# ── Public scoring API ────────────────────────────────────────────────────────

# Generic email prefixes — deprioritised vs personal addresses
_GENERIC_PREFIXES = (
    'contact@', 'hello@', 'info@', 'admin@', 'team@', 'support@',
    'editor@', 'newsletter@', 'hi@', 'mail@', 'press@', 'media@',
    'marketing@', 'organizer@', 'manager@', 'group@', 'community@',
    'members@',
)

def _is_personal_email(email: str) -> bool:
    """Returns True if the email looks like a personal/named address."""
    e = (email or '').lower()
    return bool(e) and not any(e.startswith(p) for p in _GENERIC_PREFIXES)


def score_lead(lead) -> tuple[float, float, bool]:
    """
    Returns (score, estimated_asmi_users, is_viable).

    score              — 0–100 composite
    estimated_asmi_users — projected Asmi users from this partnership
    is_viable          — True if estimated_asmi_users >= MIN_VIABLE_ASMI_USERS
    """
    asmi_users = _estimated_asmi_users(lead)
    is_viable  = asmi_users >= MIN_VIABLE_ASMI_USERS

    s = 0.0
    s += _asmi_user_score(asmi_users)                              # 0–60 pts
    s += CATEGORY_SCORE.get(lead.category or "", 8)                # 0–25 pts
    s += 10 if getattr(lead, "priority", False) else 0             # 0–10 pts
    # Personal email gets +5; generic (contact@, hello@, …) gets 0
    s += 5 if _is_personal_email(lead.email or "") else 0          # 0–5 pts (personal email bonus)
    s += 2 if lead.status == "New" else 1 if lead.status == "Email Found" else 0

    return round(s, 2), round(asmi_users, 1), is_viable


def _build_queue(candidates, limit: int):
    """
    Score all candidates, sort viable leads first then by score, return top N.

    Returns: [(lead, score, estimated_asmi_users, is_viable), ...]
    """
    scored = []
    for lead in candidates:
        s, asmi_users, viable = score_lead(lead)
        scored.append((lead, s, asmi_users, viable))

    # Viable leads always surface first; within each group sort by score desc
    scored.sort(key=lambda x: (not x[3], -x[1]))
    return scored[:limit]


def get_daily_queue(db, limit: int = 20):
    """
    Returns up to `limit` leads eligible for today's initial outreach,
    viable leads (≥1 000 Asmi users) first, then by score descending.

    Eligible = has email + status in {New, Email Found}.
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

    return _build_queue(candidates, limit)


def get_tz_optimised_batch(db, limit: int = 20):
    """
    Same as get_daily_queue but prefers leads whose local timezone is
    currently inside the 9–11 am open-rate window.
    Falls back to full priority order if no in-window leads are available.
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

    scored = []
    for lead in candidates:
        s, asmi_users, viable = score_lead(lead)
        scored.append((lead, s, asmi_users, viable))

    # Separate in-window and out-of-window, each sorted viable-first then score
    def sort_key(x):
        return (not x[3], -x[1])

    in_window  = sorted(
        [x for x in scored if _tz_in_window(getattr(x[0], "lead_timezone", "") or "America/New_York")],
        key=sort_key,
    )
    out_window = sorted(
        [x for x in scored if x not in in_window],
        key=sort_key,
    )

    combined = in_window + out_window
    return combined[:limit]
