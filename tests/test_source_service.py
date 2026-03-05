from __future__ import annotations

from app.models import Source
from app.services.source_service import fetch_from_source, get_enabled_sources


class _FakeDB:
    def list_sources(self, enabled_only: bool = False):
        all_sources = [
            Source(1, "A", "rss", "https://a.com/feed", True, None, None),
            Source(2, "B", "rss", "https://b.com/feed", False, None, None),
        ]
        if enabled_only:
            return [s for s in all_sources if s.enabled]
        return all_sources


def test_get_enabled_sources() -> None:
    db = _FakeDB()
    result = get_enabled_sources(db)
    assert len(result) == 1
    assert result[0].name == "A"


def test_fetch_from_source_dispatch(monkeypatch) -> None:
    src_rss = Source(1, "R", "rss", "https://a.com/feed", True, None, None)
    src_web = Source(
        2,
        "W",
        "web",
        "https://site.com/news",
        True,
        None,
        {"item_selector": ".x", "title_selector": ".t", "link_selector": "a"},
    )

    monkeypatch.setattr("app.services.source_service.fetch_rss", lambda _url: ["rss"])
    monkeypatch.setattr("app.services.source_service.fetch_web", lambda _src: ["web"])

    assert fetch_from_source(src_rss) == ["rss"]
    assert fetch_from_source(src_web) == ["web"]
