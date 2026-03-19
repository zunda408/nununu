"""
Supervisor Agent
Orchestrates all agents, monitors execution, and detects anomalies.
"""

import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import anthropic

from config import settings

logger = logging.getLogger(__name__)


@dataclass
class RunReport:
    """Summary report produced after each supervisor run."""

    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    topics: list[dict[str, Any]] = field(default_factory=list)
    analysis: dict[str, Any] = field(default_factory=dict)
    posts_published: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    anomalies: list[str] = field(default_factory=list)
    finished_at: str = ""


class SupervisorAgent:
    """
    Agent 6: Supervisor
    Orchestrates the full pipeline and performs anomaly detection.

    Pipeline:
        Fetcher → Analyst → Researcher → Writer → Poster
    """

    ANOMALY_SYSTEM_PROMPT = (
        "あなたはThreadsアカウント運用の監視AIです。\n"
        "提供された実行レポートを確認し、異常や問題点を日本語で指摘してください。\n"
        "問題がなければ「異常なし」と返してください。"
    )

    def __init__(
        self,
        researcher=None,
        analyst=None,
        writer=None,
        poster=None,
        fetcher=None,
        claude_client: anthropic.Anthropic | None = None,
    ) -> None:
        # Lazy-import to avoid circular imports; allow injection for testing
        if researcher is None:
            from agents.researcher import ResearcherAgent
            researcher = ResearcherAgent()
        if analyst is None:
            from agents.analyst import AnalystAgent
            analyst = AnalystAgent()
        if writer is None:
            from agents.writer import WriterAgent
            writer = WriterAgent()
        if poster is None:
            from agents.poster import PosterAgent
            poster = PosterAgent()
        if fetcher is None:
            from agents.fetcher import FetcherAgent
            fetcher = FetcherAgent()

        self._researcher = researcher
        self._analyst = analyst
        self._writer = writer
        self._poster = poster
        self._fetcher = fetcher
        self._claude = claude_client or anthropic.Anthropic(api_key=settings.anthropic_api_key)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def run(
        self,
        niche: str = "",
        topics_count: int = 3,
        dry_run: bool = False,
    ) -> RunReport:
        """
        Execute the full content pipeline.

        Args:
            niche: Optional content niche to focus on.
            topics_count: How many topics to research and post.
            dry_run: If True, skip the actual Threads API post.

        Returns:
            RunReport summarising what happened.
        """
        report = RunReport()
        logger.info("Supervisor: Pipeline started (niche=%r, dry_run=%s)", niche, dry_run)

        # Step 1 – Fetch recent performance data
        posts_data: list[dict[str, Any]] = []
        try:
            posts_data = self._fetcher.fetch_recent_posts(limit=20)
        except Exception as exc:
            msg = f"Fetcher error: {exc}"
            logger.error("Supervisor: %s", msg)
            report.errors.append(msg)

        # Step 2 – Analyse performance
        analysis: dict[str, Any] = {}
        try:
            analysis = self._analyst.analyze(posts_data)
            report.analysis = analysis
        except Exception as exc:
            msg = f"Analyst error: {exc}"
            logger.error("Supervisor: %s", msg)
            report.errors.append(msg)

        recommendations: list[str] = analysis.get("recommendations", [])

        # Step 3 – Research topics
        topics: list[dict[str, Any]] = []
        try:
            topics = self._researcher.collect_topics(niche=niche, count=topics_count)
            report.topics = topics
        except Exception as exc:
            msg = f"Researcher error: {exc}"
            logger.error("Supervisor: %s", msg)
            report.errors.append(msg)

        # Step 4 & 5 – Write and post for each topic
        for topic in topics:
            try:
                post_text = self._writer.generate_post(topic, recommendations=recommendations)
            except Exception as exc:
                msg = f"Writer error for topic '{topic.get('title')}': {exc}"
                logger.error("Supervisor: %s", msg)
                report.errors.append(msg)
                continue

            if dry_run:
                logger.info("Supervisor: [dry_run] Would post: %s", post_text[:80])
                report.posts_published.append({"dry_run": True, "text": post_text})
                continue

            try:
                result = self._poster.post(post_text)
                report.posts_published.append({"text": post_text, **result})
            except Exception as exc:
                msg = f"Poster error for topic '{topic.get('title')}': {exc}"
                logger.error("Supervisor: %s", msg)
                report.errors.append(msg)

        # Step 6 – Anomaly detection
        report.anomalies = self._detect_anomalies(report)
        report.finished_at = datetime.now(timezone.utc).isoformat()
        logger.info(
            "Supervisor: Pipeline finished. published=%d errors=%d anomalies=%d",
            len(report.posts_published),
            len(report.errors),
            len(report.anomalies),
        )
        return report

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _detect_anomalies(self, report: RunReport) -> list[str]:
        """Use Claude to review the run report and detect anomalies."""
        report_dict = {
            "started_at": report.started_at,
            "topics_count": len(report.topics),
            "posts_published_count": len(report.posts_published),
            "errors": report.errors,
            "analysis_summary": report.analysis.get("summary", ""),
        }
        user_message = (
            "以下の実行レポートを確認し、異常や問題点を指摘してください:\n\n"
            f"{json.dumps(report_dict, ensure_ascii=False, indent=2)}\n\n"
            "問題点があれば箇条書きのJSONリスト形式で、なければ空リスト [] を返してください。"
        )

        try:
            message = self._claude.messages.create(
                model=settings.claude_model,
                max_tokens=512,
                system=self.ANOMALY_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_message}],
            )
            raw = message.content[0].text
            match = re.search(r"\[.*?\]", raw, re.DOTALL)
            if match:
                anomalies: list[str] = json.loads(match.group())
                return anomalies
        except Exception as exc:
            logger.error("Supervisor: Anomaly detection error: %s", exc)

        return []
