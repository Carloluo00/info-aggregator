from __future__ import annotations

from collections.abc import Callable
from typing import Any

from app.models import NewsItem


def run_once(
    rss_urls: list[str],
    fetcher: Callable[[str], list[NewsItem]],
    notifier: Any,
    db: Any,
) -> dict[str, int]:
    stats = {"fetched": 0, "sent": 0, "deduplicated": 0}
    for source_url in rss_urls:
        items = fetcher(source_url)
        stats["fetched"] += len(items)
        for item in items:
            if db.has_item(item.source_url, item.item_id):
                stats["deduplicated"] += 1
                continue

            if notifier.send_news(item):
                db.add_item(
                    source_url=item.source_url,
                    item_id=item.item_id,
                    title=item.title,
                    link=item.link,
                    published=item.published,
                )
                stats["sent"] += 1
    return stats


def build_scheduler(interval_seconds: int, job_func: Callable[[], None]) -> Any:
    from apscheduler.schedulers.background import BackgroundScheduler

    scheduler = BackgroundScheduler()
    scheduler.add_job(job_func, "interval", seconds=interval_seconds)
    return scheduler
