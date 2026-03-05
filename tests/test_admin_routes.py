from __future__ import annotations

import uuid
from pathlib import Path

import pytest

fastapi_testclient = pytest.importorskip("fastapi.testclient")
TestClient = fastapi_testclient.TestClient

from app.admin import create_admin_app
from app.storage.db import Database


def test_admin_source_flow() -> None:
    db_path = Path("data") / f"test_admin_{uuid.uuid4().hex}.db"
    db = Database(db_path)
    try:
        db.init()
        app = create_admin_app(db)
        client = TestClient(app)

        res = client.get("/sources")
        assert res.status_code == 200

        create = client.post(
            "/sources/new",
            data={
                "source_name": "Test RSS",
                "source_type": "rss",
                "source_url": "https://example.com/feed",
                "source_enabled": "1",
            },
            follow_redirects=False,
        )
        assert create.status_code == 303

        list_after = client.get("/sources")
        assert "Test RSS" in list_after.text

        source = db.list_sources()[0]
        disable = client.post(
            f"/sources/{source.id}/toggle",
            data={"enabled": "0"},
            follow_redirects=False,
        )
        assert disable.status_code == 303
        assert db.get_source(source.id) is not None
        assert db.get_source(source.id).enabled is False  # type: ignore[union-attr]
    finally:
        if db_path.exists():
            db_path.unlink()


def test_admin_settings_flow() -> None:
    db_path = Path("data") / f"test_admin_settings_{uuid.uuid4().hex}.db"
    db = Database(db_path)
    try:
        db.init()
        app = create_admin_app(db)
        client = TestClient(app)
        res = client.post(
            "/settings",
            data={"max_push_per_cycle": "12", "summary_when_exceed": "false"},
            follow_redirects=False,
        )
        assert res.status_code == 303
        assert db.get_setting("max_push_per_cycle") == "12"
        assert db.get_setting("summary_when_exceed") == "false"
    finally:
        if db_path.exists():
            db_path.unlink()
