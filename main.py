"""
Main entry point for the Threads AI Agent pipeline.

Usage:
    python main.py [--niche <topic>] [--count <int>] [--dry-run]

Environment variables required (see .env.example):
    ANTHROPIC_API_KEY
    THREADS_ACCESS_TOKEN
    THREADS_USER_ID
"""

import argparse
import json
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the Threads AI Agent pipeline.",
    )
    parser.add_argument(
        "--niche",
        default="",
        help="Content niche / category to focus research on (optional).",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=3,
        help="Number of topics to research and post (default: 3).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run the full pipeline without publishing to Threads.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    from agents.supervisor import SupervisorAgent

    supervisor = SupervisorAgent()
    report = supervisor.run(
        niche=args.niche,
        topics_count=args.count,
        dry_run=args.dry_run,
    )

    print("\n===== Run Report =====")
    print(json.dumps(
        {
            "started_at": report.started_at,
            "finished_at": report.finished_at,
            "topics_researched": len(report.topics),
            "posts_published": len(report.posts_published),
            "errors": report.errors,
            "anomalies": report.anomalies,
        },
        ensure_ascii=False,
        indent=2,
    ))

    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
