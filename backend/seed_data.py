from database import SessionLocal
from models import Template, Lead, AppSettings
import os

# ── Canonical template — edit here, deploys on next restart ──────────────────
CANONICAL_TEMPLATE = dict(
    name="Asmi Outreach",
    category="AI Tools",
    subject_a="Intro: Asmi (2x Founder, raised $100M + FAIR/DeepMind scientists)",
    subject_b="Intro: Asmi (2x Founder, raised $100M + FAIR/DeepMind scientists)",
    body=(
        "Hi {{name}},\n\n"
        "I'm Rishi - previously built and scaled a consumer platform to 600M+ users across Asia, "
        "raised ~$100M from SoftBank, DoorDash and Zoom founders. My co-founder Satwik is ex-FAIR "
        "and DeepMind, CMU PhD, 40+ highly cited papers on large action models.\n\n"
        "We just launched Asmi - AI that handles your personal chores in the physical world.\n\n"
        "You tell it what's stuck. It calls your dentist, bank, plumber, friends - navigates IVR, "
        "waits on hold, follows up - and pings you on WhatsApp or iMessage when done. No app. No screen.\n\n"
        "What it's handled this week:\n"
        "• $47 charge on a bill - Asmi called, navigated the IVR, got it reversed\n"
        "• 5 plumbers called, quotes compared, best one booked\n"
        "• Daily check-in with a user's elderly mother in Rome. In Italian.\n\n"
        "5,000+ real-world tasks closed in 4 weeks of beta. Zero paid acquisition.\n\n"
        "Backed by Jack Brody (CPO Suno AI, ex-CPO Snap), ex-GenAI head Meta, and founders of frontier AI labs.\n\n"
        "Would love to explore getting Asmi in front of your audience - happy to chat about what makes sense.\n\n"
        "Regards,\n"
        "Rishi"
    ),
    followup1_subject="Following up — Asmi",
    followup1_body=(
        "Hi {{name}},\n\n"
        "Just circling back on Asmi. The traction — 5,000+ real-world tasks, zero paid acquisition, "
        "40%+ day-7 retention — is pretty unique right now.\n\n"
        "Would love 15 min to talk through what a collaboration could look like.\n\n"
        "Regards,\n"
        "Rishi"
    ),
    followup2_subject="Last note — Asmi",
    followup2_body=(
        "Hi {{name}},\n\n"
        "Final message from me. If the timing isn't right, totally understand — "
        "would love to reconnect when it is.\n\n"
        "Regards,\n"
        "Rishi"
    ),
)


def _enforce_template(db):
    """
    Creates the canonical template ONLY if no template exists yet.
    User edits via UI are never overwritten on redeploy.
    """
    if db.query(Template).count() > 0:
        return   # already exists — never clobber user edits
    tmpl = Template(**CANONICAL_TEMPLATE)
    db.add(tmpl)
    db.commit()
    print("[seed] Template seeded (first run).")


def seed():
    db = SessionLocal()
    try:
        # Always enforce the single correct template on every startup/deploy
        _enforce_template(db)

        # Only seed leads + settings on first run (empty DB)
        if db.query(Lead).count() > 0:
            return

        print("[seed] First run detected — seeding settings and leads...")

        # Seed AppSettings
        if db.query(AppSettings).count() == 0:
            settings = AppSettings(
                id=1,
                gmail_email=os.environ.get("GMAIL_EMAIL", ""),
                gmail_app_password=os.environ.get("GMAIL_APP_PASSWORD", ""),
                sender_name=os.environ.get("SENDER_NAME", "Rishi"),
                daily_send_limit=40,  # 40/day × 3 days = 120 leads in pipeline
                followup1_days=4,
                followup2_days=9,
                send_hours_start=9,
                send_hours_end=17,
                timezone="America/Los_Angeles",
                imap_enabled=False,
            )
            db.add(settings)
            db.commit()

        # Seed leads
        leads_data = [
            {"name": "Matt Wolfe", "newsletter_name": "Future Tools", "url": "futuretools.io", "estimated_audience": 230000, "category": "AI Tools", "contact_method": "Email", "email": "mreflow@futuretools.io", "twitter_handle": "@mreflow", "status": "Email Found"},
            {"name": "AI Toolhouse", "newsletter_name": "AI Toolhouse Newsletter", "url": "aitoolhouse.com", "estimated_audience": 11000, "category": "AI Tools", "contact_method": "Email", "email": "hello@aitoolhouse.com", "status": "Email Found"},
            {"name": "Andy Zhao", "newsletter_name": "There's An AI For That", "url": "theresanaiforthat.com", "estimated_audience": 1700000, "category": "AI Tools", "contact_method": "Email", "email": "andy@theresanaiforthat.com", "status": "Email Found"},
            {"name": "Pete Huang", "newsletter_name": "The Neuron", "url": "theneurondaily.com", "estimated_audience": 500000, "category": "AI Tools", "contact_method": "Email", "email": "pete@theneurondaily.com", "status": "Email Found"},
            {"name": "AI Fire", "newsletter_name": "AI Fire Newsletter", "url": "aifire.co", "estimated_audience": 65000, "category": "AI Tools", "contact_method": "Email", "email": "contact@aifire.co", "status": "Email Found"},
            {"name": "The AI Entrepreneurs", "newsletter_name": "The AI Entrepreneurs", "url": "theaientrepreneurs.com", "estimated_audience": 70000, "category": "AI Tools", "contact_method": "Submission Form", "email": "", "notes": "Find email via site", "status": "New"},
            {"name": "AI Tool Report", "newsletter_name": "AI Tool Report", "url": "theaireport.ai", "estimated_audience": 50000, "category": "AI Tools", "contact_method": "Email", "email": "contact@theaireport.ai", "status": "Email Found"},
            {"name": "Alex Banks", "newsletter_name": "Sunday Signal", "url": "sundaysignal.ai", "estimated_audience": 40000, "category": "Productivity", "contact_method": "Email", "email": "alex@sundaysignal.ai", "status": "Email Found"},
            {"name": "Linas Beliunas", "newsletter_name": "Linas Newsletter", "url": "linas.substack.com", "estimated_audience": 355000, "category": "Productivity", "contact_method": "LinkedIn", "email": "", "linkedin_url": "linkedin.com/in/linasbeliunas", "notes": "Find email via LinkedIn", "status": "New"},
            {"name": "Wes Kao", "newsletter_name": "Wes Kao Newsletter", "url": "weskao.com", "estimated_audience": 120000, "category": "Productivity", "contact_method": "Email", "email": "wes@weskao.com", "status": "Email Found"},
            {"name": "AI Hustle", "newsletter_name": "AI Hustle", "url": "aihustle.com", "estimated_audience": 30000, "category": "Productivity", "contact_method": "Submission Form", "email": "", "notes": "Find email via site", "status": "New"},
            {"name": "Chris Baylis", "newsletter_name": "Finxter", "url": "finxter.com", "estimated_audience": 50000, "category": "Productivity", "contact_method": "Email", "email": "chris@finxter.com", "status": "Email Found"},
            {"name": "Swyx", "newsletter_name": "Latent Space", "url": "latent.space", "estimated_audience": 200000, "category": "Startup-Founder", "contact_method": "Email", "email": "swyx@swyx.io", "twitter_handle": "@swyx", "status": "Email Found"},
            {"name": "Dan Shipper", "newsletter_name": "Every", "url": "every.to", "estimated_audience": 75000, "category": "Startup-Founder", "contact_method": "Email", "email": "dan@every.to", "twitter_handle": "@danshipper", "status": "Email Found"},
            {"name": "Ethan Mollick", "newsletter_name": "One Useful Thing", "url": "oneusefulthing.org", "estimated_audience": 500000, "category": "Startup-Founder", "contact_method": "Email", "email": "emollick@wharton.upenn.edu", "twitter_handle": "@emollick", "status": "Email Found"},
            {"name": "Pat Walls", "newsletter_name": "Starter Story", "url": "starterstory.com", "estimated_audience": 50000, "category": "Business Owner", "contact_method": "Email", "email": "pat@starterstory.com", "status": "Email Found"},
            {"name": "Sean Scott", "newsletter_name": "Product Hustle Stack", "url": "producthustlestack.substack.com", "estimated_audience": 15000, "category": "Startup-Founder", "contact_method": "Submission Form", "email": "", "notes": "Find email via Substack", "status": "New"},
            {"name": "Codie Sanchez", "newsletter_name": "Contrarian Thinking", "url": "contrariancontrarian.com", "estimated_audience": 1000000, "category": "Business Owner", "contact_method": "Email", "email": "", "notes": "Find email via team page", "status": "New"},
            {"name": "Dan Ni", "newsletter_name": "TLDR Founders", "url": "tldr.tech", "estimated_audience": 200000, "category": "Startup-Founder", "contact_method": "Email", "email": "dan@tldr.tech", "status": "Email Found"},
            {"name": "Aakash Gupta", "newsletter_name": "Product Growth", "url": "aakashg.com", "estimated_audience": 455000, "category": "Indian-Origin", "contact_method": "Email", "email": "aakash@aakashg.com", "linkedin_url": "linkedin.com/in/aakashgupta", "status": "Email Found"},
            {"name": "Shreyas Doshi", "newsletter_name": "Shreyas Doshi Newsletter", "url": "shreyasdoshi.com", "estimated_audience": 334000, "category": "Indian-Origin", "contact_method": "X DM", "email": "", "twitter_handle": "@shreyas", "notes": "Find email via X @shreyas", "status": "New"},
            {"name": "Zain Kahn", "newsletter_name": "Superhuman AI", "url": "superhuman.ai", "estimated_audience": 1500000, "category": "Indian-Origin", "contact_method": "Email", "email": "zain@superhuman.ai", "twitter_handle": "@heykahn", "status": "Email Found"},
            {"name": "Vaibhav Sisinty", "newsletter_name": "GrowthSchool", "url": "growthschool.io", "estimated_audience": 200000, "category": "Indian-Origin", "contact_method": "Email", "email": "vaibhav@growthschool.io", "linkedin_url": "linkedin.com/in/vaibhavsisinty", "status": "Email Found"},
            {"name": "Sachin Rekhi", "newsletter_name": "Sachin Rekhi Newsletter", "url": "sachinrekhi.com", "estimated_audience": 50000, "category": "Indian-Origin", "contact_method": "Email", "email": "sachin@sachinrekhi.com", "linkedin_url": "linkedin.com/in/sachinrekhi", "status": "Email Found"},
            {"name": "Desi Founder", "newsletter_name": "Desi Founder", "url": "desifounder.com", "estimated_audience": 20000, "category": "Indian-Origin", "contact_method": "Email", "email": "hello@desifounder.com", "status": "Email Found"},
            {"name": "The Assist", "newsletter_name": "The Assist", "url": "theassist.io", "estimated_audience": 100000, "category": "Business Owner", "contact_method": "Email", "email": "hello@theassist.io", "status": "Email Found"},
            {"name": "Indie Hackers", "newsletter_name": "Indie Hackers", "url": "indiehackers.com", "estimated_audience": 60000, "category": "Startup-Founder", "contact_method": "Submission Form", "email": "", "notes": "Find email via site", "status": "New"},
            {"name": "AI Valley", "newsletter_name": "AI Valley", "url": "aivalley.ai", "estimated_audience": 40000, "category": "AI Tools", "contact_method": "Submission Form", "email": "", "notes": "Find email via site", "status": "New"},
            {"name": "Neat Prompts", "newsletter_name": "Neat Prompts", "url": "neatprompts.com", "estimated_audience": 30000, "category": "Productivity", "contact_method": "Submission Form", "email": "", "notes": "Find email via site", "status": "New"},
            {"name": "Sahar Mor", "newsletter_name": "AI Tidbits", "url": "", "estimated_audience": 20000, "category": "AI Tools", "contact_method": "LinkedIn", "email": "", "notes": "Find email via LinkedIn", "status": "New"},
            {"name": "Mindstream", "newsletter_name": "Mindstream", "url": "mindstream.news", "estimated_audience": 150000, "category": "AI Tools", "contact_method": "Email", "email": "hello@mindstream.news", "status": "Email Found"},
            {"name": "Ben Tossell", "newsletter_name": "Ben's Bites", "url": "bensbites.beehiiv.com", "estimated_audience": 120000, "category": "AI Tools", "contact_method": "Email", "email": "ben@bensbites.co", "twitter_handle": "@bentossell", "status": "Email Found"},
            {"name": "Shiva Bhaskar", "newsletter_name": "1947 Tech", "url": "1947tech.substack.com", "estimated_audience": 15000, "category": "Indian-Origin", "contact_method": "Email", "email": "shiva@1947tech.com", "status": "Email Found"},
            {"name": "The AI PM Newsletter", "newsletter_name": "The AI PM Newsletter", "url": "", "estimated_audience": 30000, "category": "Startup-Founder", "contact_method": "Submission Form", "email": "", "notes": "Find email via site", "status": "New"},
            {"name": "Lenny Rachitsky", "newsletter_name": "Lenny's Newsletter", "url": "lennysnewsletter.com", "estimated_audience": 650000, "category": "Startup-Founder", "contact_method": "Email", "email": "lenny@lennysnewsletter.com", "twitter_handle": "@lennysan", "status": "Email Found"},
        ]

        for lead_data in leads_data:
            lead = Lead(**lead_data)
            db.add(lead)

        db.commit()
        print(f"[seed] Seeded {len(leads_data)} leads.")
    except Exception as e:
        print(f"[seed] Error: {e}")
        db.rollback()
    finally:
        db.close()
