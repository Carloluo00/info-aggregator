from __future__ import annotations

import argparse
import time
from typing import Any

from app.config import Settings, load_settings
from app.fetchers.rss_fetcher import fetch_rss
from app.notifier.feishu import FeishuNotifier
from app.scheduler.jobs import build_scheduler, run_once
from app.storage.db import Database


def build_runtime(settings: Settings | None = None) -> tuple[Settings, Database, Any]:
    active_settings = settings or load_settings()
    db = Database(active_settings.sqlite_path)
    db.init()
    notifier = FeishuNotifier(active_settings.feishu_webhook_url)
    return active_settings, db, notifier


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Info aggregator MVP")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run one cycle and exit",
    )
    args = parser.parse_args(argv)

    settings, db, notifier = build_runtime()

    def job() -> dict[str, int]:
        return run_once(
            rss_urls=settings.rss_urls,
            fetcher=fetch_rss,
            notifier=notifier,
            db=db,
        )

    if args.once:
        print(job())
        return 0

    scheduler = build_scheduler(settings.poll_interval_seconds, job)
    scheduler.start()
    print(f"Scheduler started. Interval={settings.poll_interval_seconds}s")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.shutdown(wait=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
