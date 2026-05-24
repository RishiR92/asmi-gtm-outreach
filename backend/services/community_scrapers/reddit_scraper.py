"""
Reddit community discovery using PRAW (Python Reddit API Wrapper).

Searches subreddits by topic keywords, extracts community metrics,
and attempts to identify moderators/community managers.

Requires Reddit API credentials in environment:
  REDDIT_CLIENT_ID
  REDDIT_CLIENT_SECRET
  REDDIT_USER_AGENT (optional, defaults to "AsmiBotScout/1.0")
"""

import os
import asyncio
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

# Reddit API credentials from environment
REDDIT_CLIENT_ID = os.environ.get("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.environ.get("REDDIT_CLIENT_SECRET", "")
REDDIT_USER_AGENT = os.environ.get("REDDIT_USER_AGENT", "AsmiBotScout/1.0")

# Don't initialize PRAW if credentials missing; fail gracefully
_REDDIT = None

def _init_reddit():
    """Lazy-load Reddit API client."""
    global _REDDIT
    if _REDDIT is None:
        if not REDDIT_CLIENT_ID or not REDDIT_CLIENT_SECRET:
            logger.warning(
                "[reddit_scout] Reddit API credentials not configured "
                "(REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET). Reddit scouting disabled."
            )
            return None
        try:
            import praw
            _REDDIT = praw.Reddit(
                client_id=REDDIT_CLIENT_ID,
                client_secret=REDDIT_CLIENT_SECRET,
                user_agent=REDDIT_USER_AGENT,
            )
            logger.info("[reddit_scout] Reddit API client initialized")
        except Exception as e:
            logger.error(f"[reddit_scout] Failed to init Reddit API: {e}")
            return None
    return _REDDIT


async def scout_reddit(topics: Dict) -> List[Dict]:
    """
    Search Reddit for communities matching given topics.

    Args:
        topics: Dict of {topic_name: {keywords, category, relevance_score, description}}

    Returns:
        List of community dicts with metadata:
        {
            "newsletter_name": "subreddit_name",
            "members": 12345,
            "manager_name": "top_moderator",
            "manager_url": "https://...",
            "url": "https://reddit.com/r/...",
            "topic": "topic_name",
            "category": "...",
            "description": "...",
            "activity_level": 0.75,  # 0-1 based on post frequency
            "source": "reddit",
        }
    """
    reddit = _init_reddit()
    if not reddit:
        return []

    communities = []
    seen_subreddits = set()

    try:
        for topic_name, topic_config in topics.items():
            keywords = topic_config.get("keywords", [])

            for keyword in keywords:
                try:
                    # Search subreddits by keyword (aggressive: limit=15 per keyword)
                    # Note: Reddit search is approximate; search results vary
                    for subreddit in reddit.subreddits.search(keyword, limit=15):
                        sub_name = subreddit.display_name.lower()

                        # Skip if already processed
                        if sub_name in seen_subreddits:
                            continue
                        seen_subreddits.add(sub_name)

                        # Filter: only medium-sized active communities (1K-500K)
                        subscribers = getattr(subreddit, "subscribers", 0) or 0
                        if subscribers < 1_000 or subscribers > 500_000:
                            continue

                        # Estimate activity level (simplistic: online/subscribers ratio)
                        online = getattr(subreddit, "accounts_active", 0) or 0
                        activity = min(1.0, online / max(subscribers, 1) * 100)

                        # Get top moderators
                        moderators = list(subreddit.moderator())
                        top_mod_name = moderators[0].name if moderators else None
                        top_mod_url = f"https://reddit.com/u/{top_mod_name}" if top_mod_name else ""

                        # Extract description
                        description = (
                            getattr(subreddit, "public_description", "")
                            or getattr(subreddit, "description", "")
                            or ""
                        )[:200]

                        community = {
                            "newsletter_name": f"r/{sub_name}",
                            "members": subscribers,
                            "manager_name": top_mod_name or f"r/{sub_name} mods",
                            "manager_url": top_mod_url,
                            "manager_email": "",  # Reddit doesn't expose mod emails via API
                            "url": f"https://reddit.com/r/{sub_name}",
                            "topic": topic_name,
                            "category": topic_config.get("category", "Niche"),
                            "description": topic_config.get("description", "") or description,
                            "activity_level": activity,
                            "source": "reddit",
                        }
                        communities.append(community)

                except Exception as e:
                    logger.debug(f"[reddit_scout] Error searching '{keyword}': {e}")
                    continue

    except Exception as e:
        logger.error(f"[reddit_scout] Scouting failed: {e}")
        return []

    logger.info(f"[reddit_scout] Discovered {len(communities)} Reddit communities")
    return communities
