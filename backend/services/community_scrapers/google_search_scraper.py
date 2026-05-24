"""
Google Search community discovery via SerpAPI.

Searches for communities matching keywords like "parenting community",
"real estate slack", "founder discord", etc. and extracts URLs + metadata.

Uses SerpAPI (free tier: 100/month) for reliable Google Search results.
"""

import logging
import os
import requests
from typing import List, Dict
from urllib.parse import urlparse
import time

logger = logging.getLogger(__name__)

SERPAPI_KEY = os.environ.get("SERPAPI_KEY", "")


def scout_google_sync(topics: Dict) -> List[Dict]:
    """
    Search Google for communities matching topics.

    Searches for keywords like "[topic] community", "[topic] slack",
    "[topic] discord" to find communities.

    Returns list of community dicts with URLs and metadata.
    """
    communities = []
    seen_urls = set()

    # Expanded search patterns to find more communities
    search_patterns = [
        "{keyword} community",
        "{keyword} community online",
        "{keyword} community groups",
        "{keyword} professional community",
        "{keyword} network forum",
        "{keyword} slack channel",
        "{keyword} discord server",
        "{keyword} facebook group",
        "{keyword} meetup group",
        "{keyword} leaders network",
    ]

    if not SERPAPI_KEY:
        logger.warning("[google_scout] SERPAPI_KEY not configured - skipping web search")
        return []

    try:
        for topic_name, topic_config in topics.items():
            keywords = topic_config.get("keywords", [])

            # Search more keywords when we have API access
            for keyword in keywords[:3]:
                for pattern in search_patterns:
                    search_query = pattern.format(keyword=keyword)

                    try:
                        logger.debug(f"[google_scout] Searching: {search_query}")
                        results = _search_serpapi(search_query)

                        # Take more results when available
                        for result in results[:8]:
                            url = result.get("url", "")
                            title = result.get("title", "")
                            snippet = result.get("snippet", "")

                            if not url or url in seen_urls:
                                continue

                            # Filter out obvious non-community URLs
                            if _is_community_url(url, title, snippet):
                                seen_urls.add(url)

                                # Extract community name from title
                                community_name = title or urlparse(url).netloc
                                if len(community_name) > 100:
                                    community_name = community_name[:100]

                                community = {
                                    "newsletter_name": community_name,
                                    "members": 0,  # unknown from search results
                                    "manager_name": "",
                                    "manager_url": url,
                                    "manager_email": "",
                                    "url": url,
                                    "topic": topic_name,
                                    "category": topic_config.get("category", "Niche"),
                                    "description": f"{snippet[:200] if snippet else title}",
                                    "activity_level": 0.6,  # moderate estimate for search results
                                    "source": "google_search",
                                }
                                communities.append(community)

                    except Exception as e:
                        logger.debug(f"[google_scout] Error searching '{search_query}': {e}")
                        continue

                    # Be respectful with rate limiting
                    time.sleep(0.5)

    except Exception as e:
        logger.error(f"[google_scout] Scouting failed: {e}")
        return []

    logger.info(f"[google_scout] Discovered {len(communities)} communities via search")
    return communities


def _is_community_url(url: str, title: str, snippet: str) -> bool:
    """
    Filter URLs to keep only community-related results.
    """
    # Convert to lowercase for matching
    url_lower = url.lower()
    title_lower = title.lower()
    snippet_lower = snippet.lower()

    # Exclude common noise
    exclude_patterns = [
        "reddit.com",  # Reddit is too noisy
        "twitter.com",
        "facebook.com/groups",  # Too many unrelated Facebook groups
        "youtube.com",
        "amazon.com",
        "ebay.com",
        "wikipedia.org",
        "ads.google",
        "support.google",
        "shop.",
        "store.",
        "buy.",
    ]

    for pattern in exclude_patterns:
        if pattern in url_lower:
            return False

    # Include community signals
    include_keywords = [
        "community",
        "group",
        "forum",
        "network",
        "association",
        "organization",
        "meetup",
        "professional",
        "members",
        "leaders",
        "newsletter",
        "slack",
        "discord",
    ]

    content = (title_lower + " " + snippet_lower).lower()
    return any(keyword in content for keyword in include_keywords)


def _search_serpapi(query: str) -> List[Dict]:
    """Search via SerpAPI."""
    try:
        params = {
            "q": query,
            "api_key": SERPAPI_KEY,
            "engine": "google",
            "num": 10,
            "gl": "us",  # Focus on US results
        }
        resp = requests.get("https://serpapi.com/search", params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        results = []
        for item in data.get("organic_results", []):
            results.append({
                "url": item.get("link"),
                "title": item.get("title"),
                "snippet": item.get("snippet"),
            })

        logger.debug(f"[serpapi] Got {len(results)} results for query")
        return results
    except Exception as e:
        logger.debug(f"[serpapi] Search failed: {e}")
        return []
