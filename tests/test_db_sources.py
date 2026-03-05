from __future__ import annotations

import uuid
from pathlib import Path

from app.storage.db import Database


def test_source_crud_and_toggle() -> None:
    db_path = Path("data") / f"test_sources_{uuid.uuid4().hex}.db"
    db = Database(db_path)
    try:
        db.init()
        source_id = db.add_source(
            name="HN RSS",
            source_type="rss",
            url="https://news.ycombinator.com/rss",
        )
        source = db.get_source(source_id)
        assert source is not None
        assert source.name == "HN RSS"
        assert source.enabled is True

        assert db.toggle_source(source_id, False) is True
        source = db.get_source(source_id)
        assert source is not None
        assert source.enabled is False

        assert db.delete_source(source_id) is True
        assert db.get_source(source_id) is None
    finally:
        if db_path.exists():
            db_path.unlink()


def test_import_rss_urls_if_needed_only_once() -> None:
    db_path = Path("data") / f"test_import_{uuid.uuid4().hex}.db"
    db = Database(db_path)
    try:
        db.init()
        inserted = db.import_rss_urls_if_needed(["https://a.com/feed", "https://b.com/feed"])
        assert inserted == 2
        inserted_again = db.import_rss_urls_if_needed(["https://c.com/feed"])
        assert inserted_again == 0
        assert len(db.list_sources()) == 2
    finally:
        if db_path.exists():
            db_path.unlink()


def test_settings_upsert() -> None:
    db_path = Path("data") / f"test_settings_{uuid.uuid4().hex}.db"
    db = Database(db_path)
    try:
        db.init()
        assert db.get_setting("max_push_per_cycle") is None
        db.set_setting("max_push_per_cycle", "5")
        assert db.get_setting("max_push_per_cycle") == "5"
        db.set_setting("max_push_per_cycle", "10")
        assert db.get_setting("max_push_per_cycle") == "10"
    finally:
        if db_path.exists():
            db_path.unlink()
