# 信息源整合工具（MVP）

一个基于 Python 的资讯整合脚本：定时抓取 RSS，去重后推送到飞书机器人。

## 1. 功能
- 支持多个 RSS 源抓取
- SQLite 去重，避免重复推送
- 飞书 Webhook 推送
- 支持 `--once` 单次运行与定时轮询

## 2. 环境要求
- Python 3.11+
- Windows / macOS / Linux

## 3. 安装
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 4. 配置
复制 `.env.example` 为 `.env`，并填写：

- `FEISHU_WEBHOOK_URL`：飞书自定义机器人 webhook
- `FEISHU_BOT_SECRET`：可选（MVP 当前未启用签名）
- `POLL_INTERVAL_SECONDS`：轮询间隔（秒）
- `RSS_URLS`：逗号分隔的 RSS 地址
- `SQLITE_PATH`：本地数据库路径（默认 `data/app.db`）

## 5. 运行
单次执行（推荐先验证）：
```powershell
python -m app.main --once
```

定时运行：
```powershell
python -m app.main
```

## 6. 测试
按模块测试：
```powershell
python -m pytest tests/test_config.py -q -p no:cacheprovider
python -m pytest tests/test_db.py -q -p no:cacheprovider
python -m pytest tests/test_rss_fetcher.py -q -p no:cacheprovider
python -m pytest tests/test_feishu.py -q -p no:cacheprovider
python -m pytest tests/test_jobs.py -q -p no:cacheprovider
```

全量测试：
```powershell
python -m pytest tests -q -p no:cacheprovider
```

## 7. 下一步建议
- 为飞书机器人加签名（timestamp + sign）
- 增加关键词过滤（白名单/黑名单）
- 增加网页抓取兜底源（无 RSS 场景）
