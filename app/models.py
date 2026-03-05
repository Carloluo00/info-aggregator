from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class NewsItem:
    source_url: str
    item_id: str
    title: str
    link: str
    published: str
    summary: str


@dataclass(frozen=True)
class Source:
    id: int
    name: str
    source_type: str
    url: str
    enabled: bool
    fetch_interval_seconds: int | None
    selectors: dict[str, Any] | None
