from __future__ import annotations

import requests

from app.models import NewsItem
from app.notifier.feishu import FeishuNotifier


class _MockResponse:
    def __init__(self, payload: dict, status_ok: bool = True) -> None:
        self._payload = payload
        self._status_ok = status_ok

    def raise_for_status(self) -> None:
        if not self._status_ok:
            raise requests.HTTPError("bad status")

    def json(self) -> dict:
        return self._payload


def _build_item() -> NewsItem:
    return NewsItem(
        source_url="https://example.com/feed",
        item_id="id-1",
        title="Hello",
        link="https://example.com/1",
        published="Thu, 05 Mar 2026 10:00:00 GMT",
        summary="",
    )


def test_send_news_success(monkeypatch) -> None:
    notifier = FeishuNotifier("https://open.feishu.cn/open-apis/bot/v2/hook/token")
    captured = {}

    def _mock_post(url: str, json: dict, timeout: int):
        captured["url"] = url
        captured["json"] = json
        captured["timeout"] = timeout
        return _MockResponse({"code": 0})

    monkeypatch.setattr("app.notifier.feishu.requests.post", _mock_post)

    ok = notifier.send_news(_build_item())

    assert ok is True
    assert captured["url"].startswith("https://open.feishu.cn/")
    assert captured["json"]["msg_type"] == "text"
    assert "Hello" in captured["json"]["content"]["text"]


def test_send_news_api_error(monkeypatch) -> None:
    notifier = FeishuNotifier("https://open.feishu.cn/open-apis/bot/v2/hook/token")
    monkeypatch.setattr(
        "app.notifier.feishu.requests.post",
        lambda *_args, **_kwargs: _MockResponse({"code": 999, "msg": "error"}),
    )

    assert notifier.send_news(_build_item()) is False


def test_send_news_network_error(monkeypatch) -> None:
    notifier = FeishuNotifier("https://open.feishu.cn/open-apis/bot/v2/hook/token")

    def _raise(*_args, **_kwargs):
        raise requests.ConnectionError("down")

    monkeypatch.setattr("app.notifier.feishu.requests.post", _raise)

    assert notifier.send_news(_build_item()) is False


def test_send_summary_success(monkeypatch) -> None:
    notifier = FeishuNotifier("https://open.feishu.cn/open-apis/bot/v2/hook/token")
    captured = {}

    def _mock_post(url: str, json: dict, timeout: int):
        captured["payload"] = json
        return _MockResponse({"code": 0})

    monkeypatch.setattr("app.notifier.feishu.requests.post", _mock_post)
    ok = notifier.send_summary(total_pending=8, sent_count=5, items=[_build_item()])
    assert ok is True
    assert "本轮抓到" in captured["payload"]["content"]["text"]
