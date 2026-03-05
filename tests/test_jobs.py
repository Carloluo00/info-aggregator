from __future__ import annotations

from app.models import NewsItem, Source
from app.scheduler.jobs import run_once


class _FakeDB:
    def __init__(self) -> None:
        self.seen: set[tuple[str, str]] = set()

    def has_item(self, source_url: str, item_id: str) -> bool:
        return (source_url, item_id) in self.seen

    def add_item(self, source_url: str, item_id: str, **_kwargs) -> bool:
        key = (source_url, item_id)
        if key in self.seen:
            return False
        self.seen.add(key)
        return True


class _FakeNotifier:
    def __init__(self) -> None:
        self.sent_ids: list[str] = []
        self.summary_calls = 0

    def send_news(self, item: NewsItem) -> bool:
        self.sent_ids.append(item.item_id)
        return True

    def send_summary(self, *_args, **_kwargs) -> bool:
        self.summary_calls += 1
        return True


def test_run_once_sends_only_new_items() -> None:
    source = Source(1, "rss", "rss", "https://example.com/feed", True, None, None)
    first = NewsItem(source.url, "id-1", "t1", "https://example.com/1", "", "")
    second = NewsItem(source.url, "id-2", "t2", "https://example.com/2", "", "")

    db = _FakeDB()
    notifier = _FakeNotifier()

    def _fetcher(_source: Source) -> list[NewsItem]:
        return [first, second]

    stats_first = run_once([source], _fetcher, notifier, db, max_push_per_cycle=10)
    stats_second = run_once([source], _fetcher, notifier, db, max_push_per_cycle=10)

    assert stats_first["fetched"] == 2
    assert stats_first["sent"] == 2
    assert stats_first["deduplicated"] == 0
    assert stats_second["sent"] == 0
    assert stats_second["deduplicated"] == 2
    assert notifier.sent_ids == ["id-1", "id-2"]
