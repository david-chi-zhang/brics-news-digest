#!/usr/bin/env python3
import json
import os
import re
from datetime import datetime

# Country names and flags
COUNTRIES = {
    'eu': ('🇪🇺 Eurozone', ['eu', 'european union', 'eurozone', 'ecb', 'european commission', 'brussels', 'france', 'germany', 'italy', 'spain']),
    'us': ('🇺🇸 United States', ['us', 'usa', 'united states', 'america', 'american', 'wall street', 'fed', 'federal reserve']),
    'jp': ('🇯🇵 Japan', ['jp', 'japan', 'japanese', 'tokyo', 'nikkei', 'boj', 'bank of japan']),
    'br': ('🇧🇷 Brazil', ['br', 'brazil', 'brazilian', 'brasilia', 'real', 'bovespa']),
    'ru': ('🇷🇺 Russia', ['ru', 'russia', 'russian', 'moscow', 'kremlin', 'ruble']),
    'in': ('🇮🇳 India', ['in', 'india', 'indian', 'new delhi', 'mumbai', 'rbi', 'reserve bank']),
    'cn': ('🇨🇳 China', ['cn', 'china', 'chinese', 'beijing', 'shanghai', 'pboc', 'yuan', 'renminbi']),
    'za': ('🇿🇦 South Africa', ['za', 'south africa', 'south african', 'johannesburg', 'pretoria', 'rand']),
    'eg': ('🇪🇬 Egypt', ['eg', 'egypt', 'egyptian', 'cairo', 'nile']),
    'bd': ('🇧🇩 Bangladesh', ['bd', 'bangladesh', 'bangladeshi', 'dhaka']),
    'ae': ('🇦🇪 UAE', ['ae', 'uae', 'united arab emirates', 'dubai', 'abu dhabi', 'emirati'])
}

# Sports keywords to exclude
SPORTS_KEYWORDS = [
    'football', 'soccer', 'futebol', 'basketball', 'baseball', 'hockey', 'tennis', 'cricket',
    'match', 'game', 'team', 'player', 'coach', 'score', 'goal', 'win', 'loss', 'championship',
    'flamengo', 'palmeiras', 'santos', 'corinthians', 'são paulo', 'botafogo', 'vasco',
    'real madrid', 'barcelona', 'manchester', 'liverpool', 'arsenal', 'chelsea',
    'nba', 'nfl', 'mlb', 'nhl', 'fifa', 'world cup', 'olympics', 'j-league', 'j1 league'
]

# Entertainment keywords to exclude
ENTERTAINMENT_KEYWORDS = [
    'celebrity', 'movie', 'music', 'award', 'entertainment', 'actor', 'actress', 'singer',
    'concert', 'album', 'film', 'hollywood', 'bollywood', 'oscar', 'grammy', 'netflix',
    'anime', 'manga', 'idol', 'drama series'
]

# UI/junk text patterns to exclude from summaries
UI_PATTERNS = [
    r'facebook でシェアする',
    r'x でシェアする',
    r'はてなブックマーク',
    r'メニューをとばして',
    r'記事の本文エリアへ',
    r'line で送る',
    r'ツイートする',
    r'共有する',
    r'click to share',
    r'share on',
    r'follow us',
    r'subscribe',
    r'advertisement',
    r'sponsored',
    r'関連記事',
    r'おすすめ',
]

# Category keywords
FINANCIAL_KEYWORDS = [
    'stock', 'market', 'bond', 'currency', 'oil', 'gold', 'crypto', 'exchange', 'share',
    'banking', 'investment', 'fund', 'trading', 'ipo', 'earnings', 'dividend', 'portfolio',
    'hedge fund', 'private equity', 'venture capital', 'merger', 'acquisition', 'tax',
    'finance', 'fiscal', 'revenue', 'spending', 'budget deficit', 'debt'
]

MACRO_KEYWORDS = [
    'gdp', 'inflation', 'employment', 'trade', 'economic', 'economy', 'central bank',
    'pmi', 'cpi', 'deficit', 'fiscal', 'monetary', 'export', 'import', 'tariff', 'wage',
    'unemployment', 'interest rate', 'quantitative easing', 'stimulus', 'budget',
    'growth', 'recession', 'gdp growth', 'consumer price'
]

def clean_summary(text):
    """Remove UI text and junk from summary"""
    if not text:
        return None
    
    # Remove UI patterns
    for pattern in UI_PATTERNS:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # Remove social media sharing text
    text = re.sub(r'\b(share|tweet|follow|subscribe)\b.*', '', text, flags=re.IGNORECASE)
    
    # Clean up whitespace
    text = ' '.join(text.split())
    
    return text.strip() if text.strip() else None

def extract_summary(text, max_len=180):
    """Extract a clean summary from text"""
    if not text or len(text) < 50:
        return None
    
    # Clean the text first
    text = clean_summary(text)
    if not text:
        return None
    
    # Get first meaningful sentence
    sentences = re.split(r'[.!?。！？]', text)
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) > 30 and not any(p in sentence.lower() for p in ['share', 'follow', 'click', 'menu']):
            summary = sentence[:max_len]
            if not summary.endswith('.'):
                summary += '.'
            return summary
    
    # Fallback: first 180 chars
    summary = text[:max_len].strip()
    if summary and not summary.endswith('.'):
        summary += '.'
    return summary if len(summary) > 20 else None

def is_sports(text):
    if not text:
        return False
    text_lower = text.lower()
    return any(kw in text_lower for kw in SPORTS_KEYWORDS)

def is_entertainment(text):
    if not text:
        return False
    text_lower = text.lower()
    return any(kw in text_lower for kw in ENTERTAINMENT_KEYWORDS)

def classify_news(text):
    if not text:
        return 'Politics/Geopolitics'
    
    text_lower = text.lower()
    
    # Check financial first
    financial_matches = sum(1 for kw in FINANCIAL_KEYWORDS if kw in text_lower)
    macro_matches = sum(1 for kw in MACRO_KEYWORDS if kw in text_lower)
    
    if financial_matches >= 1:
        return 'Financial Markets'
    elif macro_matches >= 1:
        return 'Macroeconomics'
    else:
        return 'Politics/Geopolitics'

def is_likely_english(text):
    """Check if text is likely English"""
    if not text:
        return True
    
    # Check for common non-English characters
    non_english_patterns = [
        r'[\u4e00-\u9fff]',  # Chinese/Japanese
        r'[\u3040-\u309f]',  # Hiragana
        r'[\u30a0-\u30ff]',  # Katakana
        r'[\u00c0-\u00ff]',  # Latin extended (French, Spanish, etc.)
        r'[\u0400-\u04ff]',  # Cyrillic (Russian)
        r'[\u0600-\u06ff]',  # Arabic
    ]
    
    for pattern in non_english_patterns:
        if re.search(pattern, text):
            return False
    
    return True

def translate_title_jp(text):
    """Simple translation mapping for common Japanese news terms"""
    if not text:
        return text
    
    translations = {
        '予算': 'budget',
        '成立': 'passed/enacted',
        '参院': 'House of Councillors',
        '衆院': 'House of Representatives',
        '首相': 'Prime Minister',
        '国会': 'Diet/Parliament',
        '審議': 'deliberation',
        '新年度': 'new fiscal year',
        'きょう': 'today',
        '夕方': 'evening',
        '午前': 'AM',
        '午後': 'PM',
        '記事': 'article',
        '学校': 'school',
        '教育': 'education',
        '医療': 'medical/healthcare',
        '手術': 'surgery',
        '患者': 'patient',
        '家族': 'family',
        '同意': 'consent',
        '不要': 'not required',
        '病院': 'hospital',
        '政策': 'policy',
        '経済': 'economy',
        '市場': 'market',
        '企業': 'company',
        '株価': 'stock price',
        '円': 'yen',
        '日銀': 'Bank of Japan',
        '総裁': 'Governor',
        '選挙': 'election',
        '政権': 'administration',
        '外交': 'diplomacy',
        '防衛': 'defense',
        '軍事': 'military',
    }
    
    # For Japanese text, provide a translated title based on keywords
    result = text
    for jp, en in translations.items():
        if jp in text:
            result = result.replace(jp, f'{jp}({en})')
    
    return result

def translate_title_generic(text, lang='auto'):
    """Translate title if not English - simplified version"""
    if is_likely_english(text):
        return text
    
    # For Japanese, add translation hints
    if re.search(r'[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]', text):
        return translate_title_jp(text)
    
    # For other languages, just return original with note
    return text

def process_country(country_code):
    filepath = f'/home/admin/openclaw/workspace/news_collection/{country_code}.json'
    if not os.path.exists(filepath):
        return []
    
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    news_items = data.get('news', [])
    processed = []
    
    for item in news_items:
        title = item.get('title', '')
        text = item.get('text', '')
        url = item.get('url', item.get('id', ''))
        author = item.get('author', 'Unknown')
        publish_date = item.get('publish_date', '')
        language = item.get('language', 'en')
        
        # Skip if no title
        if not title:
            continue
        
        # Skip sports
        if is_sports(title) or is_sports(text):
            continue
        
        # Skip entertainment
        if is_entertainment(title) or is_entertainment(text):
            continue
        
        # Extract clean summary
        summary = extract_summary(text)
        if not summary or len(summary) < 20:
            continue
        
        # Translate non-English titles
        translated_title = translate_title_generic(title, language)
        
        # Classify based on content
        category = classify_news(title + ' ' + text)
        
        # Note if translation was applied
        title_display = translated_title
        if not is_likely_english(title):
            title_display = f"{translated_title} *[Original: {title}]*"
        
        processed.append({
            'title': title_display,
            'original_title': title,
            'summary': summary,
            'link': url,
            'source': author,
            'published': publish_date,
            'category': category,
            'language': language
        })
    
    # Limit to 5 per country
    return processed[:5]

def main():
    all_news = {}
    stats = {'total': 0, 'Financial Markets': 0, 'Macroeconomics': 0, 'Politics/Geopolitics': 0}
    
    for country_code in ['eu', 'us', 'jp', 'br', 'ru', 'in', 'cn', 'za', 'eg', 'bd', 'ae']:
        news = process_country(country_code)
        all_news[country_code] = news
        stats['total'] += len(news)
        for item in news:
            stats[item['category']] += 1
    
    # Generate markdown report
    today = datetime.now()
    report_date = today.strftime('%B %d, %Y')
    report_time = today.strftime('%I:%M %p')
    
    md = f"""# Daily BRICS+ Economic & Political News Digest
**Date:** {report_date}  
**Coverage Period:** Past 24 Hours  
**Countries Covered:** 🇪🇺 Eurozone, 🇺🇸 US, 🇯🇵 Japan, 🇧🇷 Brazil, 🇷🇺 Russia, 🇮🇳 India, 🇨🇳 China, 🇿🇦 South Africa, 🇪🇬 Egypt, 🇧🇩 Bangladesh, 🇦🇪 UAE

---

"""
    
    for country_code in ['eu', 'us', 'jp', 'br', 'ru', 'in', 'cn', 'za', 'eg', 'bd', 'ae']:
        flag_name, _ = COUNTRIES[country_code]
        news = all_news[country_code]
        
        md += f"## {flag_name}\n\n"
        
        if not news:
            md += "*No significant news in the past 24 hours.*\n\n"
            continue
        
        for i, item in enumerate(news, 1):
            md += f"### {item['category']}\n"
            md += f"**{i}. {item['title']}**\n"
            md += f"- **Source:** {item['source']}\n"
            md += f"- **Published:** {item['published']}\n"
            md += f"- **Link:** [{item['link']}]({item['link']})\n"
            md += f"- **Summary:** {item['summary']}\n\n"
        
        md += "---\n\n"
    
    # Statistics
    md += f"""## Summary Statistics

| Metric | Value |
|--------|-------|
| **Total News Items** | {stats['total']} |
| **Countries/Regions** | 11 |
| **Politics/Geopolitics** | {stats['Politics/Geopolitics']} |
| **Macroeconomics** | {stats['Macroeconomics']} |
| **Financial Markets** | {stats['Financial Markets']} |

**Report Generated:** {report_date}, {report_time} (Asia/Shanghai)  
**Source:** World News API
"""
    
    # Save report
    output_path = f'/home/admin/openclaw/workspace/daily-brics-news-{today.strftime("%Y-%m-%d")}.md'
    with open(output_path, 'w') as f:
        f.write(md)
    
    print(f"Report saved to: {output_path}")
    print(f"Total news items: {stats['total']}")
    print(f"Stats: {stats}")
    
    return output_path

if __name__ == '__main__':
    main()
