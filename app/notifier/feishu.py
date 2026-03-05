from __future__ import annotations

import requests

from app.models import NewsItem


class FeishuNotifier:
    def __init__(self, webhook_url: str, timeout: int = 10) -> None:
        self.webhook_url = webhook_url
        self.timeout = timeout

    @staticmethod
    def build_payload(item: NewsItem) -> dict:
        body = f"{item.title}\n{item.link}"
        if item.published:
            body = f"{body}\n发布时间: {item.published}"
        return {
            "msg_type": "text",
            "content": {
                "text": body,
            },
        }

    def send_news(self, item: NewsItem) -> bool:
        payload = self.build_payload(item)
        try:
            response = requests.post(self.webhook_url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            return data.get("code", -1) == 0
        except requests.RequestException:
            return False
