"""
Fetcher Agent
Retrieves post metrics (views, likes, replies, reposts) from the Threads API.
"""

import logging
from typing import Any

import requests

from config import settings

logger = logging.getLogger(__name__)

THREADS_API_BASE = "https://graph.threads.net/v1.0"

# Insight metrics supported by the Threads API
INSIGHT_METRICS = ["views", "likes", "replies", "reposts", "quotes"]


class FetcherAgent:
    """
    Agent 5: Fetcher
    Fetches engagement data for posts using the Threads Insights API.
    """

    def __init__(self, access_token: str | None = None, user_id: str | None = None) -> None:
        self._token = access_token or settings.threads_access_token
        self._user_id = user_id or settings.threads_user_id

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def fetch_recent_posts(self, limit: int = 10) -> list[dict[str, Any]]:
        """
        Fetch recent posts and their insight metrics.

        Args:
            limit: Number of recent posts to retrieve (max 100).

        Returns:
            List of post dicts with keys 'id', 'text', 'timestamp',
            'views', 'likes', 'replies', 'reposts', 'quotes'.
        """
        posts = self._get_threads(limit)
        results: list[dict[str, Any]] = []
        for post in posts:
            metrics = self._get_insights(post["id"])
            results.append(
                {
                    "id": post["id"],
                    "text": post.get("text", ""),
                    "timestamp": post.get("timestamp", ""),
                    **metrics,
                }
            )
        logger.info("Fetcher: Fetched metrics for %d posts", len(results))
        return results

    def fetch_post_insights(self, post_id: str) -> dict[str, Any]:
        """
        Fetch insight metrics for a single post.

        Args:
            post_id: The Threads post ID.

        Returns:
            Dict with metric names as keys and integer counts as values.
        """
        return self._get_insights(post_id)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _get_threads(self, limit: int) -> list[dict[str, Any]]:
        """Retrieve the user's recent threads list."""
        url = f"{THREADS_API_BASE}/{self._user_id}/threads"
        params = {
            "fields": "id,text,timestamp",
            "limit": min(limit, 100),
            "access_token": self._token,
        }
        response = requests.get(url, params=params, timeout=30)
        self._raise_for_status(response, "get threads")
        data: list[dict[str, Any]] = response.json().get("data", [])
        return data

    def _get_insights(self, post_id: str) -> dict[str, Any]:
        """Retrieve insight metrics for a single post."""
        url = f"{THREADS_API_BASE}/{post_id}/insights"
        params = {
            "metric": ",".join(INSIGHT_METRICS),
            "access_token": self._token,
        }
        response = requests.get(url, params=params, timeout=30)
        if not response.ok:
            logger.warning(
                "Fetcher: Insights unavailable for post %s: %s",
                post_id,
                response.text,
            )
            return {m: 0 for m in INSIGHT_METRICS}

        metrics: dict[str, Any] = {m: 0 for m in INSIGHT_METRICS}
        for item in response.json().get("data", []):
            name = item.get("name")
            if name in metrics:
                metrics[name] = item.get("values", [{}])[0].get("value", 0)
        return metrics

    @staticmethod
    def _raise_for_status(response: requests.Response, step: str) -> None:
        if not response.ok:
            raise RuntimeError(
                f"Fetcher: API error at '{step}': "
                f"status={response.status_code} body={response.text}"
            )
