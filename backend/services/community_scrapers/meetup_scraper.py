"""
Meetup.com community discovery.

Searches Meetup for groups matching keywords, extracts organizer info,
group size, and activity level.

Meetup has public JSON feeds for groups (no auth required for basic data).
"""

import logging
import requests
from typing import List, Dict

logger = logging.getLogger(__name__)

# Meetup API (free tier, no auth required for basic queries)
MEETUP_BASE = "https://api.meetup.com"


def scout_meetup_sync(topics: Dict) -> List[Dict]:
    """
    Search Meetup.com for groups matching topics.

    Returns list of community dicts with metadata.
    """
    communities = []
    seen_groups = set()

    try:
        for topic_name, topic_config in topics.items():
            keywords = topic_config.get("keywords", [])

            for keyword in keywords[:3]:  # limit to 3 keywords per topic
                try:
                    # Meetup API: search groups by keyword
                    # Note: Meetup's free API has rate limits; use sparingly
                    params = {
                        "search": keyword,
                        "country": "us",  # focus on US for now
                        "order": "members",
                        "page": 20,
                    }

                    resp = requests.get(
                        f"{MEETUP_BASE}/find/groups",
                        params=params,
                        timeout=10,
                    )
                    resp.raise_for_status()
                    groups = resp.json()

                    if not isinstance(groups, list):
                        continue

                    for group in groups:
                        group_name = group.get("name", "")
                        group_id = group.get("id")

                        # Skip if already processed
                        if group_id in seen_groups:
                            continue
                        seen_groups.add(group_id)

                        # Filter: 50+ members (more permissive to find enough communities)
                        members = group.get("members", 0)
                        if members < 50 or members > 100_000:
                            continue

                        # Organizer info
                        organizer = group.get("organizer", {})
                        organizer_name = organizer.get("name", "")

                        # Group URL
                        group_url = group.get("link", "")

                        # Description
                        description = group.get("description", "")[:200]

                        community = {
                            "newsletter_name": f"Meetup: {group_name}",
                            "members": members,
                            "manager_name": organizer_name,
                            "manager_url": f"https://meetup.com{group.get('urlname', '')}",
                            "manager_email": "",  # Meetup doesn't expose emails via API
                            "url": group_url,
                            "topic": topic_name,
                            "category": topic_config.get("category", "Niche"),
                            "description": topic_config.get("description", "") or description,
                            "activity_level": min(1.0, group.get("members", 0) / 1000),  # rough estimate
                            "source": "meetup",
                        }
                        communities.append(community)

                except Exception as e:
                    logger.debug(f"[meetup_scout] Error searching '{keyword}': {e}")
                    continue

    except Exception as e:
        logger.error(f"[meetup_scout] Scouting failed: {e}")
        return []

    logger.info(f"[meetup_scout] Discovered {len(communities)} Meetup groups")
    return communities
