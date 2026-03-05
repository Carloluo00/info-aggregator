from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NewsItem:
    source_url: str
    item_id: str
    title: str
    link: str
    published: str
    summary: str
