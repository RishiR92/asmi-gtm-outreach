"""
Asmi GTM outreach seed list — built for consumer AI growth (1K → 50K users).

Strategy: newsletters charge $5K/ad for passive reads. Consumer growth in 2026
comes from ACTIVE community gatekeepers who can flip a whole audience at once.

Priority tiers (by expected Asmi users per placement):
  1. Discord / Telegram / WhatsApp admins  — 500–50K members, instant activation
  2. YouTube / TikTok / podcast creators   — 50K–5M reach, review drives signups
  3. Reddit / Facebook community mods      — mass reach, trust signal from mod
  4. College AI / CS club leaders          — viral campus spread, tech-forward
  5. AI tool directories & review sites    — passive but high-intent SEO traffic
  6. Newsletter authors                    — included but de-prioritised vs above
  7. Coworking / accelerator operators     — captive audience of founders/creators

All fields:
  name       — contact person name
  newsletter — platform / community name
  url        — link to community or contact page
  email      — personal email if publicly known, blank otherwise
  audience   — estimated reachable members
  channel    — what type of platform this is
"""

NEWSLETTER_AUTHORS = [

    # ════════════════════════════════════════════════════════════════════════
    # TIER 1 — Discord / Telegram / WhatsApp admins
    # Best channel for consumer AI: engaged tech-forward users, free, instant
    # Approach: "partner post" pinned in #tools or #resources channel
    # ════════════════════════════════════════════════════════════════════════

    # AI / ML Discords
    {"name": "Stability AI Community Admin",  "newsletter": "Stable Diffusion Discord",     "url": "https://discord.gg/stablediffusion",       "email": "",                                    "audience": 250000,  "channel": "discord"},
    {"name": "Midjourney Support Team",       "newsletter": "Midjourney Discord",           "url": "https://discord.gg/midjourney",            "email": "support@midjourney.com",              "audience": 600000,  "channel": "discord"},
    {"name": "Hugging Face Community",        "newsletter": "Hugging Face Discord",         "url": "https://discord.gg/huggingface",           "email": "community@huggingface.co",            "audience": 80000,   "channel": "discord"},
    {"name": "EleutherAI Community Admin",    "newsletter": "EleutherAI Discord",           "url": "https://discord.gg/zBGx3azzUn",            "email": "",                                    "audience": 40000,   "channel": "discord"},
    {"name": "Cursor AI Community",           "newsletter": "Cursor Discord",               "url": "https://discord.gg/cursor-ai",             "email": "team@cursor.sh",                      "audience": 120000,  "channel": "discord"},

    # Productivity / Creator Discords
    {"name": "Notion Community Admin",        "newsletter": "Notion Community Discord",     "url": "https://discord.gg/notion-community",      "email": "",                                    "audience": 150000,  "channel": "discord"},
    {"name": "Obsidian Community Admin",      "newsletter": "Obsidian Discord",             "url": "https://discord.gg/obsidianmd",            "email": "",                                    "audience": 70000,   "channel": "discord"},
    {"name": "Raycast Community",             "newsletter": "Raycast Discord",              "url": "https://discord.gg/raycast",               "email": "support@raycast.com",                 "audience": 30000,   "channel": "discord"},

    # ════════════════════════════════════════════════════════════════════════
    # TIER 2 — YouTube creators (AI tools / productivity)
    # A single honest review video = 10K–500K views, 1–10% convert to signups
    # Approach: direct email, offer exclusive early access / co-branded content
    # ════════════════════════════════════════════════════════════════════════

    {"name": "Kevin Stratvert",               "newsletter": "Kevin Stratvert YouTube",      "url": "https://www.youtube.com/@KevinStratvert", "email": "kevin@kevinsstratvert.com",            "audience": 3000000, "channel": "youtube"},
    {"name": "Jeff Su",                       "newsletter": "Jeff Su YouTube",              "url": "https://www.youtube.com/@JeffSu",         "email": "jeffsu.work@gmail.com",               "audience": 700000,  "channel": "youtube"},
    {"name": "Francesco D'Alessio",           "newsletter": "Keep Productive YouTube",      "url": "https://www.youtube.com/@KeepProductive", "email": "hello@keepproductive.com",            "audience": 500000,  "channel": "youtube"},
    {"name": "Thomas Frank",                  "newsletter": "Thomas Frank YouTube",         "url": "https://www.youtube.com/@ThomasFrank",    "email": "thomas@collegeinfogeek.com",          "audience": 3000000, "channel": "youtube"},
    {"name": "Mike Vardy",                    "newsletter": "Productivityist",              "url": "https://productivityist.com",             "email": "mike@productivityist.com",            "audience": 50000,   "channel": "youtube"},
    {"name": "Tiago Forte",                   "newsletter": "Building a Second Brain",      "url": "https://www.buildingasecondbrain.com",    "email": "tiago@buildingasecondbrain.com",      "audience": 500000,  "channel": "youtube"},
    {"name": "Ali Abdaal",                    "newsletter": "Ali Abdaal YouTube",           "url": "https://www.youtube.com/@aliabdaal",      "email": "ali@aliabdaal.com",                   "audience": 5000000, "channel": "youtube"},
    {"name": "Dan Martell",                   "newsletter": "Dan Martell YouTube",          "url": "https://www.youtube.com/@DanMartell",     "email": "dan@danmartell.com",                  "audience": 1000000, "channel": "youtube"},
    {"name": "Peter Levels (Pieter Levels)",  "newsletter": "Levels.io / Nomad List",       "url": "https://levels.io",                       "email": "pieter@levels.io",                    "audience": 500000,  "channel": "youtube"},
    {"name": "Andrej Karpathy",               "newsletter": "Karpathy YouTube",             "url": "https://www.youtube.com/@AndrejKarpathy", "email": "",                                    "audience": 1000000, "channel": "youtube"},
    {"name": "AI Explained",                  "newsletter": "AI Explained YouTube",         "url": "https://www.youtube.com/@aiexplained",    "email": "",                                    "audience": 600000,  "channel": "youtube"},
    {"name": "David Shapiro",                 "newsletter": "David Shapiro YouTube",        "url": "https://www.youtube.com/@DavidShapiroAI", "email": "",                                    "audience": 400000,  "channel": "youtube"},
    {"name": "Fireship",                      "newsletter": "Fireship YouTube",             "url": "https://www.youtube.com/@Fireship",       "email": "fireship.io@gmail.com",               "audience": 3000000, "channel": "youtube"},
    {"name": "Mariana's Corner",              "newsletter": "Mariana Pereira AI YouTube",   "url": "https://www.youtube.com/@marianascorner", "email": "",                                    "audience": 300000,  "channel": "youtube"},
    {"name": "Skill Leap AI",                 "newsletter": "Skill Leap AI YouTube",        "url": "https://www.youtube.com/@SkillLeapAI",    "email": "hello@skillleap.co",                  "audience": 400000,  "channel": "youtube"},

    # ════════════════════════════════════════════════════════════════════════
    # TIER 3 — Podcast hosts
    # 1 episode mention → 5K–100K listeners, very high trust/conversion
    # Approach: offer to come on as a guest, or provide free access for host
    # ════════════════════════════════════════════════════════════════════════

    {"name": "Shaan Puri",                    "newsletter": "My First Million Podcast",     "url": "https://www.mfmpod.com",                  "email": "shaan@shaanpuri.com",                 "audience": 400000,  "channel": "podcast"},
    {"name": "Sam Parr",                      "newsletter": "My First Million Podcast",     "url": "https://www.mfmpod.com",                  "email": "sam@thehustle.co",                    "audience": 400000,  "channel": "podcast"},
    {"name": "Shane Parrish",                 "newsletter": "The Knowledge Project Podcast","url": "https://fs.blog/knowledge-podcast",       "email": "shane@fs.blog",                       "audience": 300000,  "channel": "podcast"},
    {"name": "Lenny Rachitsky",               "newsletter": "Lenny's Podcast",              "url": "https://www.lennyspodcast.com",           "email": "lenny@lennysnewsletter.com",          "audience": 500000,  "channel": "podcast"},
    {"name": "Harry Stebbings",               "newsletter": "20VC Podcast",                 "url": "https://www.thetwentyminutevc.com",       "email": "harry@thetwentyminutevc.com",         "audience": 300000,  "channel": "podcast"},
    {"name": "Lex Fridman",                   "newsletter": "Lex Fridman Podcast",          "url": "https://lexfridman.com/podcast",          "email": "lex@lexfridman.com",                  "audience": 3000000, "channel": "podcast"},
    {"name": "Tim Ferriss",                   "newsletter": "The Tim Ferriss Show",         "url": "https://tim.blog/podcast",                "email": "tim@fourhourworkweek.com",             "audience": 1000000, "channel": "podcast"},
    {"name": "Andrew Huberman",               "newsletter": "Huberman Lab Podcast",         "url": "https://hubermanlab.com",                 "email": "",                                    "audience": 3000000, "channel": "podcast"},
    {"name": "Noah Kagan",                    "newsletter": "Noah Kagan Presents",          "url": "https://noahkagan.com",                   "email": "noah@appsumo.com",                    "audience": 400000,  "channel": "podcast"},
    {"name": "Greg Isenberg",                 "newsletter": "Greg Isenberg Podcast",        "url": "https://www.gregisenberg.com",            "email": "greg@gregisenberg.com",               "audience": 200000,  "channel": "podcast"},

    # ════════════════════════════════════════════════════════════════════════
    # TIER 4 — Reddit community moderators
    # Subreddit mod post / sticky = 100K–10M reach, 0.1-1% convert
    # Approach: offer free early access + community-specific feature, ask for mod sticky
    # ════════════════════════════════════════════════════════════════════════

    {"name": "r/ChatGPT Moderators",          "newsletter": "r/ChatGPT (Reddit)",           "url": "https://reddit.com/r/ChatGPT",            "email": "",                                    "audience": 6000000, "channel": "reddit"},
    {"name": "r/artificial Moderators",       "newsletter": "r/artificial (Reddit)",        "url": "https://reddit.com/r/artificial",         "email": "",                                    "audience": 900000,  "channel": "reddit"},
    {"name": "r/productivity Moderators",     "newsletter": "r/productivity (Reddit)",      "url": "https://reddit.com/r/productivity",       "email": "",                                    "audience": 2500000, "channel": "reddit"},
    {"name": "r/MachineLearning Moderators",  "newsletter": "r/MachineLearning (Reddit)",   "url": "https://reddit.com/r/MachineLearning",    "email": "",                                    "audience": 3000000, "channel": "reddit"},
    {"name": "r/LocalLLaMA Moderators",       "newsletter": "r/LocalLLaMA (Reddit)",        "url": "https://reddit.com/r/LocalLLaMA",         "email": "",                                    "audience": 400000,  "channel": "reddit"},
    {"name": "r/Entrepreneur Moderators",     "newsletter": "r/Entrepreneur (Reddit)",      "url": "https://reddit.com/r/Entrepreneur",       "email": "",                                    "audience": 1200000, "channel": "reddit"},
    {"name": "r/LifeProTips Moderators",      "newsletter": "r/LifeProTips (Reddit)",       "url": "https://reddit.com/r/LifeProTips",        "email": "",                                    "audience": 22000000,"channel": "reddit"},

    # ════════════════════════════════════════════════════════════════════════
    # TIER 5 — Facebook Group admins
    # Huge overlooked channel. "ChatGPT Users" groups have 1M+ members.
    # Admin post reaches everyone. Free, immediate.
    # ════════════════════════════════════════════════════════════════════════

    {"name": "ChatGPT Users Facebook Admin",  "newsletter": "ChatGPT Users (FB Group)",     "url": "https://www.facebook.com/groups/chatgptusers", "email": "",                               "audience": 1200000, "channel": "facebook"},
    {"name": "AI Tools Facebook Admin",       "newsletter": "AI Tools & Resources (FB)",    "url": "https://www.facebook.com/groups/aitools", "email": "",                                    "audience": 600000,  "channel": "facebook"},
    {"name": "Productivity Hackers Admin",    "newsletter": "Productivity Hackers (FB)",    "url": "https://www.facebook.com/groups/productivityhackers", "email": "",                        "audience": 500000,  "channel": "facebook"},
    {"name": "Side Hustle Nation Admin",      "newsletter": "Side Hustle Nation (FB)",      "url": "https://www.facebook.com/groups/sidehustlenation", "email": "nick@sidehustlenation.com",  "audience": 400000,  "channel": "facebook"},
    {"name": "Female Founder Collective",     "newsletter": "Female Founder Collective",    "url": "https://femalefoundercollective.com",      "email": "hello@femalefoundercollective.com",  "audience": 100000,  "channel": "facebook"},

    # ════════════════════════════════════════════════════════════════════════
    # TIER 6 — AI tool directories & Product Hunt (high-intent traffic)
    # People visiting these are actively looking for new tools — conversion 5-20%
    # ════════════════════════════════════════════════════════════════════════

    {"name": "Noah Kagan (AppSumo)",          "newsletter": "AppSumo",                      "url": "https://appsumo.com",                     "email": "partnerships@appsumo.com",            "audience": 1000000, "channel": "directory"},
    {"name": "Ryan Hoover",                   "newsletter": "Product Hunt",                 "url": "https://www.producthunt.com",             "email": "ryan@producthunt.com",                "audience": 700000,  "channel": "directory"},
    {"name": "Ben Tossell",                   "newsletter": "Ben's Bites",                  "url": "https://bensbites.beehiiv.com",           "email": "ben@bensbites.co",                    "audience": 100000,  "channel": "newsletter"},
    {"name": "There's An AI For That",        "newsletter": "There's An AI For That",       "url": "https://theresanaiforthat.com",           "email": "andy@theresanaiforthat.com",          "audience": 500000,  "channel": "directory"},
    {"name": "AI Tool Report Team",           "newsletter": "AI Tool Report",               "url": "https://www.aitoolreport.com",            "email": "contact@aitoolreport.com",            "audience": 300000,  "channel": "directory"},
    {"name": "Rowan Cheung",                  "newsletter": "The Rundown AI",               "url": "https://www.therundown.ai",               "email": "rowan@therundown.ai",                 "audience": 600000,  "channel": "newsletter"},
    {"name": "Zain Kahn",                     "newsletter": "Superhuman AI",                "url": "https://www.superhuman.ai",               "email": "zain@superhuman.ai",                  "audience": 700000,  "channel": "newsletter"},

    # ════════════════════════════════════════════════════════════════════════
    # TIER 7 — College AI / CS club leaders
    # Each club = 100–2000 highly engaged tech students who share everything.
    # Viral campus spread — one club announcement hits the whole school.
    # ════════════════════════════════════════════════════════════════════════

    {"name": "MIT AI Club President",         "newsletter": "MIT AI Club",                  "url": "https://ai.mit.edu",                      "email": "ai-club@mit.edu",                     "audience": 5000,    "channel": "university"},
    {"name": "Stanford AI Club (SAIL)",       "newsletter": "Stanford AI Club",             "url": "https://www.stanfordaiclubb.com",         "email": "sail@stanford.edu",                   "audience": 8000,    "channel": "university"},
    {"name": "CMU AI Club",                   "newsletter": "CMU AI Club",                  "url": "https://www.cmuai.club",                  "email": "cmuaiclub@gmail.com",                 "audience": 4000,    "channel": "university"},
    {"name": "Berkeley AI Student Group",     "newsletter": "Berkeley AI (BAIR)",           "url": "https://bair.berkeley.edu",               "email": "bair@berkeley.edu",                   "audience": 6000,    "channel": "university"},
    {"name": "Harvard Applied Math AI",       "newsletter": "Harvard AI Club",              "url": "https://harvardai.club",                  "email": "harvardaiclub@gmail.com",             "audience": 3000,    "channel": "university"},
    {"name": "Georgia Tech AI Club",          "newsletter": "Georgia Tech AI Club",         "url": "https://www.gtai.club",                   "email": "gtai@gatech.edu",                     "audience": 3000,    "channel": "university"},
    {"name": "UT Austin AI/ML Club",          "newsletter": "UT Austin ML",                 "url": "https://utaiaml.com",                     "email": "utaiaml@gmail.com",                   "audience": 2000,    "channel": "university"},
    {"name": "UIUC CS AI Club",               "newsletter": "UIUC AI Society",              "url": "https://acm.illinois.edu",                "email": "acm@acm.illinois.edu",                "audience": 3000,    "channel": "university"},
    {"name": "Waterloo AI Student Assoc",     "newsletter": "Waterloo AI",                  "url": "https://uwai.ca",                         "email": "ai@uwaterloo.ca",                     "audience": 2000,    "channel": "university"},
    {"name": "Columbia Data Science Club",    "newsletter": "Columbia DSI",                 "url": "https://www.columbia.edu/dsi",            "email": "",                                    "audience": 2000,    "channel": "university"},

    # ════════════════════════════════════════════════════════════════════════
    # TIER 8 — Accelerators / coworking operators
    # Each has 50–500 startup founders as a captive audience.
    # Operators do weekly emails to all members — one placement = mass reach.
    # ════════════════════════════════════════════════════════════════════════

    {"name": "YC Group Partners",             "newsletter": "Y Combinator",                 "url": "https://www.ycombinator.com",             "email": "partners@ycombinator.com",            "audience": 50000,   "channel": "accelerator"},
    {"name": "Techstars Community",           "newsletter": "Techstars",                    "url": "https://www.techstars.com",               "email": "community@techstars.com",             "audience": 20000,   "channel": "accelerator"},
    {"name": "Antler Community Team",         "newsletter": "Antler",                       "url": "https://www.antler.co",                   "email": "community@antler.co",                 "audience": 10000,   "channel": "accelerator"},
    {"name": "On Deck Community",             "newsletter": "On Deck (beondeck)",           "url": "https://www.beondeck.com",                "email": "hello@beondeck.com",                  "audience": 30000,   "channel": "accelerator"},
    {"name": "Replit Community Team",         "newsletter": "Replit Community",             "url": "https://replit.com",                      "email": "community@replit.com",                "audience": 300000,  "channel": "accelerator"},

    # ════════════════════════════════════════════════════════════════════════
    # TIER 9 — Newsletter authors (kept but de-prioritised vs above)
    # Still valuable but expensive for what you get vs community channels above
    # ════════════════════════════════════════════════════════════════════════

    {"name": "Packy McCormick",               "newsletter": "Not Boring",                   "url": "https://www.notboring.co",                "email": "packy@notboring.co",                  "audience": 200000,  "channel": "newsletter"},
    {"name": "Mario Gabriele",                "newsletter": "The Generalist",               "url": "https://www.thegeneralist.co",            "email": "mario@thegeneralist.co",              "audience": 90000,   "channel": "newsletter"},
    {"name": "Codie Sanchez",                 "newsletter": "Contrarian Thinking",          "url": "https://contrarianthinking.co",           "email": "codie@contrarianthinking.co",         "audience": 500000,  "channel": "newsletter"},
    {"name": "Sahil Bloom",                   "newsletter": "The Curiosity Chronicle",      "url": "https://www.sahilbloom.com",              "email": "sahil@sahilbloom.com",                "audience": 750000,  "channel": "newsletter"},
    {"name": "Justin Welsh",                  "newsletter": "The Saturday Solopreneur",     "url": "https://www.justinwelsh.me",             "email": "justin@justinwelsh.me",               "audience": 450000,  "channel": "newsletter"},
    {"name": "Ben Thompson",                  "newsletter": "Stratechery",                  "url": "https://stratechery.com",                "email": "bt@stratechery.com",                  "audience": 200000,  "channel": "newsletter"},
    {"name": "David Perell",                  "newsletter": "Monday Musings",               "url": "https://perell.com",                     "email": "david@perell.com",                    "audience": 250000,  "channel": "newsletter"},
    {"name": "Ethan Mollick",                 "newsletter": "One Useful Thing",             "url": "https://www.oneusefulthing.org",          "email": "emollick@wharton.upenn.edu",          "audience": 200000,  "channel": "newsletter"},
    {"name": "Azeem Azhar",                   "newsletter": "Exponential View",             "url": "https://www.exponentialview.co",          "email": "azeem@exponentialview.co",            "audience": 150000,  "channel": "newsletter"},
    {"name": "Nathan Barry",                  "newsletter": "Nathan Barry Newsletter",      "url": "https://nathanbarry.com",                "email": "nathan@nathanbarry.com",              "audience": 120000,  "channel": "newsletter"},
    {"name": "Anne-Laure Le Cunff",           "newsletter": "Ness Labs",                   "url": "https://nesslabs.com",                   "email": "anne@nesslabs.com",                   "audience": 80000,   "channel": "newsletter"},
    {"name": "Kyla Scanlon",                  "newsletter": "Kyla's Newsletter",           "url": "https://kylascanlon.com",                "email": "kyla@kylascanlon.com",                "audience": 75000,   "channel": "newsletter"},
    {"name": "Nik Sharma",                    "newsletter": "Nik's DTC Newsletter",        "url": "https://sharma.io",                      "email": "nik@sharma.io",                       "audience": 60000,   "channel": "newsletter"},
    {"name": "Harry Dry",                     "newsletter": "Marketing Examples",           "url": "https://marketingexamples.com",          "email": "harry@marketingexamples.com",         "audience": 70000,   "channel": "newsletter"},
    {"name": "Nick Maggiulli",                "newsletter": "Of Dollars and Data",         "url": "https://ofdollarsanddata.com",           "email": "nick@ofdollarsanddata.com",           "audience": 80000,   "channel": "newsletter"},
    {"name": "Allie K. Miller",               "newsletter": "AI Breakfast",                "url": "https://alliemiller.substack.com",       "email": "allie@alliemiller.co",                "audience": 120000,  "channel": "newsletter"},
    {"name": "Nathan Lands",                  "newsletter": "The Next Wave",               "url": "https://thenextwave.beehiiv.com",        "email": "nathan@thenextwave.fm",               "audience": 80000,   "channel": "newsletter"},
    {"name": "Dan Shipper",                   "newsletter": "Every",                       "url": "https://every.to",                       "email": "dan@every.to",                        "audience": 75000,   "channel": "newsletter"},
    {"name": "Trung Phan",                    "newsletter": "SatPost",                     "url": "https://www.trungphan.com",              "email": "trung@trungphan.com",                 "audience": 100000,  "channel": "newsletter"},
    {"name": "Katelyn Bourgoin",              "newsletter": "Why We Buy",                  "url": "https://whywebuy.co",                    "email": "katelyn@whywebuy.co",                 "audience": 50000,   "channel": "newsletter"},
    {"name": "Scott Young",                   "newsletter": "Scott Young Newsletter",      "url": "https://www.scotthyoung.com",            "email": "scott@scotthyoung.com",               "audience": 180000,  "channel": "newsletter"},
    {"name": "Wes Kao",                       "newsletter": "Wes Kao's Newsletter",        "url": "https://weskao.com",                     "email": "wes@weskao.com",                      "audience": 60000,   "channel": "newsletter"},
    {"name": "Greg Isenberg",                 "newsletter": "Greg Isenberg Newsletter",    "url": "https://www.gregisenberg.com",           "email": "greg@gregisenberg.com",               "audience": 150000,  "channel": "newsletter"},
    {"name": "Julian Shapiro",                "newsletter": "Demand Curve",                "url": "https://www.demandcurve.com",            "email": "julian@demandcurve.com",              "audience": 90000,   "channel": "newsletter"},
]

# Community seeds kept for fallback — low priority
COMMUNITY_SEEDS = {
    "Startup-Founder": [
        {"name": "Indie Hackers",   "url": "https://www.indiehackers.com", "members": 300000, "category": "Startup-Founder", "email": "", "description": "Indie developers and founders"},
        {"name": "Product Hunt",    "url": "https://www.producthunt.com",  "members": 400000, "category": "Startup-Founder", "email": "", "description": "Makers and entrepreneurs"},
        {"name": "Startup Grind",   "url": "https://www.startupgrind.com", "members": 200000, "category": "Startup-Founder", "email": "", "description": "Global entrepreneurship community"},
    ],
}


def get_newsletter_author_leads() -> list:
    """
    Return all seed leads (newsletter authors, Discord admins, YouTubers,
    podcast hosts, Reddit mods, FB admins, university clubs, accelerators).
    All formatted for lead creation.
    """
    leads = []
    for author in NEWSLETTER_AUTHORS:
        leads.append({
            "newsletter_name": author["newsletter"],
            "members": author["audience"],
            "manager_name": author["name"],
            "manager_url": author["url"],
            "manager_email": author.get("email", ""),
            "url": author["url"],
            "topic": author.get("channel", "newsletter"),
            "category": _channel_to_category(author.get("channel", "newsletter")),
            "description": f"{author['newsletter']} | {author.get('channel','newsletter')} | ~{_fmt(author['audience'])} reach",
            "activity_level": 0.9,
            "source": "newsletter_seed",
        })
    return leads


def _channel_to_category(channel: str) -> str:
    return {
        "discord":     "Community",
        "youtube":     "Creator",
        "podcast":     "Creator",
        "reddit":      "Community",
        "facebook":    "Community",
        "directory":   "Directory",
        "university":  "University",
        "accelerator": "Accelerator",
        "newsletter":  "Newsletter",
    }.get(channel, "Other")


def _fmt(n: int) -> str:
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
    if n >= 1_000:     return f"{n//1000}K"
    return str(n)


def get_seed_communities(topics: dict) -> list:
    """Community org seeds (fallback) — uses pre-set email, never guesses."""
    communities = []
    for topic_name, topic_config in topics.items():
        if topic_name not in COMMUNITY_SEEDS:
            continue
        for seed in COMMUNITY_SEEDS[topic_name]:
            communities.append({
                "newsletter_name": seed["name"],
                "members": seed["members"],
                "manager_name": "",
                "manager_url": seed["url"],
                "manager_email": seed.get("email", ""),
                "url": seed["url"],
                "topic": topic_name,
                "category": topic_config.get("category", seed.get("category", "Niche")),
                "description": seed["description"],
                "activity_level": min(1.0, max(1, seed["members"]) / 100000),
                "source": "community_seed",
            })
    return communities
