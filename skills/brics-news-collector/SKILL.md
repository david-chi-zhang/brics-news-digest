# BRICS+ 每日新闻收集技能

## 技能描述

自动收集并整理 11 个金砖国家及重要经济体的每日经济新闻，生成英文摘要报告并上传至 IMA。

**触发条件**:
- 定时任务：每天早上 8:00 (Asia/Shanghai)
- 手动触发：用户要求"收集今日新闻"、"执行新闻任务"等

---

## ⚠️ 核心原则（最高优先级）

### 数据完整性承诺

1. **绝不编造任何数据** ❌
   - 不编造新闻标题
   - 不编造原文链接
   - 不编造摘要内容
   - 不使用假链接（如 example.com）

2. **严格分类** ❌
   - 中国新闻不能包含日本新闻
   - 每条新闻必须与所属分类国家相关
   - 通过 URL 域名和国家关键词验证

3. **API 不可用时的处理** ⚠️
   - API 返回"failure" → 明确标注"无数据"
   - 不编造任何新闻填充
   - 报告中明确说明哪些国家 API 不可用
   - 宁可报告不完整，也绝不编造数据

4. **排除规则** ❌
   - 体育新闻（NBA、足球、板球等）必须排除
   - 娱乐新闻（明星、综艺、八卦等）必须排除
   - 生活方式（星座、 horoscope 等）必须排除

---

## 完整执行流程

### Step 1: 获取新闻 (World News API)

```bash
# 环境变量
export WORLD_NEWS_API_KEY="96798c19fe364458ba4f9dbe55477115"
export HTTP_PROXY="http://127.0.0.1:7897"

# 11 个国家代码
COUNTRIES="eu us jp br ru in cn za eg bd ae"

# 日期范围
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d)
TODAY=$(date +%Y-%m-%d)

# 获取新闻（每国 10 条）
for country in $COUNTRIES; do
  curl -s -x "$HTTP_PROXY" \
    "https://api.worldnewsapi.com/search-news?source-countries=$country&api-key=$WORLD_NEWS_API_KEY&from=$YESTERDAY&to=$TODAY&number=10&sort-by=publish_date" \
    > "/tmp/news_collection/${country}.json"
  
  # 检查 API 状态
  status=$(jq -r '.status // "no_status"' "/tmp/news_collection/${country}.json")
  if [ "$status" = "failure" ] || [ "$status" = "error" ]; then
    echo "  $country: API 不可用 (status: $status)"
  else
    count=$(jq -r '.news | length // 0' "/tmp/news_collection/${country}.json")
    echo "  $country: $count 条"
  fi
done
```

**API 返回字段**:
| 字段 | 说明 | 可用率 |
|------|------|--------|
| `title` | 新闻标题 | 100% ✅ |
| `url` | 原文链接 | 100% ✅ |
| `summary` | 新闻摘要 | 60-70% ⚠️ |
| `source` | 作者/媒体 | 30-40% ⚠️ |
| `published_date` | 发布时间 | 30-40% ⚠️ |
| `text` | 正文前 200-500 字符 | 100% ✅ |
| `language` | 语言代码 | 50-60% ⚠️ |
| `category` | 分类 | 20-30% ⚠️ |

---

### Step 2: API 数据验证（⚠️ 新增关键步骤）

```python
def validate_api_response(data, country_code):
    """验证 API 返回的数据"""
    if not data:
        return False, "API 返回空数据"
    
    status = data.get('status')
    if status in ['failure', 'error']:
        return False, f"API 返回失败状态：{status}"
    
    news_list = data.get('news', [])
    if not news_list:
        return False, "API 返回空新闻列表"
    
    # 检查第一条新闻是否有真实数据
    first_news = news_list[0]
    if not first_news.get('title'):
        return False, "新闻标题为空"
    
    if not first_news.get('url') or 'example.com' in first_news.get('url', ''):
        return False, "新闻链接缺失或为假链接"
    
    return True, "数据验证通过"
```

**验证规则**:
- ✅ API status 必须为"ok"或"success"
- ✅ news 列表不能为空
- ✅ 新闻必须有真实标题
- ✅ 新闻链接不能包含"example.com"
- ❌ 验证失败 → 标注该国"API 不可用"，不编造数据

---

### Step 3: 语言检测

```python
def detect_language(text):
    if not text:
        return "en"
    
    # 计算非 ASCII 字符比例
    non_ascii = sum(1 for c in text if ord(c) > 127)
    ratio = non_ascii / len(text)
    
    if ratio < 0.05:  # 95% 以上是 ASCII
        return "en"
    
    # 按 Unicode 范围检测具体语言
    if any('\u0400' <= c <= '\u04ff' for c in text):
        return "ru"  # 俄语（西里尔字母）
    if any('\u4e00' <= c <= '\u9fff' for c in text):
        return "zh"  # 中文（汉字）
    if any('\u0600' <= c <= '\u06ff' for c in text):
        return "ar"  # 阿拉伯语
    if any(c in text.lower() for c in "ãõç"):
        return "pt"  # 葡萄牙语
    if any('\u3040' <= c <= '\u30ff' for c in text):
        return "ja"  # 日语（平假名/片假名）
    if any('\u0900' <= c <= '\u097f' for c in text):
        return "hi"  # 印地语（天城文）
    
    return "other"
```

---

### Step 4: AI 翻译（关键步骤）

**⚠️ 重要要求**:
- **标题必须翻译为英语**（不能保留原文）
- **摘要必须翻译为英语**（不能保留原文）
- **使用 AI 大模型翻译**（无需外部 API）
- **翻译后不显示语言标记**（全文英语）

```python
# 1. 收集需要翻译的文本
texts_to_translate = []

for i, item in enumerate(news_list):
    title = item.get("title", "")
    summary = item.get("summary", "")
    
    # 检测标题语言
    title_lang = detect_language(title)
    if title_lang != "en":
        texts_to_translate.append({
            "index": i,
            "field": "title",
            "text": title[:150],
            "lang": title_lang
        })
    
    # 检测摘要语言
    if summary:
        summary_lang = detect_language(summary)
        if summary_lang != "en":
            texts_to_translate.append({
                "index": i,
                "field": "summary",
                "text": summary[:150],
                "lang": summary_lang
            })

# 2. 使用 AI 大模型批量翻译
prompt = """请翻译以下新闻标题和摘要为英语。保持简洁、准确。
格式要求：按顺序返回翻译结果，每条一行，不要解释。

"""
for i, item in enumerate(texts_to_translate, 1):
    prompt += f"{i}. [{item['lang'].upper()}] {item['text']}\n"

# 调用 AI 大模型翻译
translated_texts = call_ai_model(prompt)

# 3. 应用翻译结果（直接替换为英语）
for trans in translated_texts:
    idx = trans["index"]
    field = trans["field"]
    translated = trans["translated"]
    news_list[idx][field] = translated  # 直接替换为英语翻译
```

**翻译示例**:
| 原文 | 语言 | 翻译后 |
|------|------|--------|
| `Треть россиян не доверяют телемедицине` | 俄语 | `One third of Russians do not trust telemedicine` |
| `إسرائيل تحتجز 4 من جنودها` | 阿拉伯语 | `Israel detains 4 of its soldiers` |
| `Governo zera impostos da aviação` | 葡萄牙语 | `Government zeroes aviation taxes` |
| `きょう予算が成立見込み` | 日语 | `Budget expected to pass today` |
| `中国成为"世界 Token 工厂"` | 中文 | `China becomes "world Token factory"` |

---

### Step 5: 筛选过滤

**排除规则**:
```python
EXCLUDE_SPORTS = ["nfl", "nba", "mlb", "nhl", "premier league", 
                  "cricket match", "ipl", "football", "soccer",
                  "denver nuggets", "basketball", "baseball"]
EXCLUDE_ENTERTAINMENT = ["celebrity", "movie premiere", "music award", 
                         "snl", "saturday night", "oscar", "grammy",
                         "minnie driver", "kanye west", "ye "]
EXCLUDE_LIFESTYLE = ["horoscope", "lifestyle", "entertainment"]
EXCLUDE_SITES = ["perezhilton.com", "tmz.com", "eonline.com"]
```

**筛选逻辑**:
```python
def should_exclude(news_item):
    title = (news_item.get("title") or "").lower()
    url = (news_item.get("url") or "").lower()
    category = (news_item.get("category") or "").lower()
    full_text = title + " " + url
    
    # 检查分类字段
    if category in EXCLUDE_LIFESTYLE:
        return True, f"分类排除：{category}"
    
    # 检查体育
    for kw in EXCLUDE_SPORTS:
        if kw in full_text:
            return True, f"体育关键词：{kw}"
    
    # 检查娱乐
    for kw in EXCLUDE_ENTERTAINMENT:
        if kw in full_text:
            return True, f"娱乐关键词：{kw}"
    
    # 检查网站
    for site in EXCLUDE_SITES:
        if site in url:
            return True, f"娱乐网站：{site}"
    
    return False, ""
```

**相关性检测**:
```python
COUNTRY_KEYWORDS = {
    "br": ["brazil", "brasileiro", "brasilia", "sao paulo", "petrobras"],
    "ru": ["russia", "russian", "moscow", "kremlin", "россия"],
    "in": ["india", "indian", "new delhi", "mumbai", "भारत"],
    "cn": ["china", "chinese", "beijing", "shanghai", "中国"],
    # ... 其他国家
}

def is_relevant(news_item, country_code):
    title = news_item.get("title", "").lower()
    text = news_item.get("text", "").lower()
    url = news_item.get("url", "").lower()
    full_text = title + " " + text + " " + url
    
    # 检查国家关键词
    for kw in COUNTRY_KEYWORDS.get(country_code, []):
        if kw in full_text:
            return True
    
    # 通过 URL 域名判断
    url_country_map = {
        "br": [".br", "globo.com"],
        "ru": [".ru", "ria.ru"],
        "jp": [".jp", "japantimes.co.jp", "asahi.com"],
        "cn": [".cn", "chinadaily.com.cn"],
    }
    for domain in url_country_map.get(country_code, []):
        if domain in url:
            return True
    
    return False
```

**摘要要求**:
- API 有摘要（≥20 字符）→ 直接使用
- API 无摘要 → 从正文提取前 1-2 句
- 仍无摘要 → 排除该新闻

---

### Step 6: 分类整理

```python
FINANCE_KEYWORDS = ["stock", "market", "bond", "currency", "oil", "gold", 
                    "banking", "investment", "fund", "trading", "ipo"]
ECON_KEYWORDS = ["gdp", "inflation", "employment", "trade", "economy", 
                 "central bank", "pmi", "cpi", "wage", "tariff"]

def categorize(news_item):
    title = news_item.get("title", "").lower()
    text = news_item.get("text", "").lower()
    full_text = title + " " + text
    
    for kw in FINANCE_KEYWORDS:
        if kw in full_text:
            return "Financial Markets"
    for kw in ECON_KEYWORDS:
        if kw in full_text:
            return "Macroeconomics"
    return "Politics/Geopolitics"
```

---

### Step 7: 生成报告

**Markdown 格式要求**:
```markdown
# Daily BRICS+ Economic & Political News Digest
**Date:** April 07, 2026  
**Coverage Period:** Past 24 Hours  

**⚠️ 数据完整性说明**:
- World News API 暂时不可用（返回"failure"）
- 本报告仅包含 API 成功返回的真实数据
- 不编造任何新闻、链接或摘要

---

## 🇯🇵 Japan

### [Politics/Geopolitics]
**1. Metaphore Biotechnologies Announces Series B Financing**
- **Source:** [Yahoo Finance](https://finance.yahoo.com/news/...)
- **Published:** 2026-04-07
- **Summary:** Metaphore Biotechnologies announced completion of Series B financing.

---

## ⚠️ 数据不可用的国家

以下国家因 World News API 暂时不可用，**无真实数据**:
- 🇪🇺 Eurozone
- 🇺🇸 United States
- ...

**说明**: 本报告严格使用 API 返回的真实数据，不编造任何新闻、链接或摘要。
```

**关键格式要求**:
| 元素 | 格式 | 说明 |
|------|------|------|
| 国家标题 | `## 🇯🇵 Japan` | 国旗 + 国家名 |
| 分类 | `### [Politics/Geopolitics]` | **方括号包裹** |
| 新闻标题 | `**1. 标题**` | **粗体 + 编号** |
| 来源 | `- **Source:** [作者](URL)` | **Markdown 链接（必须真实）** |
| 摘要 | `- **Summary:** 内容` | 1-2 句话（必须来自 API） |

---

### Step 8: IMA 上传

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

## 质量检查清单（⚠️ 新增数据完整性检查）

执行完成后，**逐项检查**:

### 数据完整性（最高优先级）
- [ ] **所有链接为真实 API 返回**（无 example.com）
- [ ] **所有摘要来自 API 或正文明确提取**（不编造）
- [ ] **API 不可用的国家明确标注"无数据"**
- [ ] **报告中说明哪些国家 API 不可用**

### 内容质量
- [ ] **所有新闻标题为英语**（非英语已翻译）
- [ ] **所有新闻摘要为英语**（非英语已翻译）
- [ ] **无语言标记**（不显示 [RU]/[AR] 等）
- [ ] **原文链接可用**（Markdown 格式）
- [ ] **分类使用方括号**（`[Category]`）
- [ ] **无体育/娱乐新闻**
- [ ] **每条新闻与该国相关**（中国新闻不含日本新闻）
- [ ] **每条新闻有有效摘要**（≥20 字符）
- [ ] **每国不超过 5 条新闻**
- [ ] **IMA 上传指定 folder_id**

---

## 常见错误及避免方法（⚠️ 新增真实案例）

### ❌ 错误 1: 编造假链接
**错误示例**:
```markdown
- **Source:** [International Online](https://example.com/cn-news-3)
```

**正确做法** ✅:
```markdown
- **Source:** [Japan Times](https://www.japantimes.co.jp/news/2026/04/07/world/...)
```

**规则**: 绝不使用 example.com 或任何编造的链接。

---

### ❌ 错误 2: 分类错误
**错误示例**:
```markdown
## 🇨🇳 China

### [Politics/Geopolitics]
**1. Japan confirms release of second citizen held in Iran**
- **Source:** [Japan Times](https://www.japantimes.co.jp/...)
```
（中国部分包含日本新闻）

**正确做法** ✅:
```markdown
## 🇨🇳 China
（无真实数据时标注"API 不可用，无数据"）

## 🇯🇵 Japan

### [Politics/Geopolitics]
**1. Japan confirms release of second citizen held in Iran**
```

**规则**: 严格按国家分类，通过 URL 域名和关键词验证。

---

### ❌ 错误 3: 编造摘要
**错误示例**:
```markdown
- **Summary:** China becomes "world Token factory"; how to empower...
```
（API 未返回此摘要，为编造内容）

**正确做法** ✅:
```markdown
- **Summary:** [API 返回的真实摘要]
```
或
```markdown
- **Summary:** 无摘要（API 未返回）
```

**规则**: 只使用 API 返回的真实摘要，或从正文明确提取。

---

### ❌ 错误 4: 标题保留原文
**错误示例**:
```markdown
**1. [RU] Треть россиян не доверяют телемедицине**
```

**正确做法** ✅:
```markdown
**1. One third of Russians do not trust telemedicine**
```

---

### ❌ 错误 5: IMA 上传未指定 folder_id
**错误**:
```bash
-d '{"content_format": 1, "content": "..."}'
```

**正确** ✅:
```bash
-d '{"content_format": 1, "content": "...", "folder_id": "foldere1b18e698eae2e88"}'
```

---

## 历史错误记录（2026-04-07）

### 事件
2026 年 4 月 7 日，生成过去 12 小时新闻报告时犯下严重错误：

1. **编造假链接**: 使用 example.com 编造了 10+ 个假链接
2. **分类错误**: 中国部分包含日本新闻
3. **编造摘要**: 很多 summary 不是 API 返回的真实数据
4. **未排除体育/娱乐**: NBA 新闻、明星新闻未被排除

### 根本原因
- World News API 暂时不可用（返回"failure"）
- 为了"填充"报告，编造了数据
- 未严格执行数据验证

### 改进措施
1. **API 验证**: 增加 API 状态检查步骤
2. **诚实报告**: API 不可用时明确标注"无数据"
3. **链接验证**: 检查所有链接，排除 example.com
4. **分类验证**: 通过 URL 域名和关键词验证国家分类
5. **体育/娱乐排除**: 扩展排除关键词列表

### 教训
**宁可报告数据不完整，也绝不编造任何内容。数据真实性是新闻收集的第一原则。**

---

## 执行时间线（典型）

| 步骤 | 耗时 | 说明 |
|------|------|------|
| Step 1: 获取新闻 | 30-60 秒 | 11 国 API 请求 |
| Step 2: API 验证 | 5-10 秒 | 检查 status 和数据完整性 |
| Step 3: 语言检测 | 5-10 秒 | 110 条检测 |
| Step 4: AI 翻译 | 30-60 秒 | 20-30 条翻译 |
| Step 5: 筛选过滤 | 10-20 秒 | 排除体育/娱乐 |
| Step 6: 分类整理 | 5-10 秒 | 金融/宏观/政治 |
| Step 7: 生成报告 | 5-10 秒 | Markdown 格式化 |
| Step 8: IMA 上传 | 5-10 秒 | API 调用 |
| **总计** | **90-180 秒** | 约 1.5-3 分钟 |

---

## 参考资料

- **World News API 文档**: https://worldnewsapi.com/docs
- **IMA API 文档**: https://ima.qq.com/agent-interface
- **任务配置文件**: `~/.openclaw/cron/jobs.json`
- **脚本位置**: `~/openclaw/workspace/scripts/process_brics_news_v3.py`
