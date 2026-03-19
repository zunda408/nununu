"""
Analyst Agent
Analyzes past post performance and derives actionable insights.
"""

import json
import logging
import re
from typing import Any

import anthropic

from config import settings

logger = logging.getLogger(__name__)


class AnalystAgent:
    """
    Agent 2: Analyst
    Analyzes post performance data and returns recommendations using Claude.
    """

    SYSTEM_PROMPT = (
        "あなたはThreadsアカウントのパフォーマンスアナリストです。\n"
        "提供された投稿データ（閲覧数、いいね数、返信数、リポスト数）を分析し、"
        "今後の投稿戦略に役立つ洞察と改善提案を日本語で提供してください。"
    )

    def __init__(self, client: anthropic.Anthropic | None = None) -> None:
        self._client = client or anthropic.Anthropic(api_key=settings.anthropic_api_key)

    def analyze(self, posts_data: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Analyze post performance data and return insights.

        Args:
            posts_data: List of post dicts with keys 'id', 'text', 'views',
                        'likes', 'replies', 'reposts', 'timestamp'.

        Returns:
            Dictionary with 'summary', 'top_posts', 'recommendations'.
        """
        if not posts_data:
            return {
                "summary": "分析対象の投稿がありません。",
                "top_posts": [],
                "recommendations": [],
            }

        data_str = json.dumps(posts_data, ensure_ascii=False, indent=2)
        user_message = (
            "以下の投稿パフォーマンスデータを分析してください:\n\n"
            f"{data_str}\n\n"
            "次のJSON形式で返してください（JSON オブジェクトのみ出力）:\n"
            "{\n"
            '  "summary": "全体の傾向まとめ",\n'
            '  "top_posts": ["最もパフォーマンスの高い投稿IDリスト"],\n'
            '  "recommendations": ["改善提案1", "改善提案2", ...]\n'
            "}"
        )

        logger.info("Analyst: Analyzing %d posts", len(posts_data))
        message = self._client.messages.create(
            model=settings.claude_model,
            max_tokens=1024,
            system=self.SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )

        raw = message.content[0].text
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            logger.warning("Analyst: Failed to parse JSON from response: %s", raw)
            return {"summary": raw, "top_posts": [], "recommendations": []}

        result: dict[str, Any] = json.loads(match.group())
        logger.info("Analyst: Analysis complete")
        return result
