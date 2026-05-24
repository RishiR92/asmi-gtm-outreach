from database import SessionLocal
from models import Template, Lead, AppSettings
import os


def seed():
    db = SessionLocal()
    try:
        # Only seed if tables are empty
        if db.query(Lead).count() > 0:
            db.close()
            return

        print("Seeding database...")

        # Seed AppSettings
        if db.query(AppSettings).count() == 0:
            settings = AppSettings(
                id=1,
                gmail_email=os.environ.get("GMAIL_EMAIL", ""),
                gmail_app_password=os.environ.get("GMAIL_APP_PASSWORD", ""),
                sender_name=os.environ.get("SENDER_NAME", "Rishi"),
                daily_send_limit=20,
                followup1_days=4,
                followup2_days=9,
                send_hours_start=9,
                send_hours_end=17,
                timezone="Asia/Kolkata",
                imap_enabled=False,
            )
            db.add(settings)
            db.commit()

        # Seed single canonical template
        if db.query(Template).count() == 0:
            tmpl = Template(
                name="Asmi Outreach",
                category="AI Tools",
                subject_a="2x founder + DeepMind/FAIR team building AI for {{newsletter}} audience",
                subject_b="AI co-founder team (DeepMind, FAIR) + early traction",
                body="Hey {{name}},\n\nRishi here — 2x founder, scaled to 600M+ consumers, ~$100M raised from SoftBank, DoorDash & Zoom founders.\n\nI'm now building Asmi with Satwik (CMU PhD, FAIR, DeepMind, 40+ highly cited papers) + team of AI researchers from DeepMind, FAIR, Google, CMU. Backed by Suno AI CPO/Snap CPO.\n\nAsmi: AI that handles personal chores in the physical world. 2,000+ real-world tasks executed in 3.5 weeks, 40%+ day-7 retention, $0 acquisition (growth from Asmi calling users' networks).\n\n{{custom_line}}\n\nThink this fits perfectly with {{newsletter}}. Would love to explore an engagement activity.\n\nBest,\nRishi",
                followup1_subject="Quick follow-up — Asmi for {{newsletter}}",
                followup1_body="Hey {{name}},\n\nJust circling back on Asmi. The traction (40%+ retention, organic growth through our AI calls) is genuinely noteworthy.\n\nWould be great to chat when you have 15 min.\n\nBest,\nRishi",
                followup2_subject="Last message",
                followup2_body="Hey {{name}},\n\nFinal follow-up. If timing isn't right now, I'd love to reconnect when it is. Building something I think your audience will care about.\n\nBest,\nRishi",
            )
            db.add(tmpl)
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
        print(f"Seeded {len(leads_data)} leads and {len(templates_data)} templates.")
    except Exception as e:
        print(f"Seed error: {e}")
        db.rollback()
    finally:
        db.close()
