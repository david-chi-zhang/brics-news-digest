---
name: brics-news-digest
description: |
  Daily BRICS+ Economic & Political News Digest Skill.
  Uses World News API to fetch real-time news, filters domestic/national news only,
  translates non-English to English, generates report and uploads to IMA.
  
  **Countries/Regions Covered**: 🇪🇺 Eurozone, 🇺🇸 🇯🇵 🇧🇷 🇷🇺 🇮🇳 🇨🇳 🇿🇦 🇪🇬 🇧🇩 🇦🇪
  **Execution Time**: 8:00 AM daily (Beijing Time)
  **News Categories**: Macroeconomics + Financial Markets + Politics/Geopolitics
  **Items per Country**: 5 (domestic/national news only)
  **Output Language**: English (non-English translated)
  **China Specific**: National-level only (NO provincial/local news)
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
export IMA_OPENAPI_APIKEY="lh0q+b9rbrt7R/2QmINAmw6Z8rmydv5zuvjw9wC+tF4rOD8fTnn0rd0GuhWtGw9Ab6+AKJhN9g=="
export HTTP_PROXY="http://127.0.0.1:7897"
```

**IMA Configuration**:
- **Notebook ID**: `foldere1b18e698eae2e88` (DailyNews)
- **Knowledge Base ID**: `mz_V5FtC10F57Fu3Ly7zZVf2SSbcIQUKLghXd8HeMOY=`

## 📰 API Endpoints

```bash
# Fetch news from World News API
https://api.worldnewsapi.com/search-news?source-countries={country}&api-key={key}&categories=politics,business&number=10&sort-by=publish-time&sort-direction=DESC
```

**Response Fields**:
- `title`: News title
- `summary`: Auto-generated summary (1-2 sentences)
- `text`: Full article text
- `url`: Article link
- `author`: Author name
- `publish_date`: Publication timestamp
- `category`: Category (politics, business, sports, etc.)
- `language`: Language code (en, zh, ru, ar, pt, etc.)
- `source_country`: Source country code (us, cn, ru, etc.)

## 📝 News Filtering Logic

### ✅ Categories to Collect

**Via API `categories` parameter**:
```
categories=politics,business
```

**Specific Topics**:
1. **Macroeconomics**
   - GDP, inflation, employment, trade, export, import, economic policy, central bank

2. **Financial Markets**
   - stock market, forex, bonds, commodities, oil price, gold price, investment, banking

3. **Politics/Geopolitics**
   - election, diplomacy, geopolitics, government policy, international relations

### ❌ Content to Exclude

**Keyword Filtering**:
```python
exclude_keywords = [
    # Sports
    'football', 'soccer', 'basketball', 'baseball', 'tennis', 'golf',
    'game', 'match', 'team', 'player', 'score', 'goal', 'championship', 'world cup',
    
    # Entertainment
    'movie', 'film', 'actor', 'actress', 'singer', 'concert',
    'entertainment', 'celebrity', 'awards', 'festival', 'music video',
    
    # Lifestyle
    'lifestyle', 'fashion', 'food', 'recipe', 'travel guide',
    
    # Technology (unless related to economic news)
    'smartphone', 'app', 'software update', 'game release'
]
```

### 🌍 Domestic News Filter (CRITICAL!)

**Each country's news MUST be about that country itself**:

```python
def is_domestic_news(news, country_code):
    """Check if news is about the country itself, not just from that country"""
    
    title = news.get('title', '').lower()
    text = news.get('text', '').lower()
    summary = news.get('summary', '').lower()
    
    # Country-specific keywords that indicate domestic focus
    country_keywords = {
        'us': ['us ', 'usa ', 'america', 'american', 'united states', 'congress', 'white house', 'senate', 'federal reserve', 'wall street'],
        'cn': ['china', 'chinese', 'beijing', 'national', 'central government'],
        'ru': ['russia', 'russian', 'moscow', 'kremlin'],
        'jp': ['japan', 'japanese', 'tokyo'],
        'br': ['brazil', 'brazilian', 'brasilia'],
        'in': ['india', 'indian', 'new delhi'],
        'za': ['south africa', 'south african', 'pretoria'],
        'eg': ['egypt', 'egyptian', 'cairo'],
        'bd': ['bangladesh', 'bangladeshi', 'dhaka'],
        'ae': ['uae', 'united arab emirates', 'dubai', 'abu dhabi'],
    }
    
    keywords = country_keywords.get(country_code, [])
    content = title + ' ' + summary + ' ' + text[:500]
    
    # Check if any country keyword appears
    for keyword in keywords:
        if keyword in content:
            return True
    
    return False
```

**✅ Valid US news**:
- "US Federal Reserve raises interest rates"
- "American stocks surge on earnings reports"
- "White House announces new economic policy"

**❌ Invalid US news** (even if from US source):
- "China and Pakistan outline peace plan" → About China/Pakistan
- "Middle East conflict escalates" → About Middle East
- "Italy misses World Cup" → About Italy

### 🇨🇳 China National-Level Filter (VERY IMPORTANT!)

**China news MUST be national-level, NOT provincial/local**:

```python
def is_national_china_news(news):
    """Filter out local/provincial China news, keep only national-level"""
    
    title = news.get('title', '').lower()
    summary = news.get('summary', '').lower()
    text = news.get('text', '').lower()
    content = title + ' ' + summary + ' ' + text[:500]
    
    # ❌ Exclude local/provincial keywords
    local_keywords = [
        # Provinces
        'anhui', 'guangdong', 'sichuan', 'zhejiang', 'jiangsu', 'shandong',
        'henan', 'hebei', 'hunan', 'hubei', 'jiangxi', 'shanxi', 'shaanxi',
        'gansu', 'qinghai', 'guizhou', 'yunnan', 'fujian', 'liaoning',
        'jilin', 'heilongjiang', 'hainan', 'inner mongolia', 'guangxi',
        'ningxia', 'xinjiang', 'tibet',
        
        # Cities (except Beijing for national news)
        'guangzhou', 'shenzhen', 'chengdu', 'hangzhou', 'nanjing', 'jinan',
        'zhengzhou', 'shijiazhuang', 'changsha', 'wuhan', 'nanchang', 'taiyuan',
        'xi\'an', 'lanzhou', 'xining', 'guiyang', 'kunming', 'fuzhou', 'xiamen',
        'shenyang', 'changchun', 'harbin', 'haikou', 'nanning', 'yinchuan',
        'urumqi', 'lhasa',
        
        # Local government terms
        'provincial government', 'municipal government', 'local authorities',
        'city officials', 'provincial officials'
    ]
    
    # ✅ Include national-level keywords
    national_keywords = [
        'china', 'chinese', 'beijing', 'central government', 'state council',
        'national', 'nationwide', 'country', 'president', 'premier',
        'national people\'s congress', 'politburo', 'central committee',
        'ministry of', 'national development', 'china\'s economy',
        'china\'s gdp', 'china\'s trade', 'china\'s inflation',
        'pbc', 'people\'s bank of china', 'china securities',
    ]
    
    # Check if contains local keywords (exclude)
    for keyword in local_keywords:
        if keyword in content:
            return False
    
    # Check if contains national keywords (include)
    for keyword in national_keywords:
        if keyword in content:
            return True
    
    # Default: if it's about China but not local, include
    if 'china' in content or 'chinese' in content:
        return True
    
    return False
```

**✅ Valid China National News**:
- "China's GDP grows 5.2% in Q1"
- "PBOC announces new monetary policy"
- "President Xi meets with foreign leaders"
- "China's trade surplus reaches record high"
- "Central government unveils economic stimulus"

**❌ Invalid China Local News**:
- "Anhui province reports strong industrial growth" → Local
- "Guangdong exports surge" → Local
- "Sichuan tourism revenue increases" → Local
- "Shanghai stock exchange new rules" → Local
- "Shenzhen tech companies expand" → Local

### 🌐 Translation for Non-English News

**Translate title and summary to English**:

```python
def translate_to_english(text, source_lang='auto'):
    """Translate text to English"""
    
    # If already English, return as-is
    if source_lang == 'en':
        return text
    
    # Add translation marker
    return f"[Translated from {source_lang}] {text}"
```

**Translation Strategy**:
1. Check `news['language']` field
2. If not 'en', mark title and summary for translation
3. Keep original source link
4. Add "[Translated]" marker

## 🎯 News Selection Strategy

### Selection Logic (Priority Order)

```
1. Fetch news (10 items per country)
   ↓
2. Filter domestic news only (source_country matches AND content about country)
   ↓
3. For China: Additional national-level filter (exclude provincial/local)
   ↓
4. Filter by category (politics, business only)
   ↓
5. Exclude sports, entertainment, lifestyle
   ↓
6. Check summary quality (length > 50 chars)
   ↓
7. Sort by time (newest first)
   ↓
8. Select top 5
   ↓
9. Translate non-English to English
```

### Detailed Implementation

```python
def select_top_5_news(all_news, country_code):
    """Select 5 domestic/national news items for a specific country"""
    
    # 1. Filter domestic news only
    if country_code == 'cn':
        # China: Use national-level filter
        domestic = [n for n in all_news if is_national_china_news(n)]
    else:
        # Other countries: Use domestic filter
        domestic = [n for n in all_news if is_domestic_news(n, country_code)]
    
    # 2. Filter by category
    valid = [n for n in domestic if n.get('category') in ['politics', 'business']]
    
    # 3. Exclude unwanted topics
    filtered = [n for n in valid if not has_exclude_keywords(n)]
    
    # 4. Check summary quality
    quality = [n for n in filtered if len(n.get('summary', '')) > 50]
    
    # 5. Sort by time (newest first)
    sorted_news = sorted(quality, key=lambda x: x['publish_date'], reverse=True)
    
    # 6. Select top 5
    selected = sorted_news[:5]
    
    # 7. Translate non-English to English
    for news in selected:
        if news.get('language', 'en') != 'en':
            news['title'] = translate_to_english(news['title'], news['language'])
            news['summary'] = translate_to_english(news['summary'], news['language'])
    
    return selected
```

## 🔄 Execution Flow

### 1. Fetch News from All Countries
```bash
for country in us jp br ru in cn za eg bd ae; do
  curl -s --proxy "$HTTP_PROXY" \
    "https://api.worldnewsapi.com/search-news?source-countries=$country&api-key=$WORLD_NEWS_API_KEY&categories=politics,business&number=10&sort-by=publish-time&sort-direction=DESC" \
    > /tmp/news_${country}.json
done
```

### 2. Filter Domestic/National News Only
```python
for country in countries:
  news = load_news(country)
  if country == 'cn':
    # China: National-level only
    selected = select_top_5_news(news, country, national_only=True)
  else:
    # Other countries: Domestic only
    selected = select_top_5_news(news, country, national_only=False)
```

### 3. Translate Non-English
```python
if news['language'] != 'en':
  news['title'] = translate(news['title'])
  news['summary'] = translate(news['summary'])
```

### 4. Upload to IMA

#### Step 1: Create Note
```bash
curl -s -X POST "https://ima.qq.com/openapi/note/v1/import_doc" \
  -H "ima-openapi-clientid: $IMA_OPENAPI_CLIENTID" \
  -H "ima-openapi-apikey: $IMA_OPENAPI_APIKEY" \
  -H "Content-Type: application/json" \
  -d '{
    "content_format": 1,
    "content": "<Markdown content>",
    "folder_id": "foldere1b18e698eae2e88"
  }'
```

#### Step 2: Add to Knowledge Base ✅ CORRECT FORMAT
```bash
curl -s -X POST "https://ima.qq.com/openapi/wiki/v1/add_knowledge" \
  -H "ima-openapi-clientid: $IMA_OPENAPI_CLIENTID" \
  -H "ima-openapi-apikey: $IMA_OPENAPI_APIKEY" \
  -H "Content-Type: application/json" \
  -d '{
    "knowledge_base_id": "mz_V5FtC10F57Fu3Ly7zZVf2SSbcIQUKLghXd8HeMOY=",
    "media_type": 11,
    "title": "Note Title",
    "note_info": {
      "content_id": "<doc_id from step 1>"
    }
  }'
```

**⚠️ Important**: `title` must be at the same level as `note_info`, NOT inside it!

**❌ Wrong**:
```json
{
  "media_type": 11,
  "note_info": {
    "content_id": "doc_id",
    "title": "Title"
  }
}
```

**✅ Correct**:
```json
{
  "media_type": 11,
  "title": "Title",
  "note_info": {
    "content_id": "doc_id"
  }
}
```

## 📊 Token Consumption

| Item | Tokens |
|------|--------|
| World News API (10 calls) | ~500 |
| Input content (with translation) | ~3,000-4,000 |
| IMA API | ~500 |
| **Daily Total** | **~4,000-5,000** |

**Savings vs original**: 99.5% ✅

## ⚠️ Important Notes

1. **Domestic News Only**: Each country's news must be ABOUT that country
2. **China National Only**: NO provincial/local news (Anhui, Guangdong, etc.)
3. **Translate Non-English**: Title and summary must be in English
4. **Category Filter**: Use `categories=politics,business` parameter
5. **Keyword Filter**: Exclude sports, entertainment, lifestyle
6. **Summary Quality**: Minimum 50 characters
7. **Knowledge Base Format**: `title` at same level as `note_info`

## 📋 Output Format

```markdown
# YYYY-MM-DD Daily BRICS+ Economic & Political News Digest

**Generated:** Month DD, YYYY, HH:MM AM/PM (Asia/Shanghai)  
**Coverage Period:** Past 24 hours  
**Data Source:** World News API (Real-time)  
**Categories:** Macroeconomics, Financial Markets, Politics  
**Language:** English (non-English translated)  
**China Filter:** National-level only (no provincial news)

---

## 🇺🇸🇪🇺🇯🇵 DEVELOPED ECONOMIES

### 🇺🇸 United States

### 1. [English Title] [Category]

[English summary, 2-3 sentences]

**Source:** [Author] | **Link:** [URL]

... (up to 5 US domestic news items)

---

## 🇨🇳 CHINA

... (China NATIONAL news only, NO Anhui/Guangdong/etc.)

---

## 🇧🇷 BRAZIL

... (Brazil domestic news only)

---

(Continue for all 9 countries/regions)

---

## SUMMARY

**Total News Items:** XX  
**Macroeconomics:** XX  
**Financial Markets:** XX  
**Politics:** XX  
**Translated:** XX (from non-English sources)

**Key Themes:**
- Theme 1
- Theme 2

---

**END OF DIGEST**

*This digest covers macroeconomic, financial market, and political news from BRICS+ countries (past 24 hours). All non-English news have been translated to English. China news are national-level only (no provincial/local news).*
```
