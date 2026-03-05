from __future__ import annotations

from app.models import NewsItem, Source
from app.scheduler.jobs import run_once


class _FakeDB:
    def __init__(self) -> None:
        self.seen: set[tuple[str, str]] = set()

    def has_item(self, source_url: str, item_id: str) -> bool:
        return (source_url, item_id) in self.seen

    def add_item(self, source_url: str, item_id: str, **_kwargs) -> bool:
        self.seen.add((source_url, item_id))
        return True


class _FakeNotifier:
    def __init__(self) -> None:
        self.sent_ids: list[str] = []
        self.summary_calls = 0

    def send_news(self, item: NewsItem) -> bool:
        self.sent_ids.append(item.item_id)
        return True

    def send_summary(self, total_pending: int, sent_count: int, items: list[NewsItem]) -> bool:
        self.summary_calls += 1
        assert total_pending == 8
        assert sent_count == 5
        assert len(items) == 3
        return True


def test_run_once_applies_rate_limit_and_summary() -> None:
    source = Source(1, "web", "web", "https://example.com/news", True, None, {"item_selector": ".x"})
    items = [
        NewsItem(source.url, f"id-{i}", f"title-{i}", f"https://example.com/{i}", "", "")
        for i in range(8)
    ]

    db = _FakeDB()
    notifier = _FakeNotifier()
    stats = run_once(
        [source],
        lambda _src: items,
        notifier,
        db,
        max_push_per_cycle=5,
        summary_when_exceed=True,
    )
    assert stats["sent"] == 5
    assert stats["summarized"] == 1
    assert len(db.seen) == 5
    assert notifier.sent_ids == [f"id-{i}" for i in range(5)]
