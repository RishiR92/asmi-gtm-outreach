"""
Google Search community discovery via SerpAPI with email extraction.

Searches for communities matching keywords and extracts:
- Email addresses from snippets and content
- Generic email patterns (contact@, hello@, info@, etc.)

Uses SerpAPI (free tier) for reliable Google Search results.
"""

import logging
import os
import requests
import re
from typing import List, Dict
from urllib.parse import urlparse
import time

logger = logging.getLogger(__name__)

# Common generic email patterns to try
GENERIC_EMAIL_PATTERNS = [
    "contact",
    "hello",
    "info",
    "hello",
    "support",
    "team",
    "manager",
    "founder",
    "lead",
    "admin",
]


def get_serpapi_key():
    """Get SERPAPI_KEY from environment at runtime (not at import time)."""
    return os.environ.get("SERPAPI_KEY", "")


def extract_emails(text: str) -> List[str]:
    """Extract email addresses from text using regex."""
    if not text:
        return []

    # Email regex pattern
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)

    # Remove duplicates and invalid patterns
    valid_emails = []
    for email in set(emails):
        # Filter out obviously fake/test emails
        if not any(x in email.lower() for x in ['example', 'test', 'fake', 'noreply']):
            valid_emails.append(email)

    return valid_emails


def get_generic_emails(domain: str) -> List[str]:
    """Generate common generic email addresses for a domain."""
    if not domain:
        return []

    # Remove www. prefix if present
    domain = domain.replace('www.', '')

    emails = []
    for pattern in GENERIC_EMAIL_PATTERNS:
        emails.append(f"{pattern}@{domain}")

    return emails


def scout_google_sync(topics: Dict) -> List[Dict]:
    """
    Search Google for communities matching topics.

    Extracts both specific email addresses and generates generic patterns.

    Returns list of community dicts with emails and metadata.
    """
    communities = []
    seen_urls = set()

    # Optimized search patterns for fast discovery
    search_patterns = [
        "{keyword} community",
        "{keyword} professional community",
    ]

    serpapi_key = get_serpapi_key()
    if not serpapi_key:
        logger.warning("[google_scout] SERPAPI_KEY not configured - skipping web search")
        return []

    try:
        for topic_name, topic_config in topics.items():
            keywords = topic_config.get("keywords", [])

            # Use fewer keywords for faster discovery
            for keyword in keywords[:2]:
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

                                # Extract email from snippet/title
                                content_for_email = f"{title} {snippet}"
                                specific_emails = extract_emails(content_for_email)
                                preferred_email = specific_emails[0] if specific_emails else None

                                # If no specific email found, generate generic patterns
                                if not preferred_email:
                                    domain = urlparse(url).netloc
                                    generic_emails = get_generic_emails(domain)
                                    # Use the most common one (contact@)
                                    preferred_email = generic_emails[0] if generic_emails else ""

                                community = {
                                    "newsletter_name": community_name,
                                    "members": 0,  # unknown from search results
                                    "manager_name": "",
                                    "manager_url": url,
                                    "manager_email": preferred_email,  # Email found or generic pattern
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
    serpapi_key = get_serpapi_key()
    if not serpapi_key:
        logger.warning("[serpapi] No API key configured")
        return []

    try:
        params = {
            "q": query,
            "api_key": serpapi_key,
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
