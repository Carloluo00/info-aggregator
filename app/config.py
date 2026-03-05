from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    feishu_webhook_url: str
    feishu_bot_secret: str
    poll_interval_seconds: int
    rss_urls: list[str]
    sqlite_path: Path


def _parse_rss_urls(raw: str) -> list[str]:
    urls = [item.strip() for item in raw.split(",") if item.strip()]
    if not urls:
        raise ValueError("RSS_URLS must contain at least one URL")
    return urls


def load_settings(dotenv_path: str | None = None) -> Settings:
    load_dotenv(dotenv_path=dotenv_path, override=False)

    webhook = os.getenv("FEISHU_WEBHOOK_URL", "").strip()
    if not webhook.startswith("http"):
        raise ValueError("FEISHU_WEBHOOK_URL must be a valid http(s) URL")

    secret = os.getenv("FEISHU_BOT_SECRET", "").strip()

    raw_interval = os.getenv("POLL_INTERVAL_SECONDS", "300").strip()
    try:
        interval = int(raw_interval)
    except ValueError as exc:
        raise ValueError("POLL_INTERVAL_SECONDS must be an integer") from exc
    if interval <= 0:
        raise ValueError("POLL_INTERVAL_SECONDS must be greater than 0")

    rss_urls = _parse_rss_urls(os.getenv("RSS_URLS", ""))

    sqlite_path = Path(os.getenv("SQLITE_PATH", "data/app.db")).expanduser()

    return Settings(
        feishu_webhook_url=webhook,
        feishu_bot_secret=secret,
        poll_interval_seconds=interval,
        rss_urls=rss_urls,
        sqlite_path=sqlite_path,
    )
