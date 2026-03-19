"""
Writer Agent
Automatically generates Threads post content using Claude.
"""

import logging
from typing import Any

import anthropic

from config import settings

logger = logging.getLogger(__name__)

# Threads post character limit
THREADS_MAX_CHARS = 500


class WriterAgent:
    """
    Agent 3: Writer
    Generates engaging Threads post text based on topic and analyst recommendations.
    """

    SYSTEM_PROMPT = (
        "あなたはThreadsアカウントの投稿ライターです。\n"
        f"最大{THREADS_MAX_CHARS}文字の日本語Threads投稿を作成してください。\n"
        "読者の共感を得られる、自然で魅力的な文章にしてください。\n"
        "絵文字を適切に使い、エンゲージメントを高める工夫をしてください。"
    )

    def __init__(self, client: anthropic.Anthropic | None = None) -> None:
        self._client = client or anthropic.Anthropic(api_key=settings.anthropic_api_key)

    def generate_post(
        self,
        topic: dict[str, Any],
        recommendations: list[str] | None = None,
    ) -> str:
        """
        Generate a Threads post for the given topic.

        Args:
            topic: Topic dict with 'title', 'description', 'hashtags'.
            recommendations: Optional list of analyst recommendations to incorporate.

        Returns:
            Post text string within THREADS_MAX_CHARS characters.
        """
        rec_section = ""
        if recommendations:
            rec_text = "\n".join(f"- {r}" for r in recommendations)
            rec_section = f"\n\n参考にすべきアナリストの改善提案:\n{rec_text}"

        hashtags_str = " ".join(topic.get("hashtags", []))
        user_message = (
            f"テーマ: {topic.get('title', '')}\n"
            f"内容: {topic.get('description', '')}\n"
            f"ハッシュタグ: {hashtags_str}"
            f"{rec_section}\n\n"
            f"上記テーマでThreads投稿を{THREADS_MAX_CHARS}文字以内で作成してください。"
            "投稿テキストのみ返してください。"
        )

        logger.info("Writer: Generating post for topic %r", topic.get("title"))
        message = self._client.messages.create(
            model=settings.claude_model,
            max_tokens=1024,
            system=self.SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )

        post_text: str = message.content[0].text.strip()
        if len(post_text) > THREADS_MAX_CHARS:
            logger.warning(
                "Writer: Post exceeds %d chars (%d), truncating",
                THREADS_MAX_CHARS,
                len(post_text),
            )
            post_text = post_text[:THREADS_MAX_CHARS]

        logger.info("Writer: Post generated (%d chars)", len(post_text))
        return post_text
