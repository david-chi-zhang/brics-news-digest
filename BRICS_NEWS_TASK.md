# BRICS+ 每日新闻收集任务

## 任务概述

**定时执行**: 每天早上 8:00 (Asia/Shanghai)  
**任务 ID**: `4ece854e-dad5-4e21-952a-455589f21b3e`  
**配置文件**: `~/.openclaw/cron/jobs.json`

---

## 完整执行流程

### 1. 获取新闻 (World News API)

```bash
export WORLD_NEWS_API_KEY="96798c19fe364458ba4f9dbe55477115"
export HTTP_PROXY="http://127.0.0.1:7897"

COUNTRIES="eu us jp br ru in cn za eg bd ae"
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d)
TODAY=$(date +%Y-%m-%d)

for country in $COUNTRIES; do
  curl -s -x "$HTTP_PROXY" \
    "https://api.worldnewsapi.com/search-news?source-countries=$country&api-key=$WORLD_NEWS_API_KEY&from=$YESTERDAY&to=$TODAY&number=10" \
    > "/tmp/news_collection/${country}.json"
done
```

**产出**: 11 国 × 10 条 = 110 条新闻

---

### 2. 语言检测

**检测逻辑**:
- 计算非 ASCII 字符比例
- 按 Unicode 范围识别具体语言（俄语/阿拉伯语/葡萄牙语/日语/中文/印地语）

**典型分布**:
- 英语新闻：~60-70 条
- 非英语新闻：~40-50 条（需要翻译）

---

### 3. AI 翻译（⚠️ 关键步骤）

**核心要求**:
- ✅ **所有非英语标题必须翻译为英语**（不能保留原文）
- ✅ **所有非英语摘要必须翻译为英语**（不能保留原文）
- ✅ **使用 AI 大模型翻译**（无需外部 API）
- ✅ **翻译后不显示语言标记**（全文英语）

**翻译流程**:
```python
# 1. 收集需要翻译的文本
texts_to_translate = []
for item in news_list:
    if detect_language(title) != "en":
        texts_to_translate.append({"field": "title", "text": title})
    if summary and detect_language(summary) != "en":
        texts_to_translate.append({"field": "summary", "text": summary})

# 2. 使用 AI 大模型批量翻译
prompt = "请翻译以下新闻标题和摘要为英语..."
translated_texts = call_ai_model(prompt)

# 3. 应用翻译结果（直接替换为英语）
for trans in translated_texts:
    news_list[trans["index"]][trans["field"]] = trans["translated"]
```

**翻译示例**:
| 原文 | 语言 | 翻译后 |
|------|------|--------|
| `Треть россиян не доверяют телемедицине` | 俄语 | `One third of Russians do not trust telemedicine` |
| `إسرائيل تحتجز 4 من جنودها` | 阿拉伯语 | `Israel detains 4 of its soldiers` |
| `Governo zera impostos da aviação` | 葡萄牙语 | `Government zeroes aviation taxes` |
| `きょう予算が成立見込み` | 日语 | `Budget expected to pass today` |
| `中国成为世界 Token 工厂` | 中文 | `China becomes world Token factory` |

---

### 4. 筛选过滤

**排除规则**:
- 体育新闻（nfl, nba, cricket, football, soccer 等）
- 娱乐新闻（celebrity, movie, music award 等）
- 娱乐网站（perezhilton.com, tmz.com 等）

**相关性检测**:
- 检查国家关键词
- 检查 URL 域名（.br, .ru, .in 等）

**摘要要求**:
- API 有摘要（≥20 字符）→ 直接使用
- API 无摘要 → 从正文提取前 1-2 句
- 仍无摘要 → 排除该新闻

**产出**: 约 55 条新闻（排除 50-60 条）

---

### 5. 分类整理

**分类规则**:
- **Financial Markets**: stock, market, bond, currency, oil, gold, banking, investment
- **Macroeconomics**: gdp, inflation, employment, trade, economy, cpi, wage
- **Politics/Geopolitics**: 其他政治、外交、军事、政策新闻

**典型分布**:
- Politics/Geopolitics: 40-45 条（70-80%）
- Macroeconomics: 8-12 条（15-20%）
- Financial Markets: 2-5 条（5-10%）

---

### 6. 生成报告

**Markdown 格式**:
```markdown
# Daily BRICS+ Economic & Political News Digest
**Date:** April 07, 2026  
**Coverage Period:** Past 24 Hours  

---

## 🇪🇺 Eurozone

### [Politics/Geopolitics]
**1. EU foreign policy shambles triggers calls for radical overhaul**
- **Source:** [Nicholas Vinocur](https://www.politico.eu/article/...)
- **Published:** 2026-04-06
- **Summary:** From Ukraine funding to Iran and Russia...

---

## Summary Statistics

| Metric | Value |
|--------|-------|
| **Total News Items** | 55 |
| **Countries/Regions** | 11 |
```

**关键格式要求**:
- 国家标题：`## 🇪🇺 Eurozone`（国旗 + 国家名）
- 分类：`### [Politics/Geopolitics]`（**方括号包裹**）
- 新闻标题：`**1. 标题**`（**粗体 + 编号**）
- 来源：`- **Source:** [作者](URL)`（**Markdown 链接**）
- 摘要：`- **Summary:** 内容`（1-2 句话）

---

### 7. IMA 上传

**环境变量**:
```bash
export IMA_OPENAPI_CLIENTID="0acab5edb61ac4876ff36cb9b20831b7"
export IMA_OPENAPI_APIKEY="lh0q+b9rbrt7R/2QmINAmw6Z8rmydv5zuvjw9wC+tF4rOD8fTnn0rd0GuhWtGw9Ab6+AKJhN9g=="
```

**API 调用**:
```bash
content=$(cat /home/admin/openclaw/workspace/daily-brics-news-YYYY-MM-DD.md)

curl -s -X POST "https://ima.qq.com/openapi/note/v1/import_doc" \
  -H "ima-openapi-clientid: $IMA_OPENAPI_CLIENTID" \
  -H "ima-openapi-apikey: $IMA_OPENAPI_APIKEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"content_format\": 1,
    \"content\": $(echo "$content" | jq -Rs .),
    \"folder_id\": \"foldere1b18e698eae2e88\"
  }"
```

**⚠️ 重要**: 必须指定 `folder_id: "foldere1b18e698eae2e88"`（DailyNews 笔记本）

---

## 质量检查清单

执行完成后，**逐项检查**:

- [ ] **所有新闻标题为英语**（非英语已翻译）
- [ ] **所有新闻摘要为英语**（非英语已翻译）
- [ ] **无语言标记**（不显示 [RU]/[AR] 等）
- [ ] **原文链接可用**（Markdown 格式）
- [ ] **分类使用方括号**（`[Category]`）
- [ ] **无体育/娱乐新闻**
- [ ] **每条新闻与该国相关**
- [ ] **每条新闻有有效摘要**（≥20 字符）
- [ ] **每国不超过 5 条新闻**
- [ ] **IMA 上传指定 folder_id**

---

## 常见错误及避免方法

### ❌ 错误 1: 标题保留原文
**错误**:
```markdown
**1. [RU] Треть россиян не доверяют телемедицине**
```

**正确** ✅:
```markdown
**1. One third of Russians do not trust telemedicine**
```

### ❌ 错误 2: 缺少原文链接
**错误**:
```markdown
- **Source:** Nicholas Vinocur
```

**正确** ✅:
```markdown
- **Source:** [Nicholas Vinocur](https://www.politico.eu/article/...)
```

### ❌ 错误 3: 分类无方括号
**错误**:
```markdown
### Politics/Geopolitics
```

**正确** ✅:
```markdown
### [Politics/Geopolitics]
```

### ❌ 错误 4: IMA 上传未指定 folder_id
**错误**:
```bash
-d '{"content_format": 1, "content": "..."}'
```

**正确** ✅:
```bash
-d '{"content_format": 1, "content": "...", "folder_id": "foldere1b18e698eae2e88"}'
```

---

## 执行时间线（典型）

| 步骤 | 耗时 | 说明 |
|------|------|------|
| 1. 获取新闻 | 30-60 秒 | 11 国 API 请求 |
| 2. 语言检测 | 5-10 秒 | 110 条检测 |
| 3. AI 翻译 | 30-60 秒 | 20-30 条翻译 |
| 4. 筛选过滤 | 10-20 秒 | 排除体育/娱乐 |
| 5. 分类整理 | 5-10 秒 | 金融/宏观/政治 |
| 6. 生成报告 | 5-10 秒 | Markdown 格式化 |
| 7. IMA 上传 | 5-10 秒 | API 调用 |
| **总计** | **90-180 秒** | 约 1.5-3 分钟 |

---

## 参考资料

- **完整技能文档**: `~/openclaw/workspace/skills/brics-news-collector/SKILL.md`
- **处理脚本**: `~/openclaw/workspace/scripts/process_brics_news_v3.py`
- **翻译模块**: `~/openclaw/workspace/scripts/ai_translate.py`
- **任务配置**: `~/.openclaw/cron/jobs.json`
