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

2. **严格筛选** ❌
   - 先筛选，后翻译（避免翻译无用新闻）
   - 每国最多 5 条新闻
   - 排除体育/娱乐新闻

3. **API 不可用时的处理** ⚠️
   - **立即停止，提醒用户**
   - 提供 3 个选项：A) 继续 B) 等待 C) 取消
   - **等待用户决策后再执行**

4. **翻译策略** ✅
   - **先筛选，后翻译**（核心优化）
   - 只翻译最终收录的新闻
   - 使用当前对话的 AI 能力（无需外部 API）

---

## 完整执行流程（5 步）

### Step 1: 获取新闻

**数据源**:
1. **World News API** - 11 个国家
2. **Financial Express Bangladesh** - 孟加拉备用源

```bash
# 环境变量
export WORLD_NEWS_API_KEY="96798c19fe364458ba4f9dbe55477115"
export HTTP_PROXY="http://127.0.0.1:7897"

# 11 个国家代码
COUNTRIES="eu us jp br ru in cn za eg bd ae"

# 日期范围
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d)
TODAY=$(date +%Y-%m-%d)

# 获取新闻（每国 10 条用于筛选）
for country in $COUNTRIES; do
  curl -s -x "$HTTP_PROXY" \
    "https://api.worldnewsapi.com/search-news?source-countries=$country&api-key=$WORLD_NEWS_API_KEY&from=$YESTERDAY&to=$TODAY&number=10&sort-by=publish_date" \
    > "/tmp/news_collection/${country}.json"
done

# 孟加拉备用源（直接抓取 Financial Express）
web_fetch "https://thefinancialexpress.com.bd/page/economy/bangladesh" \
  --extractMode markdown --maxChars 15000 \
  > "/tmp/news_collection/bd_fe.md"
```

**API 验证**:
```python
def validate_api_response(data):
    if not data:
        return False, "API 返回空数据"
    status = data.get('status')
    if status in ['failure', 'error']:
        return False, f"API 返回失败状态：{status}"
    news_list = data.get('news', [])
    if not news_list:
        return False, "API 返回空新闻列表"
    return True, "数据验证通过"
```

---

### Step 2: 筛选新闻（⚠️ 关键步骤）

**筛选逻辑**: **先筛选，后翻译**（但非英语标题需要先翻译）

**问题**: 对于非英语标题（俄语/阿拉伯语/中文等），无法直接判断内容

**解决方案**: **两阶段筛选**

```python
def filter_news(news_list, country_code, max_items=5):
    """
    筛选新闻（两阶段）
    
    阶段 1: 不依赖标题内容的筛选
    - URL 域名验证
    - 正文字段验证
    - API 分类字段
    
    阶段 2: 非英语标题先翻译，再筛选
    """
    filtered = []
    titles_to_translate = []
    
    for item in news_list:
        # 阶段 1: 不依赖标题的筛选
        
        # 1. URL 域名验证（最可靠）
        if not is_relevant_by_url(item, country_code):
            continue
        
        # 2. 检查 API 分类字段
        category = item.get("category", "").lower()
        if category in ["sports", "entertainment", "lifestyle"]:
            continue
        
        # 3. 正文内容验证（即使标题是外语，正文可能包含英语关键词）
        if not is_relevant_by_text(item, country_code):
            continue
        
        # 4. 确保有摘要
        summary = item.get("summary")
        if not summary or len(summary) < 20:
            text = item.get("text", "")
            summary = simple_summarize(text, max_length=150)
        
        if not summary:
            continue
        
        item["summary"] = summary
        
        # 5. 检测标题语言
        title = item.get("title", "")
        title_lang = detect_language(title)
        
        if title_lang != "en":
            # 非英语标题，需要先翻译
            titles_to_translate.append({
                "index": len(filtered),
                "title": title,
                "lang": title_lang
            })
        
        filtered.append(item)
    
    # 阶段 2: 翻译非英语标题
    if titles_to_translate:
        translations = call_ai_translate(titles_to_translate)
        for trans in translations:
            filtered[trans["index"]]["title"] = trans["translated"]
    
    # 阶段 3: 翻译后再筛选（排除体育/娱乐）
    final_filtered = []
    for item in filtered:
        if should_exclude_by_title(item):
            continue
        final_filtered.append(item)
        if len(final_filtered) >= max_items:
            break
    
    return final_filtered
```

**排除规则**:
```python
EXCLUDE_SPORTS = ["nfl", "nba", "mlb", "nhl", "premier league", "cricket", "ipl"]
EXCLUDE_ENTERTAINMENT = ["celebrity", "movie", "music award", "snl"]
```

**相关性检测（多策略）**:

```python
# 策略 1: URL 域名验证（最可靠，不依赖语言）
URL_COUNTRY_MAP = {
    "br": [".br", "globo.com", "uol.com.br"],
    "ru": [".ru", "ria.ru", "tass.ru"],
    "cn": [".cn", "chinadaily.com.cn", "xinhuanet.com"],
    "jp": [".jp", "japantimes.co.jp", "asahi.com"],
    # ... 其他国家
}

def is_relevant_by_url(news_item, country_code):
    url = news_item.get("url", "").lower()
    for domain in URL_COUNTRY_MAP.get(country_code, []):
        if domain in url:
            return True
    return False

# 策略 2: 正文字段验证（即使标题是外语，正文可能包含英语）
COUNTRY_KEYWORDS = {
    "br": ["brazil", "brasileiro", "brasilia", "sao paulo"],
    "ru": ["russia", "russian", "moscow", "kremlin"],
    "cn": ["china", "chinese", "beijing", "shanghai"],
    # ... 其他国家
}

def is_relevant_by_text(news_item, country_code):
    text = (news_item.get("text") or "").lower()
    for kw in COUNTRY_KEYWORDS.get(country_code, []):
        if kw in text:
            return True
    return False

# 策略 3: API 分类字段
def is_sports_or_entertainment(news_item):
    category = (news_item.get("category") or "").lower()
    return category in ["sports", "entertainment", "lifestyle"]
```

**产出**: 每个国家最多 5 条新闻（已筛选，未翻译）

---

### Step 3: 翻译新闻

**翻译策略**: **标题和摘要都要翻译**

**流程**:
1. 筛选阶段已翻译非英语标题（为了筛选）
2. 现在翻译所有收录新闻的标题和摘要（确保全文英语）

```python
def translate_all_news(news_list):
    """
    翻译所有收录新闻的标题和摘要
    
    流程:
    1. 收集需要翻译的文本（标题 + 摘要）
    2. 批量调用 AI 翻译（使用当前对话的大模型能力）
    3. 应用翻译结果
    """
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
                "text": title[:200],
                "lang": title_lang
            })
        
        # 检测摘要语言
        if summary:
            summary_lang = detect_language(summary)
            if summary_lang != "en":
                texts_to_translate.append({
                    "index": i,
                    "field": "summary",
                    "text": summary[:200],
                    "lang": summary_lang
                })
    
    # 调用 AI 翻译（使用当前对话的大模型能力）
    if texts_to_translate:
        translations = call_ai_translate(texts_to_translate)
        news_list = apply_translations(news_list, translations)
    
    return news_list
```

**翻译示例**:
| 原文 | 语言 | 翻译后 |
|------|------|--------|
| `Треть россиян не доверяют телемедицине` | 俄语 | `One third of Russians do not trust telemedicine` |
| `إسرائيل تحتجز 4 من جنودها` | 阿拉伯语 | `Israel detains 4 of its soldiers` |
| `中国成为"世界 Token 工厂"` | 中文 | `China becomes "world Token factory"` |
| `きょう予算が成立見込み` | 日语 | `Budget expected to pass today` |

**产出**: 所有新闻标题和摘要均为英语

**语言检测**:
```python
def detect_language(text):
    # 英语：ASCII >95%
    # 日语：\u3040-\u30ff
    # 俄语：\u0400-\u04ff
    # 中文：\u4e00-\u9fff
    # 葡萄牙语：ãõç
    # 法语：éàèùâêîôûç
    # 阿拉伯语：\u0600-\u06ff
    # 印地语：\u0900-\u097f
```

**翻译示例**:
| 原文 | 语言 | 翻译后 |
|------|------|--------|
| `Треть россиян не доверяют телемедицине` | 俄语 | `One third of Russians do not trust telemedicine` |
| `إسرائيل تحتجز 4 من جنودها` | 阿拉伯语 | `Israel detains 4 of its soldiers` |
| `中国成为"世界 Token 工厂"` | 中文 | `China becomes "world Token factory"` |

**产出**: 所有新闻标题和摘要均为英语

---

### Step 4: 生成报告

**Markdown 格式**:
```markdown
# Daily BRICS+ Economic & Political News Digest
**Date:** April 08, 2026  
**Coverage Period:** Past 24 Hours  

---

## 🇺🇸 United States

### [Financial Markets]
**1. Fed announces interest rate decision**
- **Source:** [Reuters](https://www.reuters.com/...)
- **Published:** 2026-04-08
- **Summary:** The Federal Reserve announced...

---

## Summary Statistics

| Metric | Value |
|--------|-------|
| **Total News Items** | 55 |
| **Countries/Regions** | 11 |
```

**关键格式要求**:
| 元素 | 格式 | 说明 |
|------|------|------|
| 国家标题 | `## 🇺🇸 United States` | 国旗 + 国家名 |
| 分类 | `### [Financial Markets]` | **方括号包裹** |
| 新闻标题 | `**1. 标题**` | **粗体 + 编号** |
| 来源 | `- **Source:** [作者](URL)` | **Markdown 链接（必须真实）** |
| 摘要 | `- **Summary:** 内容` | 1-2 句话（必须来自 API 或正文） |

---

### Step 5: 上传 IMA 并备份

**IMA 上传**:
```bash
export IMA_OPENAPI_CLIENTID="0acab5edb61ac4876ff36cb9b20831b7"
export IMA_OPENAPI_APIKEY="lh0q+b9rbrt7R/2QmINAmw6Z8rmydv5zuvjw9wC+tF4rOD8fTnn0rd0GuhWtGw9Ab6+AKJhN9g=="

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

**本地备份**:
```bash
# 保存到 workspace
cp daily-brics-news-YYYY-MM-DD.md /home/admin/openclaw/workspace/

# 可选：归档到历史目录
mkdir -p /home/admin/openclaw/workspace/archive/$(date +%Y/%m)
cp daily-brics-news-YYYY-MM-DD.md /home/admin/openclaw/workspace/archive/$(date +%Y/%m)/
```

---

## API 不可用时的用户决策流程

**当 API 不可用时（超过 50% 国家无数据），必须**:

1. **立即停止自动执行**
2. **提醒用户**，说明情况：
   ```
   ⚠️ World News API 暂时不可用

   **受影响国家**: EU, US, JP, BR, RU, IN, CN, ZA, EG, AE (10/11 个国家)
   **可用数据源**: 🇧🇩 Bangladesh (Financial Express)

   请选择：
   A) 继续执行（仅收录孟加拉新闻，其他国家标注"无数据"）
   B) 等待 API 恢复后重新执行
   C) 取消本次任务
   ```

3. **等待用户决策**
4. **根据用户决策执行**

**严禁**:
- ❌ 未经用户同意继续执行
- ❌ 编造任何数据填充报告
- ❌ 隐瞒 API 不可用的情况

---

## 质量检查清单

执行完成后，**逐项检查**:

### 数据完整性（最高优先级）
- [ ] **所有链接为真实 API 返回**（无 example.com）
- [ ] **所有摘要来自 API 或正文明确提取**（不编造）
- [ ] **API 不可用的国家明确标注"无数据"**
- [ ] **报告中说明哪些国家 API 不可用**

### 筛选逻辑
- [ ] **先筛选，后翻译**（避免翻译无用新闻）
- [ ] **每国不超过 5 条新闻**
- [ ] **无体育/娱乐新闻**
- [ ] **每条新闻与该国相关**

### 翻译质量
- [ ] **所有新闻标题为英语**（非英语已翻译）
- [ ] **所有新闻摘要为英语**（非英语已翻译）
- [ ] **无语言标记**（不显示 [RU]/[AR] 等）

### 格式规范
- [ ] **原文链接可用**（Markdown 格式）
- [ ] **分类使用方括号**（`[Category]`）
- [ ] **每国不超过 5 条新闻**
- [ ] **IMA 上传指定 folder_id**

---

## 执行时间线（典型）

| 步骤 | 耗时 | 说明 |
|------|------|------|
| Step 1: 获取新闻 | 30-60 秒 | 11 国 API 请求 + Financial Express |
| Step 2: 筛选新闻 | 15-25 秒 | **两阶段筛选**：<br>1. URL/正文验证（不依赖标题）<br>2. 非英语标题先翻译，再筛选 |
| Step 3: 翻译新闻 | 30-60 秒 | 翻译所有收录新闻的**标题 + 摘要** |
| Step 4: 生成报告 | 5-10 秒 | Markdown 格式化 |
| Step 5: IMA 上传 | 5-10 秒 | API 调用 |
| **总计** | **85-165 秒** | 约 1.5-2.5 分钟 |

**优化点**: 
- 两阶段筛选：先 URL/正文验证，再翻译标题，避免翻译无关新闻
- 批量翻译：标题和摘要一起翻译，提高效率
- 只翻译最终收录的新闻（25-55 条 × 2 = 50-110 个文本块）

---

## 历史错误记录（2026-04-07）

### 事件
2026 年 4 月 7 日，生成过去 12 小时新闻报告时犯下严重错误：

1. **编造假链接**: 使用 example.com 编造了 10+ 个假链接
2. **分类错误**: 中国部分包含日本新闻
3. **编造摘要**: 很多 summary 不是 API 返回的真实数据
4. **未排除体育/娱乐**: NBA 新闻、明星新闻未被排除
5. **未经用户决策继续执行**: API 不可用时未提醒用户

### 根本原因
- World News API 暂时不可用（返回"failure"）
- 为了"填充"报告，编造了数据
- 未严格执行数据验证
- 未遵循"先筛选后翻译"的流程

### 改进措施
1. **API 验证**: 增加 API 状态检查步骤
2. **用户决策**: API 不可用时立即提醒，等待决策
3. **链接验证**: 检查所有链接，排除 example.com
4. **分类验证**: 通过 URL 域名和关键词验证国家分类
5. **流程优化**: **先筛选，后翻译**（避免翻译无用新闻）
6. **翻译模块**: 使用当前对话的 AI 能力（无需外部 API）

### 教训
**宁可报告数据不完整，也绝不编造任何内容。数据真实性是新闻收集的第一原则。**

---

## 参考资料

- **World News API 文档**: https://worldnewsapi.com/docs
- **IMA API 文档**: https://ima.qq.com/agent-interface
- **任务配置文件**: `~/.openclaw/cron/jobs.json`
- **脚本位置**: 
  - `~/openclaw/workspace/scripts/process_brics_news_v3.py`（主流程）
  - `~/openclaw/workspace/scripts/ai_translate.py`（翻译模块）
