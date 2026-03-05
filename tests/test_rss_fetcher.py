from __future__ import annotations

from app.fetchers.rss_fetcher import fetch_rss


class _MockResponse:
    def __init__(self, content: bytes) -> None:
        self.content = content

    def raise_for_status(self) -> None:
        return None


def test_fetch_rss_parses_entries(monkeypatch) -> None:
    xml = b"""<?xml version="1.0"?>
    <rss version="2.0">
      <channel>
        <title>Example Feed</title>
        <item>
          <guid>id-1</guid>
          <title>Title 1</title>
          <link>https://example.com/1</link>
          <pubDate>Thu, 05 Mar 2026 10:00:00 GMT</pubDate>
          <description>Summary 1</description>
        </item>
      </channel>
    </rss>"""

    def _mock_get(url: str, timeout: int):
        assert url == "https://example.com/feed"
        assert timeout == 10
        return _MockResponse(xml)

    monkeypatch.setattr("app.fetchers.rss_fetcher.requests.get", _mock_get)

    items = fetch_rss("https://example.com/feed")

    assert len(items) == 1
    assert items[0].item_id == "id-1"
    assert items[0].title == "Title 1"
    assert items[0].link == "https://example.com/1"
    assert "2026" in items[0].published


def test_fetch_rss_generates_id_when_missing(monkeypatch) -> None:
    xml = b"""<?xml version="1.0"?>
    <rss version="2.0">
      <channel>
        <item>
          <title>No Guid</title>
          <link>https://example.com/no-guid</link>
        </item>
      </channel>
    </rss>"""

    monkeypatch.setattr(
        "app.fetchers.rss_fetcher.requests.get",
        lambda *_args, **_kwargs: _MockResponse(xml),
    )

    items = fetch_rss("https://example.com/feed")

    assert len(items) == 1
    assert len(items[0].item_id) == 64
