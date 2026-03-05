import pytest

from app.config import load_settings


def test_load_settings_success(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "FEISHU_WEBHOOK_URL",
        "https://open.feishu.cn/open-apis/bot/v2/hook/token",
    )
    monkeypatch.setenv("FEISHU_BOT_SECRET", "abc123")
    monkeypatch.setenv("POLL_INTERVAL_SECONDS", "120")
    monkeypatch.setenv("RSS_URLS", "https://a.com/feed,https://b.com/rss.xml")
    monkeypatch.setenv("SQLITE_PATH", "data/test.db")

    settings = load_settings(None)

    assert settings.feishu_webhook_url.endswith("token")
    assert settings.feishu_bot_secret == "abc123"
    assert settings.poll_interval_seconds == 120
    assert settings.rss_urls == ["https://a.com/feed", "https://b.com/rss.xml"]
    assert str(settings.sqlite_path).replace("\\", "/") == "data/test.db"


def test_load_settings_requires_valid_webhook(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FEISHU_WEBHOOK_URL", "invalid-url")
    monkeypatch.setenv("RSS_URLS", "https://a.com/feed")

    with pytest.raises(ValueError, match="FEISHU_WEBHOOK_URL"):
        load_settings(None)


def test_load_settings_requires_rss_urls(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FEISHU_WEBHOOK_URL", "https://open.feishu.cn/hook/token")
    monkeypatch.setenv("RSS_URLS", "")

    with pytest.raises(ValueError, match="RSS_URLS"):
        load_settings(None)
