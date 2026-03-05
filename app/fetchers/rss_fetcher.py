from __future__ import annotations

import hashlib
import xml.etree.ElementTree as ET

import requests

from app.models import NewsItem

try:
    import feedparser  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - fallback path covered by tests
    feedparser = None


def _build_item_id(raw_id: str, link: str, title: str) -> str:
    if raw_id:
        return raw_id
    fallback = f"{link}|{title}"
    return hashlib.sha256(fallback.encode("utf-8")).hexdigest()


def _parse_with_fallback(content: bytes) -> list[dict[str, str]]:
    root = ET.fromstring(content)
    channel = root.find("channel")
    if channel is None:
        return []

    entries: list[dict[str, str]] = []
    for item in channel.findall("item"):
        entries.append(
            {
                "id": (item.findtext("guid") or "").strip(),
                "title": (item.findtext("title") or "").strip(),
                "link": (item.findtext("link") or "").strip(),
                "published": (item.findtext("pubDate") or "").strip(),
                "summary": (item.findtext("description") or "").strip(),
            }
        )
    return entries


def fetch_rss(source_url: str, timeout: int = 10) -> list[NewsItem]:
    response = requests.get(source_url, timeout=timeout)
    response.raise_for_status()

    if feedparser is None:
        raw_entries = _parse_with_fallback(response.content)
    else:
        parsed = feedparser.parse(response.content)
        raw_entries = [
            {
                "id": str(getattr(entry, "id", "")).strip(),
                "title": str(getattr(entry, "title", "")).strip(),
                "link": str(getattr(entry, "link", "")).strip(),
                "published": str(getattr(entry, "published", "")).strip(),
                "summary": str(getattr(entry, "summary", "")).strip(),
            }
            for entry in parsed.entries
        ]

    items: list[NewsItem] = []

    for entry in raw_entries:
        title = entry["title"]
        link = entry["link"]
        raw_id = entry["id"]
        published = entry["published"]
        summary = entry["summary"]

        if not title or not link:
            continue

        items.append(
            NewsItem(
                source_url=source_url,
                item_id=_build_item_id(raw_id, link, title),
                title=title,
                link=link,
                published=published,
                summary=summary,
            )
        )

    return items
