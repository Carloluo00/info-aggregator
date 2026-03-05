from __future__ import annotations

from collections.abc import Callable

from app.fetchers.rss_fetcher import fetch_rss
from app.fetchers.web_fetcher import fetch_web
from app.models import NewsItem, Source


FetcherFn = Callable[[Source], list[NewsItem]]


def get_enabled_sources(db: object) -> list[Source]:
    return db.list_sources(enabled_only=True)


def fetch_from_source(source: Source) -> list[NewsItem]:
    if source.source_type == "rss":
        return fetch_rss(source.url)
    if source.source_type == "web":
        return fetch_web(source)
    raise ValueError(f"Unsupported source_type: {source.source_type}")
