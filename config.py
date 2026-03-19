"""
Configuration module
Loads settings from environment variables (or a .env file).
"""

import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application-wide settings loaded from environment variables."""

    # Anthropic / Claude
    anthropic_api_key: str = os.environ.get("ANTHROPIC_API_KEY", "")
    claude_model: str = os.environ.get("CLAUDE_MODEL", "claude-3-5-haiku-20241022")

    # Threads API
    threads_access_token: str = os.environ.get("THREADS_ACCESS_TOKEN", "")
    threads_user_id: str = os.environ.get("THREADS_USER_ID", "")

    # Pipeline defaults
    default_niche: str = os.environ.get("DEFAULT_NICHE", "")
    default_topics_count: int = int(os.environ.get("DEFAULT_TOPICS_COUNT", "3"))


settings = Settings()
