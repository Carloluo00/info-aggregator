from __future__ import annotations

from pathlib import Path

from app.config import Settings
from app.main import main


def test_main_once_smoke(monkeypatch, capsys) -> None:
    fake_settings = Settings(
        feishu_webhook_url="https://open.feishu.cn/open-apis/bot/v2/hook/token",
        feishu_bot_secret="",
        poll_interval_seconds=300,
        rss_urls=["https://example.com/feed"],
        sqlite_path=Path("data/app.db"),
    )

    monkeypatch.setattr("app.main.build_runtime", lambda: (fake_settings, object(), object()))
    monkeypatch.setattr(
        "app.main.run_once",
        lambda **_kwargs: {"fetched": 1, "sent": 1, "deduplicated": 0},
    )

    code = main(["--once"])
    out = capsys.readouterr().out

    assert code == 0
    assert "fetched" in out
