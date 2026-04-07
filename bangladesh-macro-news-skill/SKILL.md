---
name: bangladesh-macro-news
description: >
  孟加拉宏观经济新闻收集与摘要工具。从指定新闻源收集过去 7-10 天的
  孟加拉宏观经济相关新闻，生成结构化摘要文档。
  
  **触发场景**：
  - "帮我总结过去 7 天孟加拉宏观经济新闻"
  - "收集孟加拉经济数据"
  - "孟加拉宏观经济动态"
  - 用户提到"孟加拉"+"新闻"/"经济"/"macro"
  
  **默认数据源**：https://thefinancialexpress.com.bd/page/economy/bangladesh
---

# 孟加拉宏观经济新闻收集 Skill

## 任务概述

从指定新闻源收集孟加拉宏观经济相关新闻，生成结构化摘要文档（飞书文档）。

## 数据源

**默认新闻源**：
- https://thefinancialexpress.com.bd/page/economy/bangladesh

**可扩展新闻源**：
- https://www.thedailystar.net/business/news
- https://www.tbsnews.net/economy
- https://www.dhakatribune.com/business

## 关注主题

| 主题 | 关键词 |
|------|--------|
| GDP 增长 | GDP, growth, economic output |
| 工业生产 | industrial production, manufacturing, factory |
| 货币政策 | monetary policy, Bangladesh Bank, interest rate, repo rate |
| 财政政策 | fiscal policy, budget, deficit, taxation |
| 贸易 | trade, export, import, CEPA, LDC graduation |
| 汇率 | exchange rate, BDT, USD, currency, forex reserve |
| 国际收支 | balance of payments, current account |
| 通胀 | inflation, CPI, food price, non-food |
| 侨汇 | remittance, expatriate, worker |
| 外资 | FDI, foreign investment, investment board |

## 执行流程

### Step 1: 获取列表页内容

```python
# 使用 web_fetch 获取列表页（不要用 browser.snapshot！）
web_fetch(
    url="https://thefinancialexpress.com.bd/page/economy/bangladesh",
    extractMode="markdown",
    maxChars=5000
)
```

### Step 2: 提取并过滤新闻链接

从 markdown 中提取：
- 新闻标题
- 新闻链接
- 发布日期（如果有）

**过滤规则**：
- 只保留过去 7-10 天的新闻
- 使用关键词匹配宏观经济主题
- 排除明显不相关的（体育、娱乐等）

### Step 3: 并行获取文章全文

```python
# 并行 fetch 所有相关文章（不要串行！）
# 每篇文章限制 3000 字符
for article_url in relevant_urls:
    web_fetch(
        url=article_url,
        extractMode="markdown",
        maxChars=3000
    )
```

### Step 4: 生成摘要

对每篇文章：
- 提取核心信息（50 字英文摘要）
- 识别关键数据（GDP 增长率、通胀率、外汇储备等）
- 标记主题分类

### Step 5: 创建飞书文档

**文档结构**：

```markdown
# 孟加拉宏观经济新闻摘要
**时间范围**: YYYY-MM-DD ~ YYYY-MM-DD
**生成时间**: YYYY-MM-DD HH:MM

## 📰 重要新闻

### [新闻标题 1]
- **来源**: The Financial Express
- **日期**: 2026-03-15
- **链接**: https://...
- **摘要**: 50 字英文摘要...

### [新闻标题 2]
...

## 📊 关键数据摘要

| 指标 | 数值 | 趋势 | 来源 |
|------|------|------|------|
| GDP 增长率 | X.X% | ↑ | 文章链接 |
| 通胀率 (CPI) | X.X% | ↓ | 文章链接 |
| 外汇储备 | $XX 亿 | → | 文章链接 |

## 🎯 主题总结

1. **货币政策**: Bangladesh Bank 维持利率不变...
2. **贸易**: 出口增长 X%，主要得益于...
3. **汇率**: BDT 对 USD 贬值 X%...
4. **通胀**: CPI 降至 X%，食品价格...

---
*本摘要由 AI 自动生成 | 数据源：The Financial Express*
```

## 使用示例

### 基础用法

```
帮我总结过去 7 天孟加拉宏观经济新闻
```

### 自定义时间范围

```
收集过去 10 天孟加拉经济数据
```

### 自定义新闻源

```
从 The Daily Star 收集孟加拉经济新闻
```

## Token 优化要点

### ✅ 正确做法

1. **使用 web_fetch 而非 browser**
   - web_fetch 返回纯文本/markdown
   - browser.snapshot 返回完整 DOM，token 消耗高 5-10 倍

2. **两阶段过滤**
   - 阶段 1: 只 fetch 列表页，用标题过滤
   - 阶段 2: 只 fetch 相关文章全文

3. **限制返回长度**
   ```yaml
   maxChars: 5000  # 列表页
   maxChars: 3000  # 文章全文
   ```

4. **并行处理**
   - 同时 fetch 多篇文章
   - 不要串行等待

5. **精简输出**
   - 每条新闻 50 字摘要
   - 用表格展示数据
   - 避免重复内容

### ❌ 避免的做法

1. 使用 browser.snapshot 获取列表页
2. fetch 所有文章而不用标题过滤
3. 串行处理独立任务
4. 生成冗长文档（超过 3000 字）

## 飞书文档创建

使用 `feishu_create_doc` 创建文档：

```python
feishu_create_doc(
    title="孟加拉宏观经济新闻摘要 - YYYY-MM-DD",
    markdown="[完整文档内容]",
    folder_token="[可选：指定文件夹]"
)
```

## 定时任务（可选）

使用 cron 设置自动收集：

```python
# 每天早上 9 点执行
cron.add(
    schedule={"kind": "cron", "expr": "0 9 * * *"},
    payload={
        "kind": "agentTurn",
        "message": "帮我总结过去 24 小时孟加拉宏观经济新闻"
    },
    sessionTarget="isolated"
)
```

## 故障排查

### 问题 1: 网页无法访问
**解决**: 使用 Jina Reader 代理
```
https://r.jina.ai/https://thefinancialexpress.com.bd/page/economy/bangladesh
```

### 问题 2: 找不到相关新闻
**解决**: 
- 扩大时间范围（7 天 → 14 天）
- 增加新闻源
- 放宽关键词过滤

### 问题 3: Token 超限
**解决**:
- 减少 maxChars
- 减少 fetch 的文章数量
- 分多次执行

## 扩展功能

### 1. 多新闻源对比
同时从多个新闻源收集，对比报道角度

### 2. 情感分析
对新闻进行正面/负面/中性分类

### 3. 数据可视化
将关键数据生成图表（需要额外工具）

### 4. 飞书多维表格
结构化存储历史数据，支持趋势分析

---

## 更新记录
- 2026-03-20: 初始版本，基于实际任务经验
- 依赖：web_fetch, feishu_create_doc
