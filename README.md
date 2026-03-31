# BRICS News Digest Skill

每日金砖国家及重要经济体新闻摘要技能，使用 World News API 获取实时新闻。

## 功能特点

- 🌍 覆盖 9 个国家：🇺🇸🇯🇵🇧🇷🇷🇺🇮🇳🇨🇳🇿🇦🇪🇬🇧🇩🇦🇪
- ⏰ 每天早上 8:00 自动执行
- 📰 收集：宏观经济 + 金融市场 + 政治新闻
- 🤖 使用 AI 自动生成摘要
- 💾 自动上传到 IMA DailyNews

## 安装

1. 将此 skill 复制到 OpenClaw skills 目录
2. 配置环境变量
3. 设置定时任务

## 配置

### 环境变量

```bash
export WORLD_NEWS_API_KEY="your_api_key"
export IMA_OPENAPI_CLIENTID="your_client_id"
export IMA_OPENAPI_APIKEY="your_api_key"
export HTTP_PROXY="http://127.0.0.1:7897"
```

### 定时任务

每天早上 8:00 (北京时间) 自动执行。

## 使用

```bash
# 手动执行
openclaw run brics-news-digest
```

## 输出

- 英文新闻摘要报告
- 自动上传到 IMA DailyNews 笔记本和知识库
- Token 消耗：~3,000-3,500/天 (节省 99.7%)

## License

MIT
