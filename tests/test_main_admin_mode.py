from __future__ import annotations

from pathlib import Path

from app.config import Settings
from app.main import main


def test_main_admin_mode_runs_uvicorn(monkeypatch) -> None:
    fake_settings = Settings(
        feishu_webhook_url="https://open.feishu.cn/open-apis/bot/v2/hook/token",
        feishu_bot_secret="",
        poll_interval_seconds=300,
        rss_urls=[],
        sqlite_path=Path("data/app.db"),
        max_push_per_cycle=5,
        summary_when_exceed=True,
    )
    captured = {}

    monkeypatch.setattr("app.main.build_runtime", lambda: (fake_settings, object(), object()))
    monkeypatch.setattr(
        "app.main.run_admin_server",
        lambda _db, port: captured.update({"port": port}),
    )

    code = main(["--admin", "--admin-port", "8011"])
    assert code == 0
    assert captured["port"] == 8011
