"""
Researcher Agent
Collects trending topics and content ideas for Threads posts.
"""

import json
import logging
import re
from typing import Any

import anthropic

from config import settings

logger = logging.getLogger(__name__)


class ResearcherAgent:
    """
    Agent 1: Researcher
    Searches for trending topics and collects content ideas using Claude.
    """

    SYSTEM_PROMPT = (
        "あなたはThreadsアカウントのコンテンツリサーチャーです。\n"
        "日本語で、今日のトレンドや話題になっているテーマを調査し、"
        "Threads投稿に適したネタを収集してください。\n"
        "テーマは具体的で、読者の興味を引くものを選んでください。"
    )

    def __init__(self, client: anthropic.Anthropic | None = None) -> None:
        self._client = client or anthropic.Anthropic(api_key=settings.anthropic_api_key)

    def collect_topics(self, niche: str = "", count: int = 5) -> list[dict[str, Any]]:
        """
        Collect trending topic ideas for Threads posts.

        Args:
            niche: Optional niche or category to focus research on.
            count: Number of topic ideas to generate.

        Returns:
            List of topic dictionaries with keys 'title', 'description', 'hashtags'.
        """
        niche_instruction = f"ニッチ: {niche}\n" if niche else ""
        user_message = (
            f"{niche_instruction}"
            f"Threads投稿に適したトレンドネタを{count}件リストアップしてください。\n"
            "各ネタは以下のJSON形式で返してください（JSON配列のみ出力）:\n"
            '[\n  {"title": "タイトル", "description": "説明文", "hashtags": ["#タグ1", "#タグ2"]},\n  ...\n]'
        )

        logger.info("Researcher: Collecting %d topics (niche=%r)", count, niche)
        message = self._client.messages.create(
            model=settings.claude_model,
            max_tokens=1024,
            system=self.SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )

        raw = message.content[0].text
        match = re.search(r"\[.*\]", raw, re.DOTALL)
        if not match:
            logger.warning("Researcher: Failed to parse JSON from response: %s", raw)
            return []

        topics: list[dict[str, Any]] = json.loads(match.group())
        logger.info("Researcher: Collected %d topics", len(topics))
        return topics
