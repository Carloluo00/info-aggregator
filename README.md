# Info Aggregator V1

本项目用于聚合 RSS 和静态网页资讯，并推送到飞书。

## 功能
- 本地管理面板（FastAPI + Jinja）
  - `/sources`：查看、启停、删除信息源
  - `/sources/new`：新增 RSS / Web 源
  - `/settings`：设置每轮推送上限和摘要策略
- 统一信息源存储在 SQLite `sources` 表
- 网页抓取支持静态列表页 + CSS 选择器
- 推送节流：每轮最多推送 N 条，超出发送摘要

## 安装
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 配置
```powershell
Copy-Item .env.example .env
```

核心变量：
- `FEISHU_WEBHOOK_URL`：飞书机器人 webhook
- `POLL_INTERVAL_SECONDS`：轮询间隔
- `SQLITE_PATH`：数据库路径
- `MAX_PUSH_PER_CYCLE`：每轮最多推送条数（默认 5）
- `SUMMARY_WHEN_EXCEED`：超限时是否发送摘要（默认 true）
- `RSS_URLS`：仅用于首次迁移到 `sources` 表

## 运行
单次运行：
```powershell
python -m app.main --once
```

定时运行：
```powershell
python -m app.main
```

启动管理面板（默认 `127.0.0.1:8000`）：
```powershell
python -m app.main --admin
```

指定面板端口：
```powershell
python -m app.main --admin --admin-port 8011
```

## 网页抓取规则
在新增 `web` 类型源时填写：
- `item_selector`：每条内容的容器选择器
- `title_selector`：标题节点选择器
- `link_selector`：链接节点选择器（需能取到 `href`）
- `published_selector`：可选，发布时间节点

示例：
- item: `.post`
- title: `.title`
- link: `a`
- published: `.date`

## 测试
```powershell
python -m pytest tests -q -p no:cacheprovider
```

## 常见问题
- `Admin mode requires uvicorn and fastapi installed`
  - 先执行 `pip install -r requirements.txt`
- 网页源无结果
  - 先用浏览器开发者工具验证 CSS 选择器是否匹配到节点
  - 检查链接是否在 `href` 属性中
- 一次推送过多
  - 在 `/settings` 中降低 `max_push_per_cycle`
