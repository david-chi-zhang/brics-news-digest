# Daily BRICS+ News Digest - 任务执行指南

## 🔧 翻译配置

### 支持的语言
脚本内置翻译字典支持以下语言：
- **葡萄牙语 (pt)**: 巴西新闻
- **俄语 (ru)**: 俄罗斯新闻
- **日语 (ja)**: 日本新闻
- **法语 (fr)**: 法国/欧盟新闻
- **中文 (zh)**: 中国新闻
- **阿拉伯语 (ar)**: 埃及/中东新闻
- **印地语 (hi)**: 印度新闻

### 翻译字典位置
`/home/admin/openclaw/workspace/scripts/process_brics_news_v3.py`

### 扩展翻译字典
```python
TRANSLATION_DICT = {
    "pt": {"faz": "makes", "sobre": "about", ...},
    "ru": {"Сырский": "Syrsky", "бросил в бой": "threw into battle", ...},
    ...
}
```

### 添加新语言
1. 在 `TRANSLATION_DICT` 中添加新语言条目
2. 在 `detect_language()` 函数中添加语言检测逻辑
3. 在 `COUNTRY_KEYWORDS` 中添加该语言的国家关键词

---

## ⚠️ 历史错误记录（必须避免！）

### 错误 1: 非英语新闻处理 ❌
**问题**: 巴西新闻（葡萄牙语）、俄罗斯新闻（俄语）直接以原文收录
**错误示例**:
- 葡萄牙语: "Homem é baleado após ameaça e ataque a tiros..."
- 俄语: "Разъединенное Королевство. Как Британия перестала..."

**正确做法** ✅:
- **翻译**非英语新闻的标题和摘要为英语
- 使用翻译 API 或人工翻译
- 保持原文链接和来源信息

---

### 错误 2: 体育新闻未被排除 ❌
**问题**: 足球比赛新闻被收录为"政治/地缘"新闻
**错误示例**:
- "Danilo é sincero sobre derrota do Flamengo: 'Vergonha'" (足球赛后采访)
- "Discussão após jogo entre Bragantino x Flamengo" (足球比赛争议)

**正确做法** ✅:
- 排除关键词: football, soccer, futebol, jogo, partida, match, game
- 排除球队名: Flamengo, Palmeiras, Santos, Corinthians, São Paulo
- 排除体育分类: category == "sports"

---

### 错误 3: 无关新闻被收录 ❌
**问题**: 新闻内容与目标国家无关
**错误示例**:
- 日本分类下出现波兰新闻: "Metals of the future: copper and silver flow beneath Poland's surface"
- 欧盟分类下出现英国新闻（英国已脱欧）

**正确做法** ✅:
- 验证新闻内容是否包含该国关键词
- 检查新闻来源国是否与分类匹配
- 地缘政治新闻可以跨国家，但必须有明确关联

---

### 错误 4: 缺少摘要的新闻被收录 ❌
**问题**: 多条新闻显示 "No summary available"
**错误示例**:
- "Summary: No summary available."

**正确做法** ✅:
- 必须有有效摘要（>20 字符）
- 如果 API 未提供摘要，从正文提取前 1-2 句
- 如果正文也无法获取，跳过该新闻

---

### 错误 5: IMA 上传未指定笔记本 ❌
**问题**: 笔记被创建在默认位置，而非 DailyNews 笔记本
**错误配置**:
```bash
# 错误：未指定 folder_id
curl -X POST "https://ima.qq.com/openapi/note/v1/import_doc" \
  -d '{"content_format": 1, "content": "..."}'
```

**正确配置** ✅:
```bash
# 正确：指定 DailyNews 笔记本 folder_id
curl -X POST "https://ima.qq.com/openapi/note/v1/import_doc" \
  -d '{"content_format": 1, "content": "...", "folder_id": "foldere1b18e698eae2e88"}'
```

---

### 错误 6: 分类不准确 ❌
**问题**: 新闻分类错误
**错误示例**:
- 国防/军事新闻被分类为"Financial Markets"
- 体育新闻被分类为"Politics/Geopolitics"

**正确分类规则** ✅:
| 分类 | 关键词 |
|------|--------|
| Financial Markets | stock, market, bond, currency, oil, gold, crypto, exchange, share, banking, investment, fund, trading, ipo, earnings |
| Macroeconomics | gdp, inflation, employment, trade, economic, economy, central bank, pmi, cpi, deficit, fiscal, monetary, export, import, tariff, wage |
| Politics/Geopolitics | 其他政治、外交、军事、政策新闻 |

---

## ✅ 正确执行流程

### Step 1: 获取新闻
```bash
export WORLD_NEWS_API_KEY="96798c19fe364458ba4f9dbe55477115"
export HTTP_PROXY="http://127.0.0.1:7897"

for country in eu us jp br ru in cn za eg bd ae; do
  curl -s -x "$HTTP_PROXY" \
    "https://api.worldnewsapi.com/search-news?source-countries=$country&api-key=$WORLD_NEWS_API_KEY&from=$YESTERDAY&to=$TODAY&number=10" \
    > "/tmp/news_collection/${country}.json"
done
```

### Step 2: 筛选与翻译
```python
# 对每条新闻执行：
# 1. 检查语言，非英语则翻译标题和摘要
# 2. 排除体育/娱乐新闻
# 3. 验证与该国相关性
# 4. 确保有有效摘要
# 5. 正确分类
```

### Step 3: 生成报告
- 全英文报告
- 每国最多 5 条新闻
- 包含原文链接
- 格式符合模板

### Step 4: 上传 IMA
```bash
export IMA_OPENAPI_CLIENTID="0acab5edb61ac4876ff36cb9b20831b7"
export IMA_OPENAPI_APIKEY="lh0q+b9rbrt7R/2QmINAmw6Z8rmydv5zuvjw9wC+tF4rOD8fTnn0rd0GuhWtGw9Ab6+AKJhN9g=="

curl -X POST "https://ima.qq.com/openapi/note/v1/import_doc" \
  -H "ima-openapi-clientid: $IMA_OPENAPI_CLIENTID" \
  -H "ima-openapi-apikey: $IMA_OPENAPI_APIKEY" \
  -d '{
    "content_format": 1,
    "content": "...",
    "folder_id": "foldere1b18e698eae2e88"
  }'
```

---

## 📊 IMA 配置

| 配置项 | 值 |
|--------|-----|
| API Base URL | `https://ima.qq.com/openapi/note/v1` |
| DailyNews Notebook ID | `foldere1b18e698eae2e88` |
| Client ID | `0acab5edb61ac4876ff36cb9b20831b7` |
| API Key | `lh0q+b9rbrt7R/2QmINAmw6Z8rmydv5zuvjw9wC+tF4rOD8fTnn0rd0GuhWtGw9Ab6+AKJhN9g==` |

---

## 🔍 质量检查清单

在发送报告前，逐项检查：

- [ ] 所有新闻标题为英语（非英语已翻译）
- [ ] 所有新闻摘要为英语（非英语已翻译）
- [ ] 无体育新闻（足球、篮球、棒球等）
- [ ] 无娱乐新闻（名人、电影、音乐等）
- [ ] 每条新闻与所属分类国家相关
- [ ] 每条新闻有有效摘要（>20 字符）
- [ ] 分类准确（金融/宏观/政治）
- [ ] 每国不超过 5 条新闻
- [ ] 包含原文链接
- [ ] IMA 上传指定了 folder_id

---

## 📝 报告格式模板

```markdown
# Daily BRICS+ Economic & Political News Digest
**Date:** Month DD, YYYY  
**Coverage Period:** Past 24 Hours  
**Countries Covered:** 🇪🇺 Eurozone, 🇺🇸 US, 🇯🇵 Japan, 🇧🇷 Brazil, 🇷🇺 Russia, 🇮🇳 India, 🇨🇳 China, 🇿🇦 South Africa, 🇪🇬 Egypt, 🇧🇩 Bangladesh, 🇦🇪 UAE

---

## 🇪🇺 Eurozone

### [Category]
**1. [Headline in English]**
- **Source:** [Author](URL)
- **Published:** YYYY-MM-DD HH:MM:SS
- **Summary:** [Summary in English, 1-2 sentences]

---

## Summary Statistics

| Metric | Value |
|--------|-------|
| **Total News Items** | XX |
| **Countries/Regions** | 11 |
| **Politics/Geopolitics** | XX |
| **Macroeconomics** | XX |
| **Financial Markets** | XX |

**Report Generated:** Month DD, YYYY, HH:MM AM/PM (Asia/Shanghai)  
**Source:** World News API
```
