from __future__ import annotations

import uuid
from pathlib import Path

from app.storage.db import Database


def test_db_init_and_dedup() -> None:
    db_path = Path("data") / f"test_{uuid.uuid4().hex}.db"
    db = Database(db_path)

    try:
        db.init()

        source = "https://example.com/feed"
        item_id = "item-1"

        assert db.has_item(source, item_id) is False
        assert db.add_item(source, item_id, "title", "https://example.com/1") is True
        assert db.has_item(source, item_id) is True

        # Duplicate item should be ignored by unique constraint.
        assert db.add_item(source, item_id, "title", "https://example.com/1") is False
    finally:
        if db_path.exists():
            db_path.unlink()
