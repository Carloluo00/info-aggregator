from __future__ import annotations

import argparse
import time
from typing import Any

from app.config import Settings, load_settings
from app.notifier.feishu import FeishuNotifier
from app.scheduler.jobs import build_scheduler, run_once
from app.services.source_service import fetch_from_source, get_enabled_sources
from app.storage.db import Database


def build_runtime(settings: Settings | None = None) -> tuple[Settings, Database, Any]:
    active_settings = settings or load_settings()
    db = Database(active_settings.sqlite_path)
    db.init()
    db.import_rss_urls_if_needed(active_settings.rss_urls)
    if db.get_setting("max_push_per_cycle") is None:
        db.set_setting("max_push_per_cycle", str(active_settings.max_push_per_cycle))
    if db.get_setting("summary_when_exceed") is None:
        db.set_setting(
            "summary_when_exceed",
            "true" if active_settings.summary_when_exceed else "false",
        )
    notifier = FeishuNotifier(active_settings.feishu_webhook_url)
    return active_settings, db, notifier


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Info aggregator MVP")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run one cycle and exit",
    )
    parser.add_argument(
        "--admin",
        action="store_true",
        help="Run local admin panel",
    )
    parser.add_argument(
        "--admin-port",
        type=int,
        default=8000,
        help="Admin panel port",
    )
    args = parser.parse_args(argv)

    settings, db, notifier = build_runtime()

    def job() -> dict[str, int]:
        max_push = int(db.get_setting("max_push_per_cycle", str(settings.max_push_per_cycle)) or "5")
        summary = (
            str(db.get_setting("summary_when_exceed", "true")).strip().lower() == "true"
        )
        return run_once(
            sources=get_enabled_sources(db),
            fetcher=fetch_from_source,
            notifier=notifier,
            db=db,
            max_push_per_cycle=max_push,
            summary_when_exceed=summary,
        )

    if args.admin:
        run_admin_server(db, args.admin_port)
        return 0

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

def run_admin_server(db: Database, port: int) -> None:
    from app.admin import create_admin_app

    try:
        import uvicorn
    except ModuleNotFoundError as exc:
        raise RuntimeError("Admin mode requires uvicorn and fastapi installed") from exc

    app = create_admin_app(db)
    uvicorn.run(app, host="127.0.0.1", port=port)


if __name__ == "__main__":
    raise SystemExit(main())
