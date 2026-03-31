---
name: brics-news-digest
description: |
  Daily BRICS+ Economic & Political News Digest Skill.
  Uses World News API to fetch real-time news with auto-summaries, generates English report and uploads to IMA notes.
  
  **Countries/Regions Covered (11)**: 🇪🇺 Eurozone, 🇺🇸🇯🇵🇧🇷🇷🇺🇮🇳🇨🇳🇿🇦🇪🇬🇧🇩🇦🇪
  **Execution Time**: 8:00 AM daily (Beijing Time)
  **News Categories**: Macroeconomics + Financial Markets + Politics/Geopolitics
  **Items per Country**: 5 (sorted by time, newest first)
  **Output Language**: English
  **Required Fields**: Each news item MUST include original source link (url)
metadata:
  {
    "openclaw":
      {
        "emoji": "📰",
        "requires": { "env": ["WORLD_NEWS_API_KEY", "IMA_OPENAPI_CLIENTID", "IMA_OPENAPI_APIKEY"] }
      }
  }
---

# BRICS News Digest - World News API Version

## ⚙️ Configuration

**Environment Variables**:
```bash
export WORLD_NEWS_API_KEY="96798c19fe364458ba4f9dbe55477115"
export IMA_OPENAPI_CLIENTID="0acab5edb61ac4876ff36cb9b20831b7"
export IMA_OPENAPI_APIKEY="lh0q+b9rbrt7R/2QmINAmw6Z8rmydv5zuvjw9wC+tF4rOD8fTnn0rd0G2GuhWtGw9Ab6+AKJhN9g=="
export HTTP_PROXY="http://127.0.0.1:7897"
```

**IMA Configuration**:
- Notebook: `foldere1b18e698eae2e88`
- Knowledge Base: `mz_V5FtC10F57Fu3Ly7zZVf2SSbcIQUKLghXd8HeMOY=`

## 📰 API Endpoints

```bash
https://api.worldnewsapi.com/search-news?source-countries={country}&api-key={key}&categories=politics,business&number=5&sort-by=publish-time&sort-direction=DESC
```

**Response Fields**:
- `title`: News headline
- `summary`: **Auto-summary** (1-2 sentences, use directly) ✅
- `text`: Full content
- `url`: **Original article link** (REQUIRED - must include in output) ✅
- `author`: Author name
- `publish_date`: Publication timestamp
- `category`: Category (politics, business, sports, etc.)
- `source`: News source name
- `sentiment`: Sentiment analysis

## 📝 News Filtering Logic

### ✅ Categories to Collect

**Via API `categories` parameter**:
```
categories=politics,business
```

**Specific Inclusions**:
1. **Macroeconomics**
   - GDP, inflation, employment, trade, export, import, economic policy, central bank

2. **Financial Markets**
   - stock market, forex, bonds, commodities, oil price, gold price, investment, banking

3. **Politics/Geopolitics**
   - election, diplomacy, geopolitics, government policy, international relations

### ❌ Content to Exclude

**Keyword filtering**:
```python
exclude_keywords = [
    # Sports
    'football', 'soccer', 'basketball', 'baseball', 'tennis', 'golf',
    'game', 'match', 'team', 'player', 'score', 'goal', 'championship',
    
    # Entertainment
    'movie', 'film', 'actor', 'actress', 'singer', 'concert',
    'entertainment', 'celebrity', 'awards', 'festival', 'music video',
    
    # Lifestyle/Culture
    'lifestyle', 'fashion', 'food', 'recipe', 'travel guide',
    
    # Tech (unless related to economic news)
    'smartphone', 'app', 'software update', 'game release'
]
```

**Exclude sources**:
```python
exclude_sources = ['tmz', 'espn', 'people', 'usweekly']
```

## 🎯 News Selection Strategy

### Selection Logic (by priority)

```
1. Sort by time (highest priority)
   ↓
2. Category priority (Macro > Finance > Politics)
   ↓
3. Source diversity (max 2 per media outlet)
   ↓
4. Summary quality check (length > 50 chars)
   ↓
5. Select top 5
```

### API Configuration

**Simplest approach**: Let API return latest 5 directly

```bash
# API request parameters
number=5
sort-by=publish-time
sort-direction=DESC
categories=politics,business
```

**Advantages**:
- ✅ Simple and efficient
- ✅ Guarantees timeliness (past 24 hours)
- ✅ Saves processing time
- ✅ Lowest token consumption

## 🔄 Execution Flow

### 1. Fetch News from All Countries
```bash
# Country codes: eu, us, jp, br, ru, in, cn, za, eg, bd, ae
for country in eu us jp br ru in cn za eg bd ae; do
  curl -s --proxy "$HTTP_PROXY" \
    "https://api.worldnewsapi.com/search-news?source-countries=$country&api-key=$WORLD_NEWS_API_KEY&categories=politics,business&number=5&sort-by=publish-time&sort-direction=DESC"
done
```

### 2. Filter News
```python
def is_valid_news(news):
    # Check category
    if news.get('category') in ['sports', 'entertainment']:
        return False
    
    # Check exclude keywords
    for keyword in exclude_keywords:
        if keyword in news['title'].lower():
            return False
    
    # Check for valid summary
    if not news.get('summary') or len(news['summary']) < 20:
        return False
    
    # Check for URL (REQUIRED)
    if not news.get('url'):
        return False
    
    return True
```

### 3. Use API Summary with Source Link
```python
# Use API-provided summary directly
summary = news['summary']  # ✅ No need to generate

# Format as Markdown (ENGLISH OUTPUT)
markdown = f"""
### {news['title']}

- **Source:** [{news.get('source', 'Unknown')}]({news['url']})
- **Published:** {news['publish_date']}
- **Summary:** {summary}
"""
```

### 4. Save File Using `write` Tool (NOT exec!)
```python
# ✅ CORRECT: Use write tool
write_tool(
    path="/tmp/DailyNews_BRICS_YYYY-MM-DD.md",
    content=markdown_content
)

# ❌ WRONG: Don't use exec to write files
# exec("echo '...' > /tmp/file.md")  # DON'T DO THIS
```

### 5. Upload to IMA
```bash
# Create note
curl -X POST "https://ima.qq.com/openapi/note/v1/import_doc" \
  -H "ima-openapi-clientid: $IMA_OPENAPI_CLIENTID" \
  -H "ima-openapi-apikey: $IMA_OPENAPI_APIKEY" \
  -d '{"content_format": 1, "content": "<Markdown>", "folder_id": "foldere1b18e698eae2e88"}'

# Add to knowledge base
curl -X POST "https://ima.qq.com/openapi/knowledge/v1/add_knowledge" \
  -H "ima-openapi-clientid: $IMA_OPENAPI_CLIENTID" \
  -H "ima-openapi-apikey: $IMA_OPENAPI_APIKEY" \
  -d '{"knowledge_base_id": "mz_V5FtC10F57Fu3Ly7zZVf2SSbcIQUKLghXd8HeMOY=", "media_type": 11}'
```

## 📊 Token Consumption

| Item | Tokens |
|------|--------|
| World News API (11 countries) | ~550 |
| Input content (using API summaries) | ~2,500-3,000 |
| IMA API | ~500 |
| **Daily Total** | **~3,500-4,000** |

**Saves 99.7% vs original approach** ✅

## ⚠️ Critical Requirements

1. **Output Language**: ALL content MUST be in **English** ✅
2. **Include Eurozone**: Add 🇪🇺 EU section as first country ✅
3. **Source Links**: Every news item MUST include clickable original link ✅
4. **Use write Tool**: Save files using `write` tool, NOT exec commands ✅
5. **Use API Summary**: Directly use `summary` field, don't generate yourself
6. **Category Filtering**: Use `categories=politics,business` parameter
7. **Keyword Filtering**: Exclude sports, entertainment, etc.
8. **Source Diversity**: Max 2 articles per media outlet
9. **Time Range**: Past 24 hours only
10. **Send File to User**: After generating, use `message` tool to send the file ✅

## 📋 Output Format (ENGLISH)

```markdown
# Daily BRICS+ Economic & Political News Digest
**Date:** Month DD, YYYY  
**Coverage Period:** Past 24 Hours  
**Countries Covered:** 🇪🇺 Eurozone, 🇺🇸 US, 🇯🇵 Japan, 🇧🇷 Brazil, 🇷🇺 Russia, 🇮🇳 India, 🇨🇳 China, 🇿🇦 South Africa, 🇪🇬 Egypt, 🇧🇩 Bangladesh, 🇦🇪 UAE

---

## 🇪🇺 EUROZONE / EUROPEAN UNION

### Politics & Macroeconomics
**1. [Headline]**
- **Source:** [Media Name](https://original-article-url.com/...)
- **Published:** YYYY-MM-DD HH:MM:SS
- **Summary:** 1-2 sentence summary from API...

---

## 🇺🇸 UNITED STATES

### Politics
**1. [Headline]**
- **Source:** [Media Name](https://original-article-url.com/...)
- **Published:** YYYY-MM-DD HH:MM:SS
- **Summary:** 1-2 sentence summary from API...

---

(Continue for all 11 countries/regions)

---

## Summary Statistics

| Metric | Value |
|--------|-------|
| **Total News Items** | XX |
| **Countries/Regions** | 11 (including EU) |
| **Politics/Geopolitics** | XX |
| **Macroeconomics** | XX |
| **Financial Markets** | XX |

**Report Generated:** Month DD, YYYY, HH:MM AM/PM (Asia/Shanghai)  
**Source:** World News API  
**Token Estimate:** ~3,500-4,000 tokens

---

## Notes
- ✅ Eurozone/EU section included
- ✅ All news items include original source links
- ✅ Excluded sports and entertainment news
- ✅ Coverage period: Past 24 hours
```

## 🛠️ Tool Usage Checklist

Before completing the task, ensure:

- [ ] Used `exec` with curl to fetch from World News API (11 countries)
- [ ] Filtered out sports/entertainment news
- [ ] **All content is in English**
- [ ] **Eurozone section added** (first section)
- [ ] **Every news item has clickable source link**
- [ ] Used `write` tool to save markdown file (NOT exec)
- [ ] Used `message` tool to send file to user
- [ ] Attempted IMA upload (if credentials available)
- [ ] Token count ~3,500-4,000

## 📁 File Delivery

**After generating the file, MUST send to user:**

```python
# Use message tool to send the file
message(
    action="send",
    filePath="/tmp/DailyNews_BRICS_YYYY-MM-DD.md"
)
```

**DO NOT** just tell user the file path - they cannot access it directly!
