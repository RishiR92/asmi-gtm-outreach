"""
Automated lead discovery: scouts web communities (Reddit, Facebook, Discord)
matching Asmi use cases, scores by relevance/conversion potential,
and auto-adds new community leaders to the leads table.

Runs every 3 days via background scheduler.
"""

import asyncio
import logging
import os
from datetime import datetime
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# Load .env for background tasks
load_dotenv()

logger = logging.getLogger(__name__)

# ── Community search topics ──────────────────────────────────────────────────
# PRIMARY: Newsletter authors — individual writers with personal email addresses.
# These are the highest-value leads (direct person, not org inbox).
# SECONDARY: Community orgs — lower priority, almost always have generic emails.
COMMUNITY_TOPICS = {
    # ── Newsletter authors (personal emails, highest priority) ───────────────
    "AI-Newsletter": {
        "keywords": ["AI newsletter", "artificial intelligence newsletter writer",
                     "machine learning newsletter", "AI tools newsletter author",
                     "ChatGPT newsletter", "LLM newsletter substack"],
        "category": "Newsletter",
        "relevance_score": 98,
        "description": "AI/ML newsletter authors and writers"
    },
    "Tech-Newsletter": {
        "keywords": ["tech newsletter author", "technology newsletter substack",
                     "software engineering newsletter", "developer newsletter writer",
                     "indie hacker newsletter", "product newsletter substack"],
        "category": "Newsletter",
        "relevance_score": 95,
        "description": "Technology and developer newsletter writers"
    },
    "Business-Newsletter": {
        "keywords": ["business newsletter author", "entrepreneurship newsletter substack",
                     "startup newsletter writer", "VC newsletter", "founder newsletter",
                     "product management newsletter"],
        "category": "Newsletter",
        "relevance_score": 93,
        "description": "Business and entrepreneurship newsletter writers"
    },
    "Productivity-Newsletter": {
        "keywords": ["productivity newsletter author", "personal development newsletter",
                     "self improvement newsletter substack", "GTD newsletter writer",
                     "remote work newsletter author"],
        "category": "Newsletter",
        "relevance_score": 90,
        "description": "Productivity and self-improvement newsletter writers"
    },
    # ── Professional communities (org contacts, lower priority) ─────────────
    "Startup-Founder": {
        "keywords": ["startup", "entrepreneur", "founder", "indie_hackers", "solopreneur"],
        "category": "Startup-Founder",
        "relevance_score": 85,
        "description": "Founders building businesses"
    },
    "Real Estate": {
        "keywords": ["realestate", "realtor", "property investor"],
        "category": "Business Owner",
        "relevance_score": 80,
        "description": "Real estate agents and investors"
    },
    "Healthcare": {
        "keywords": ["doctors", "healthcare professional", "nurses community"],
        "category": "Business Owner",
        "relevance_score": 82,
        "description": "Healthcare professionals (extremely time-constrained)"
    },
}

# ── Size-based relevance boost ──────────────────────────────────────────────
SIZE_BRACKETS = {
    "small": (1_000, 10_000, 70),          # 1K-10K members
    "medium": (10_000, 100_000, 85),       # 10K-100K (sweet spot)
    "large": (100_000, 500_000, 80),       # 100K-500K (harder to reach manager)
}


def score_community(community_data: dict) -> float:
    """
    Rate a community by relevance + conversion probability (0-100).

    Factors:
    - Topic relevance to Asmi use case
    - Community size (medium > small > large; huge is hard to reach)
    - Activity/engagement level
    - Manager accessibility (inferred from community metadata)
    """
    score = 0.0

    # Topic relevance (base score)
    topic = community_data.get("topic")
    if topic and topic in COMMUNITY_TOPICS:
        score += COMMUNITY_TOPICS[topic]["relevance_score"]
    else:
        score += 40  # generic relevance

    # Size bonus/penalty
    members = community_data.get("members", 0)
    for bracket_name, (min_size, max_size, bracket_score) in SIZE_BRACKETS.items():
        if min_size <= members < max_size:
            score = (score + bracket_score) / 2  # average with base
            break

    # Activity level (post frequency, engagement)
    activity = community_data.get("activity_level", 0.5)  # 0-1 scale
    score += activity * 10

    # Manager accessibility (do we have contact info?)
    if community_data.get("manager_email"):
        score += 15
    elif community_data.get("manager_url") or community_data.get("manager_social"):
        score += 8

    return min(100, score)


def _deduplicate_by_url(db: Session, url: str) -> bool:
    """Returns True if a lead with this URL already exists."""
    from models import Lead
    existing = db.query(Lead).filter(Lead.url == url).first()
    return existing is not None


def _deduplicate_by_name(db: Session, name: str) -> bool:
    """Returns True if a lead with this name + newsletter name combo exists."""
    from models import Lead
    # Exact match on newsletter_name (community name)
    existing = db.query(Lead).filter(Lead.newsletter_name == name).first()
    return existing is not None


def run_lead_scout():
    """
    Execute the full scouting cycle:
    1. Check if pipeline needs refilling (eligible leads < threshold)
    2. If yes, scrape communities from multiple sources (Meetup, Google Search)
    3. Score by relevance, deduplicate, insert into DB
    4. Tracks eligible (with email) vs. ineligible (no email) leads separately
    """
    from database import SessionLocal
    from models import Lead, AppSettings

    db = SessionLocal()
    try:
        # ── Check current pipeline status ────────────────────────────────────
        settings = db.query(AppSettings).first()
        daily_limit = (settings.daily_send_limit if settings else 20) or 20
        target_eligible = daily_limit * 3.5  # 3 days + 0.5 buffer = 3.5× daily_limit

        # Eligible = has email + status in [New, Email Found] + not yet contacted
        eligible_count = db.query(Lead).filter(
            Lead.email != None,
            Lead.email != "",
            Lead.status.in_(["New", "Email Found"]),
        ).count()

        print(f"[scout] Pipeline check: {eligible_count} eligible leads (target: {target_eligible:.0f})")

        if eligible_count >= target_eligible:
            print(f"[scout] Pipeline full ({eligible_count} >= {target_eligible:.0f}). Skipping this cycle.")
            return

        print(f"[scout] Pipeline thin ({eligible_count} < {target_eligible:.0f}). Starting aggressive scouting...")

        new_leads = []
        eligible_new = 0
        ineligible_new = 0

        # ── Scout Meetup ───────────────────────────────────────────────────
        print("[scout] Scouting Meetup.com groups...")
        try:
            from .community_scrapers.meetup_scraper import scout_meetup_sync
            meetup_communities = scout_meetup_sync(topics=COMMUNITY_TOPICS)
            print(f"[scout] Found {len(meetup_communities)} Meetup groups")

            for comm in meetup_communities:
                # Skip if already in DB
                if _deduplicate_by_name(db, comm["newsletter_name"]):
                    continue

                # Score and filter (lower threshold for aggressive scouting)
                comm["score"] = score_community(comm)
                if comm["score"] < 40:
                    continue

                has_email = bool(comm.get("manager_email"))

                # Create lead object
                lead = Lead(
                    name=comm.get("manager_name") or f"{comm['newsletter_name']} Organizer",
                    newsletter_name=comm["newsletter_name"],
                    url=comm.get("url", ""),
                    estimated_audience=comm.get("members", 0),
                    category=comm.get("category", "Niche"),
                    email=comm.get("manager_email", ""),
                    status="Email Found" if has_email else "New",
                    notes=f"[AUTO-SCOUT] {comm['description']} | Relevance: {comm['score']:.0f} | Source: {comm.get('source', 'unknown')}",
                )
                new_leads.append(lead)

                if has_email:
                    eligible_new += 1
                else:
                    ineligible_new += 1

        except Exception as e:
            print(f"[scout] Meetup scouting failed: {e}")

        # ── Scout Google Search ────────────────────────────────────────────
        print("[scout] Scouting via Google Search...")
        try:
            from .community_scrapers.google_search_scraper import scout_google_sync
            search_communities = scout_google_sync(topics=COMMUNITY_TOPICS)
            print(f"[scout] Found {len(search_communities)} communities via search")

            for comm in search_communities:
                # Skip if already in DB
                if _deduplicate_by_name(db, comm["newsletter_name"]):
                    continue

                # Score and filter (lower threshold for aggressive scouting)
                comm["score"] = score_community(comm)
                if comm["score"] < 40:  # lower threshold to cast wider net
                    continue

                has_email = bool(comm.get("manager_email"))

                # Create lead object
                lead = Lead(
                    name=comm.get("manager_name") or f"{comm['newsletter_name']} Manager",
                    newsletter_name=comm["newsletter_name"],
                    url=comm.get("url", ""),
                    estimated_audience=comm.get("members", 0),
                    category=comm.get("category", "Niche"),
                    email=comm.get("manager_email", ""),
                    status="Email Found" if has_email else "New",
                    notes=f"[AUTO-SCOUT] {comm['description']} | Relevance: {comm['score']:.0f} | Source: {comm.get('source', 'unknown')}",
                )
                new_leads.append(lead)

                if has_email:
                    eligible_new += 1
                else:
                    ineligible_new += 1

        except Exception as e:
            print(f"[scout] Google search scouting failed: {e}")

        # ── Scout Community Seeds (reliable fallback) ────────────────────────
        print("[scout] Adding seed communities...")
        try:
            from .community_scrapers.community_seeds import get_seed_communities
            from models import Lead

            seed_communities = get_seed_communities(topics=COMMUNITY_TOPICS)
            print(f"[scout] Found {len(seed_communities)} seed communities")

            for comm in seed_communities:
                # Score and filter
                comm["score"] = score_community(comm)
                if comm["score"] < 40:
                    continue

                has_email = bool(comm.get("manager_email"))

                # Check if this seed already exists
                existing = db.query(Lead).filter(Lead.newsletter_name == comm["newsletter_name"]).first()
                if existing:
                    # Update existing seed with email if we have one
                    if has_email and not existing.email:
                        existing.email = comm.get("manager_email", "")
                        existing.status = "Email Found"
                        db.commit()
                        if has_email:
                            eligible_new += 1
                    continue

                # Create new lead object
                lead = Lead(
                    name=comm.get("manager_name") or f"{comm['newsletter_name']} Organizer",
                    newsletter_name=comm["newsletter_name"],
                    url=comm.get("url", ""),
                    estimated_audience=comm.get("members", 0),
                    category=comm.get("category", "Niche"),
                    email=comm.get("manager_email", ""),
                    status="Email Found" if has_email else "New",
                    notes=f"[AUTO-SCOUT] {comm['description']} | Relevance: {comm['score']:.0f} | Source: {comm.get('source', 'unknown')}",
                )
                new_leads.append(lead)

                if has_email:
                    eligible_new += 1
                else:
                    ineligible_new += 1

        except Exception as e:
            print(f"[scout] Seed community loading failed: {e}")

        # ── Insert new leads ────────────────────────────────────────────────
        if new_leads:
            for lead in new_leads:
                db.add(lead)
            db.commit()

            new_eligible_total = eligible_count + eligible_new
            print(f"[scout] Added {len(new_leads)} new community leaders:")
            print(f"       → {eligible_new} with email (eligible, count towards queue)")
            print(f"       → {ineligible_new} without email (added as New, don't count yet)")
            print(f"[scout] Pipeline now: {new_eligible_total} eligible leads (target: {target_eligible:.0f})")

            if new_eligible_total < target_eligible:
                print(f"[scout] ⚠️  Still below target. Consider running another scout cycle soon.")

            # ── Push new leads to Railway so both DBs stay in sync ──────────
            try:
                from services.railway_sync import push_new_leads_to_railway
                push_new_leads_to_railway(db, new_leads)
            except Exception as push_err:
                print(f"[scout] Railway push failed (leads saved locally): {push_err}")
        else:
            print("[scout] No new communities found this cycle")

        print("[scout] Community discovery cycle complete")

    except Exception as e:
        print(f"[scout] Fatal error: {e}")
        db.rollback()
    finally:
        db.close()


# ── Background task loop (sync) ─────────────────────────────────────────────
import asyncio

async def start_lead_scout_loop():
    """
    Background task: runs lead scouting every 3 days (259,200 seconds).
    Called from main.py startup.
    """
    print("[scout] Lead scout background task started. Runs every 3 days.")
    while True:
        try:
            await asyncio.sleep(259_200)  # 3 days = 259,200 seconds
            await asyncio.to_thread(run_lead_scout)  # run sync work off the event loop
        except Exception as e:
            print(f"[scout] Background loop error: {e}")
            await asyncio.sleep(60)  # brief retry delay on error
