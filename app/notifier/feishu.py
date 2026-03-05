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
        return self._post_payload(payload)

    @staticmethod
    def build_summary_payload(total_pending: int, sent_count: int, items: list[NewsItem]) -> dict:
        overflow = max(total_pending - sent_count, 0)
        lines = [
            f"本轮抓到 {total_pending} 条新增，已推送 {sent_count} 条。",
            f"剩余 {overflow} 条将在后续轮次继续推送。",
        ]
        preview = items[: min(len(items), 5)]
        if preview:
            lines.append("未推送示例：")
            for item in preview:
                lines.append(f"- {item.title}")
                lines.append(f"  {item.link}")
        return {
            "msg_type": "text",
            "content": {"text": "\n".join(lines)},
        }

    def send_summary(self, total_pending: int, sent_count: int, items: list[NewsItem]) -> bool:
        payload = self.build_summary_payload(total_pending, sent_count, items)
        return self._post_payload(payload)

    def _post_payload(self, payload: dict) -> bool:
        try:
            response = requests.post(self.webhook_url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            return data.get("code", -1) == 0
        except requests.RequestException:
            return False
