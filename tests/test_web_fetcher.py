from __future__ import annotations

from app.fetchers.web_fetcher import fetch_web
from app.models import Source


class _MockResponse:
    def __init__(self, text: str) -> None:
        self.text = text

    def raise_for_status(self) -> None:
        return None


def test_fetch_web_parses_static_list(monkeypatch) -> None:
    html = """
    <html><body>
      <div class="post">
        <h2 class="title">Hello</h2>
        <a class="link" href="/p/1">Open</a>
        <span class="date">2026-03-05</span>
      </div>
    </body></html>
    """
    source = Source(
        id=1,
        name="WebSource",
        source_type="web",
        url="https://example.com/news",
        enabled=True,
        fetch_interval_seconds=None,
        selectors={
            "item_selector": ".post",
            "title_selector": ".title",
            "link_selector": ".link",
            "published_selector": ".date",
        },
    )

    monkeypatch.setattr(
        "app.fetchers.web_fetcher.requests.get",
        lambda *_args, **_kwargs: _MockResponse(html),
    )

    items = fetch_web(source)
    assert len(items) == 1
    assert items[0].title == "Hello"
    assert items[0].link == "https://example.com/p/1"
    assert items[0].published == "2026-03-05"


def test_fetch_web_requires_selectors() -> None:
    source = Source(1, "WebSource", "web", "https://example.com/news", True, None, None)
    try:
        fetch_web(source)
    except ValueError as exc:
        assert "selectors" in str(exc).lower()
    else:
        raise AssertionError("expected ValueError")
