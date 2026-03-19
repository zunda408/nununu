"""
Poster Agent
Publishes posts to Threads via the Threads API.
"""

import logging
from typing import Any

import requests

from config import settings

logger = logging.getLogger(__name__)

THREADS_API_BASE = "https://graph.threads.net/v1.0"


class PosterAgent:
    """
    Agent 4: Poster
    Handles two-step post creation and publishing using the Threads API.
    """

    def __init__(self, access_token: str | None = None, user_id: str | None = None) -> None:
        self._token = access_token or settings.threads_access_token
        self._user_id = user_id or settings.threads_user_id

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def post(self, text: str) -> dict[str, Any]:
        """
        Create and publish a text post to Threads.

        Args:
            text: Post body (≤500 characters).

        Returns:
            Dict with 'container_id' and 'post_id' on success.

        Raises:
            RuntimeError: If the API call fails.
        """
        container_id = self._create_container(text)
        post_id = self._publish_container(container_id)
        logger.info("Poster: Published post id=%s", post_id)
        return {"container_id": container_id, "post_id": post_id}

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _create_container(self, text: str) -> str:
        """Step 1 – create a media container."""
        url = f"{THREADS_API_BASE}/{self._user_id}/threads"
        payload = {
            "media_type": "TEXT",
            "text": text,
            "access_token": self._token,
        }
        response = requests.post(url, data=payload, timeout=30)
        self._raise_for_status(response, "create container")
        container_id: str = response.json()["id"]
        logger.info("Poster: Container created id=%s", container_id)
        return container_id

    def _publish_container(self, container_id: str) -> str:
        """Step 2 – publish the container."""
        url = f"{THREADS_API_BASE}/{self._user_id}/threads_publish"
        payload = {
            "creation_id": container_id,
            "access_token": self._token,
        }
        response = requests.post(url, data=payload, timeout=30)
        self._raise_for_status(response, "publish container")
        post_id: str = response.json()["id"]
        return post_id

    @staticmethod
    def _raise_for_status(response: requests.Response, step: str) -> None:
        if not response.ok:
            raise RuntimeError(
                f"Poster: API error at '{step}': "
                f"status={response.status_code} body={response.text}"
            )
