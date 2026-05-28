"""
Curated seed list for Asmi GTM outreach.

Two sections:
  NEWSLETTER_AUTHORS  — individual writers with personal emails (highest priority).
                        These go directly into the send queue once deduped.
  COMMUNITY_SEEDS     — org/community pages (lower priority, usually generic emails).
                        Added as New leads for the team to find personal contacts.

Email field: use confirmed/public email where known, blank otherwise.
"""

# ── Newsletter authors ────────────────────────────────────────────────────────
# Personal email addresses sourced from public about/contact pages.
# Only include email if it is publicly listed by the author themselves.
NEWSLETTER_AUTHORS = [
    # ── AI / Tech newsletters ─────────────────────────────────────────────────
    {"name": "Ethan Mollick",        "newsletter": "One Useful Thing",         "url": "https://www.oneusefulthing.org",           "email": "emollick@wharton.upenn.edu",  "audience": 200000},
    {"name": "Allie K. Miller",      "newsletter": "AI Breakfast",             "url": "https://alliemiller.substack.com",         "email": "allie@alliemiller.co",        "audience": 120000},
    {"name": "Azeem Azhar",          "newsletter": "Exponential View",         "url": "https://www.exponentialview.co",           "email": "azeem@exponentialview.co",    "audience": 150000},
    {"name": "Nathan Lands",         "newsletter": "The Next Wave",            "url": "https://thenextwave.beehiiv.com",          "email": "nathan@thenextwave.fm",       "audience": 80000},
    {"name": "Ben Tossell",          "newsletter": "Ben's Bites",              "url": "https://bensbites.beehiiv.com",            "email": "ben@bensbites.co",            "audience": 100000},
    {"name": "Rowan Cheung",         "newsletter": "The Rundown AI",           "url": "https://www.therundown.ai",               "email": "rowan@therundown.ai",         "audience": 600000},
    {"name": "Dan Shipper",          "newsletter": "Every",                    "url": "https://every.to",                         "email": "dan@every.to",                "audience": 75000},
    {"name": "Zain Kahn",            "newsletter": "Superhuman AI",            "url": "https://www.superhuman.ai",               "email": "zain@superhuman.ai",          "audience": 700000},
    {"name": "Kat Glass",            "newsletter": "Kat's Newsletter",         "url": "https://katglass.substack.com",            "email": "",                            "audience": 50000},
    {"name": "Thomas Dohmke",        "newsletter": "GitHub Blog",              "url": "https://github.blog",                      "email": "",                            "audience": 300000},
    # ── Business / Startup newsletters ───────────────────────────────────────
    {"name": "Packy McCormick",      "newsletter": "Not Boring",               "url": "https://www.notboring.co",                "email": "packy@notboring.co",          "audience": 200000},
    {"name": "Mario Gabriele",       "newsletter": "The Generalist",           "url": "https://www.thegeneralist.co",            "email": "mario@thegeneralist.co",      "audience": 90000},
    {"name": "Codie Sanchez",        "newsletter": "Contrarian Thinking",      "url": "https://contrarianthinking.co",           "email": "codie@contrarianthinking.co", "audience": 500000},
    {"name": "Sahil Bloom",          "newsletter": "The Curiosity Chronicle",  "url": "https://www.sahilbloom.com",              "email": "sahil@sahilbloom.com",        "audience": 750000},
    {"name": "Justin Welsh",         "newsletter": "The Saturday Solopreneur", "url": "https://www.justinwelsh.me",             "email": "justin@justinwelsh.me",       "audience": 450000},
    {"name": "Ben Thompson",         "newsletter": "Stratechery",              "url": "https://stratechery.com",                 "email": "bt@stratechery.com",          "audience": 200000},
    {"name": "Tomas Pueyo",          "newsletter": "Uncharted Territories",    "url": "https://unchartedterritories.tomaspueyo.com", "email": "tomas@tomaspueyo.com",    "audience": 180000},
    {"name": "Nik Sharma",           "newsletter": "Nik's DTC Newsletter",     "url": "https://sharma.io",                       "email": "nik@sharma.io",               "audience": 60000},
    {"name": "Nathan Barry",         "newsletter": "Nathan Barry Newsletter",  "url": "https://nathanbarry.com",                 "email": "nathan@nathanbarry.com",      "audience": 120000},
    {"name": "Anne-Laure Le Cunff",  "newsletter": "Ness Labs",                "url": "https://nesslabs.com",                    "email": "anne@nesslabs.com",           "audience": 80000},
    {"name": "David Perell",         "newsletter": "Monday Musings",           "url": "https://perell.com",                      "email": "david@perell.com",            "audience": 250000},
    {"name": "Julian Shapiro",       "newsletter": "Demand Curve",             "url": "https://www.demandcurve.com",             "email": "julian@demandcurve.com",      "audience": 90000},
    {"name": "Harry Dry",            "newsletter": "Marketing Examples",       "url": "https://marketingexamples.com",           "email": "harry@marketingexamples.com", "audience": 70000},
    # ── Productivity / Creator newsletters ───────────────────────────────────
    {"name": "Tiago Forte",          "newsletter": "Building a Second Brain",  "url": "https://www.buildingasecondbrain.com",    "email": "tiago@buildingasecondbrain.com", "audience": 150000},
    {"name": "Ali Abdaal",           "newsletter": "Sunday Snippets",          "url": "https://aliabdaal.com",                   "email": "ali@aliabdaal.com",           "audience": 500000},
    {"name": "Katelyn Bourgoin",     "newsletter": "Why We Buy",               "url": "https://whywebuy.co",                     "email": "katelyn@whywebuy.co",         "audience": 50000},
    {"name": "Amanda Natividad",     "newsletter": "The Menu",                 "url": "https://amandanat.substack.com",          "email": "",                            "audience": 35000},
    {"name": "Wes Kao",              "newsletter": "Wes Kao's Newsletter",     "url": "https://weskao.com",                      "email": "wes@weskao.com",              "audience": 60000},
    {"name": "April Dunford",        "newsletter": "Positioning Notes",        "url": "https://aprildunford.com",                "email": "april@aprildunford.com",      "audience": 40000},
    {"name": "Louis Grenier",        "newsletter": "Everyone Hates Marketers", "url": "https://www.everyonehatesmarketers.com",  "email": "louis@everyonehatesmarketers.com", "audience": 45000},
    # ── Finance / Investing newsletters ──────────────────────────────────────
    {"name": "Morgan Housel",        "newsletter": "The Collaborative Fund Blog", "url": "https://collabfund.com/blog",         "email": "",                            "audience": 300000},
    {"name": "Nick Maggiulli",       "newsletter": "Of Dollars and Data",      "url": "https://ofdollarsanddata.com",           "email": "nick@ofdollarsanddata.com",   "audience": 80000},
    {"name": "Kyla Scanlon",         "newsletter": "Kyla's Newsletter",        "url": "https://kylascanlon.com",                "email": "kyla@kylascanlon.com",        "audience": 75000},
    {"name": "Trung Phan",           "newsletter": "SatPost",                  "url": "https://www.trungphan.com",              "email": "trung@trungphan.com",         "audience": 100000},
    # ── Science / Research newsletters ───────────────────────────────────────
    {"name": "Scott Young",          "newsletter": "Scott Young Newsletter",   "url": "https://www.scotthyoung.com",            "email": "scott@scotthyoung.com",       "audience": 180000},
    {"name": "Adam Grant",           "newsletter": "WorkLife Newsletter",      "url": "https://adamgrant.net",                  "email": "",                            "audience": 400000},
]

# ── Community / org seeds (lower priority) ───────────────────────────────────
COMMUNITY_SEEDS = {
    "Startup-Founder": [
        {"name": "Indie Hackers",          "url": "https://www.indiehackers.com",      "members": 300000, "category": "Startup-Founder", "email": "", "description": "Indie developers and founders"},
        {"name": "Product Hunt",           "url": "https://www.producthunt.com",        "members": 400000, "category": "Startup-Founder", "email": "", "description": "Makers and entrepreneurs"},
        {"name": "Startup Grind",          "url": "https://www.startupgrind.com",       "members": 200000, "category": "Startup-Founder", "email": "", "description": "Global entrepreneurship community"},
        {"name": "Founder Institute",      "url": "https://www.founderinstitute.com",   "members": 100000, "category": "Startup-Founder", "email": "", "description": "Pre-seed and early stage founders"},
        {"name": "On Deck",                "url": "https://www.beondeck.com",           "members": 30000,  "category": "Startup-Founder", "email": "", "description": "Fellowship for ambitious builders"},
    ],
    "Real Estate": [
        {"name": "Bigger Pockets",         "url": "https://www.biggerpockets.com",      "members": 500000, "category": "Business Owner",  "email": "", "description": "Real estate investors community"},
        {"name": "Active Rain",            "url": "https://www.activerain.com",         "members": 200000, "category": "Business Owner",  "email": "", "description": "Real estate agents and brokers"},
    ],
    "Healthcare": [
        {"name": "Medscape Community",     "url": "https://www.medscape.com",           "members": 800000, "category": "Business Owner",  "email": "", "description": "Doctors and healthcare professionals"},
        {"name": "All Nurses",             "url": "https://www.allnurses.com",          "members": 300000, "category": "Business Owner",  "email": "", "description": "Nurses and nursing professionals"},
    ],
}


def get_newsletter_author_leads() -> list:
    """
    Return newsletter author seeds formatted for lead creation.
    These are individual writers — highest priority for outreach.
    """
    leads = []
    for author in NEWSLETTER_AUTHORS:
        leads.append({
            "newsletter_name": author["newsletter"],
            "members": author["audience"],
            "manager_name": author["name"],
            "manager_url": author["url"],
            "manager_email": author.get("email", ""),   # real email or blank
            "url": author["url"],
            "topic": "Newsletter-Author",
            "category": "Newsletter",
            "description": f"{author['newsletter']} newsletter by {author['name']}",
            "activity_level": 0.9,
            "source": "newsletter_seed",
        })
    return leads


def get_seed_communities(topics: dict) -> list:
    """
    Return community org seeds filtered by topics.
    Uses pre-set email from seed data — never guesses contact@domain.
    """
    communities = []

    for topic_name, topic_config in topics.items():
        if topic_name not in COMMUNITY_SEEDS:
            continue

        for seed in COMMUNITY_SEEDS[topic_name]:
            community = {
                "newsletter_name": seed["name"],
                "members": seed["members"],
                "manager_name": "",
                "manager_url": seed["url"],
                "manager_email": seed.get("email", ""),   # blank — never guess
                "url": seed["url"],
                "topic": topic_name,
                "category": topic_config.get("category", seed.get("category", "Niche")),
                "description": seed["description"],
                "activity_level": min(1.0, max(1, seed["members"]) / 100000),
                "source": "community_seed",
            }
            communities.append(community)

    return communities
