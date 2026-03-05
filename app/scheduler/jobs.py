from __future__ import annotations

from collections.abc import Callable
from typing import Any

from app.models import NewsItem, Source


def run_once(
    sources: list[Source],
    fetcher: Callable[[Source], list[NewsItem]],
    notifier: Any,
    db: Any,
    max_push_per_cycle: int = 5,
    summary_when_exceed: bool = True,
) -> dict[str, int]:
    stats = {"fetched": 0, "sent": 0, "deduplicated": 0, "source_errors": 0, "summarized": 0}
    pending_items: list[NewsItem] = []

    for source in sources:
        try:
            items = fetcher(source)
        except Exception:
            stats["source_errors"] += 1
            continue
        stats["fetched"] += len(items)
        for item in items:
            if db.has_item(item.source_url, item.item_id):
                stats["deduplicated"] += 1
                continue
            pending_items.append(item)

    send_count = min(len(pending_items), max_push_per_cycle)
    for item in pending_items[:send_count]:
        if notifier.send_news(item):
            db.add_item(
                source_url=item.source_url,
                item_id=item.item_id,
                title=item.title,
                link=item.link,
                published=item.published,
            )
            stats["sent"] += 1

    if summary_when_exceed and len(pending_items) > max_push_per_cycle:
        overflow_items = pending_items[max_push_per_cycle:]
        if notifier.send_summary(total_pending=len(pending_items), sent_count=stats["sent"], items=overflow_items):
            stats["summarized"] += 1

    return stats


def build_scheduler(interval_seconds: int, job_func: Callable[[], None]) -> Any:
    from apscheduler.schedulers.background import BackgroundScheduler

    scheduler = BackgroundScheduler()
    scheduler.add_job(job_func, "interval", seconds=interval_seconds)
    return scheduler
