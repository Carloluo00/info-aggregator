# 信息源整合工具 MVP - 需求与计划

## 1. 项目目标
构建一个基于 Python 的信息源整合工具，定时抓取感兴趣资讯，并把新增内容推送到飞书群。

## 2. MVP 范围
- 输入：一组 RSS 源配置
- 处理：抓取、解析、去重、筛选
- 输出：把新增资讯发送到飞书机器人 Webhook
- 运行：本地定时任务（APScheduler）

## 3. 非目标（MVP 暂不做）
- 用户登录/多用户系统
- Web 后台管理界面
- 复杂规则引擎（如 AI 摘要、语义分类）
- 分布式部署

## 4. 技术栈
- Python 3.11+
- feedparser（RSS 解析）
- requests（HTTP 请求）
- APScheduler（定时调度）
- sqlite3（内置数据库，去重与状态保存）
- python-dotenv（环境变量配置）

## 5. 模块划分
1. 配置模块（config）
2. 存储模块（storage/db）
3. RSS 抓取模块（fetchers/rss_fetcher）
4. 飞书通知模块（notifier/feishu）
5. 调度编排模块（scheduler/jobs）
6. 主程序入口（main）

## 6. 模块顺序与测试闸门
每个模块开发完成后必须先通过对应测试，再继续下一模块。

1) 配置模块
- 完成标准：可从 `.env` 读取飞书 Webhook、轮询间隔、RSS 源列表
- 测试标准：配置加载单元测试通过

2) 存储模块
- 完成标准：可初始化 SQLite；可记录和判断“是否已推送”
- 测试标准：数据库读写/去重测试通过

3) RSS 抓取模块
- 完成标准：可拉取 RSS 并标准化为统一文章结构
- 测试标准：抓取解析测试通过（使用本地样例 RSS）

4) 飞书通知模块
- 完成标准：可按飞书消息卡片或文本格式发送
- 测试标准：请求构造与发送流程测试通过（mock 网络）

5) 调度编排模块
- 完成标准：一次任务可串起“抓取 -> 去重 -> 推送”；定时器可启动
- 测试标准：端到端流程测试通过（mock 抓取和推送）

6) 主程序入口
- 完成标准：命令行启动后正常调度运行
- 测试标准：启动冒烟测试通过

## 7. 目录结构
```text
app/
  __init__.py
  main.py
  config.py
  models.py
  fetchers/
    __init__.py
    rss_fetcher.py
  notifier/
    __init__.py
    feishu.py
  scheduler/
    __init__.py
    jobs.py
  storage/
    __init__.py
    db.py
tests/
  test_config.py
  test_db.py
  test_rss_fetcher.py
  test_feishu.py
  test_jobs.py
.env.example
requirements.txt
README.md
TODO.md
REQUIREMENTS_PLAN.md
```

## 8. 里程碑
- M1：文档与骨架
- M2：模块逐个实现并测试
- M3：本地联调与运行说明
