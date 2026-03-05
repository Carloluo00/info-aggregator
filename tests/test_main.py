from __future__ import annotations

from pathlib import Path

from app.config import Settings
from app.main import main


class _FakeDB:
    def get_setting(self, _key: str, default: str | None = None) -> str | None:
        return default

    def list_sources(self, enabled_only: bool = True):
        return []


def test_main_once_smoke(monkeypatch, capsys) -> None:
    fake_settings = Settings(
        feishu_webhook_url="https://open.feishu.cn/open-apis/bot/v2/hook/token",
        feishu_bot_secret="",
        poll_interval_seconds=300,
        rss_urls=["https://example.com/feed"],
        sqlite_path=Path("data/app.db"),
        max_push_per_cycle=5,
        summary_when_exceed=True,
    )

    monkeypatch.setattr("app.main.build_runtime", lambda: (fake_settings, _FakeDB(), object()))
    monkeypatch.setattr(
        "app.main.run_once",
        lambda **_kwargs: {"fetched": 1, "sent": 1, "deduplicated": 0},
    )

    code = main(["--once"])
    out = capsys.readouterr().out

    assert code == 0
    assert "fetched" in out
