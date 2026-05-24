"""
Google Search community discovery via SerpAPI or DuckDuckGo.

Searches for communities matching keywords like "parenting community",
"real estate slack", "founder discord", etc. and extracts URLs + metadata.

Uses SerpAPI (free tier: 100/month) if SERPAPI_KEY is set, else falls back
to DuckDuckGo web scraping (no API needed, slower but free).
"""

import asyncio
import logging
import os
import requests
from typing import List, Dict
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

SERPAPI_KEY = os.environ.get("SERPAPI_KEY", "")


async def scout_google(topics: Dict) -> List[Dict]:
    """
    Search Google for communities matching topics.

    Searches for keywords like "[topic] community", "[topic] slack",
    "[topic] discord" to find communities.

    Returns list of community dicts with URLs and metadata.
    """
    communities = []
    seen_urls = set()

    search_patterns = [
        "{keyword} community",
        "{keyword} slack community",
        "{keyword} discord server",
        "{keyword} group slack",
        "{keyword} facebook group",
    ]

    try:
        for topic_name, topic_config in topics.items():
            keywords = topic_config.get("keywords", [])

            for keyword in keywords[:2]:  # limit to 2 keywords per topic
                for pattern in search_patterns:
                    search_query = pattern.format(keyword=keyword)

                    try:
                        results = await _search_google(search_query)

                        for result in results[:5]:  # top 5 results per search
                            url = result.get("url", "")
                            title = result.get("title", "")

                            if not url or url in seen_urls:
                                continue
                            seen_urls.add(url)

                            domain = urlparse(url).netloc.lower()

                            # Extract community name from title/URL
                            community_name = title or domain
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
                                "description": f"Found via search: {search_query}",
                                "activity_level": 0.5,  # unknown
                                "source": "google_search",
                            }
                            communities.append(community)

                    except Exception as e:
                        logger.debug(f"[google_scout] Error searching '{search_query}': {e}")
                        continue

    except Exception as e:
        logger.error(f"[google_scout] Scouting failed: {e}")
        return []

    logger.info(f"[google_scout] Discovered {len(communities)} communities via search")
    return communities


async def _search_google(query: str) -> List[Dict]:
    """
    Execute a search query.

    Uses SerpAPI if configured, else falls back to DuckDuckGo scraping.
    """
    if SERPAPI_KEY:
        return await _search_serpapi(query)
    else:
        return await _search_duckduckgo(query)


async def _search_serpapi(query: str) -> List[Dict]:
    """Search via SerpAPI (free tier: 100 searches/month)."""
    try:
        params = {
            "q": query,
            "api_key": SERPAPI_KEY,
            "engine": "google",
            "num": 10,
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
        return results
    except Exception as e:
        logger.debug(f"[serpapi] Search failed: {e}")
        return []


async def _search_duckduckgo(query: str) -> List[Dict]:
    """
    Fallback: search via DuckDuckGo (free, no API key needed).

    DuckDuckGo is more lenient than Google with scraping.
    """
    try:
        # DuckDuckGo API endpoint (simple JSON API)
        params = {"q": query, "format": "json"}
        resp = requests.get("https://api.duckduckgo.com/", params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        results = []

        # DuckDuckGo returns results in different formats
        # Try RelatedTopics first
        for item in data.get("RelatedTopics", []):
            if "FirstURL" in item:
                results.append({
                    "url": item["FirstURL"],
                    "title": item.get("Text", "").split(" - ")[0] if item.get("Text") else "",
                    "snippet": item.get("Text", ""),
                })

        return results[:10]
    except Exception as e:
        logger.debug(f"[duckduckgo] Search failed: {e}")
        return []
