from __future__ import annotations

import hashlib
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from app.models import NewsItem, Source


def _item_id(link: str, title: str) -> str:
    return hashlib.sha256(f"{link}|{title}".encode("utf-8")).hexdigest()


def _require_selector(selectors: dict, key: str) -> str:
    value = str(selectors.get(key, "")).strip()
    if not value:
        raise ValueError(f"Missing selector: {key}")
    return value


def fetch_web(source: Source, timeout: int = 10) -> list[NewsItem]:
    if source.selectors is None:
        raise ValueError("Web source requires selectors")

    item_selector = _require_selector(source.selectors, "item_selector")
    title_selector = _require_selector(source.selectors, "title_selector")
    link_selector = _require_selector(source.selectors, "link_selector")
    published_selector = str(source.selectors.get("published_selector", "")).strip()

    response = requests.get(source.url, timeout=timeout)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    items: list[NewsItem] = []
    for block in soup.select(item_selector):
        title_node = block.select_one(title_selector)
        link_node = block.select_one(link_selector)
        if title_node is None or link_node is None:
            continue

        title = title_node.get_text(strip=True)
        href = (link_node.get("href") or "").strip()
        if not title or not href:
            continue

        link = urljoin(source.url, href)
        published = ""
        if published_selector:
            published_node = block.select_one(published_selector)
            if published_node is not None:
                published = published_node.get_text(strip=True)

        items.append(
            NewsItem(
                source_url=source.url,
                item_id=_item_id(link, title),
                title=title,
                link=link,
                published=published,
                summary="",
            )
        )
    return items
