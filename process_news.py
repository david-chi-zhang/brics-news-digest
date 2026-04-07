#!/usr/bin/env python3
import json
import os
from datetime import datetime
import re

# Country names and flags
COUNTRIES = {
    'eu': ('🇪🇺 Eurozone', ['eu', 'european union', 'eurozone', 'ecb', 'european commission', 'brussels']),
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
    'nba', 'nfl', 'mlb', 'nhl', 'fifa', 'world cup', 'olympics'
]

# Entertainment keywords to exclude
ENTERTAINMENT_KEYWORDS = [
    'celebrity', 'movie', 'music', 'award', 'entertainment', 'actor', 'actress', 'singer',
    'concert', 'album', 'film', 'hollywood', 'bollywood', 'oscar', 'grammy', 'netflix'
]

# Category keywords
FINANCIAL_KEYWORDS = [
    'stock', 'market', 'bond', 'currency', 'oil', 'gold', 'crypto', 'exchange', 'share',
    'banking', 'investment', 'fund', 'trading', 'ipo', 'earnings', 'dividend', 'portfolio',
    'hedge fund', 'private equity', 'venture capital', 'merger', 'acquisition'
]

MACRO_KEYWORDS = [
    'gdp', 'inflation', 'employment', 'trade', 'economic', 'economy', 'central bank',
    'pmi', 'cpi', 'deficit', 'fiscal', 'monetary', 'export', 'import', 'tariff', 'wage',
    'unemployment', 'interest rate', 'quantitative easing', 'stimulus', 'budget'
]

def is_sports(text):
    text_lower = text.lower()
    return any(kw in text_lower for kw in SPORTS_KEYWORDS)

def is_entertainment(text):
    text_lower = text.lower()
    return any(kw in text_lower for kw in ENTERTAINMENT_KEYWORDS)

def classify_news(text):
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

def is_relevant(text, country_code):
    """Check if news is relevant to the country"""
    text_lower = text.lower()
    _, keywords = COUNTRIES.get(country_code, ('', []))
    
    # For EU, be more flexible
    if country_code == 'eu':
        return True
    
    # Check if any country keyword appears
    return any(kw in text_lower for kw in keywords)

def translate_if_needed(text, lang='auto'):
    """Placeholder for translation - in production would call translation API"""
    # For now, just return as-is (API should return English)
    return text

def extract_summary(text, max_len=200):
    """Extract a summary from text"""
    if not text or len(text) < 50:
        return None
    
    # Try to get first sentence
    sentences = text.split('.')
    if sentences:
        summary = sentences[0].strip() + '.'
        if len(summary) > 20:
            return summary[:max_len]
    
    # Fallback: first 200 chars
    return text[:max_len].strip()

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
        category_api = item.get('category', '')
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
        
        # Extract summary from text
        summary = extract_summary(text)
        if not summary or len(summary) < 20:
            continue
        
        # Classify based on content
        category = classify_news(title + ' ' + text)
        
        processed.append({
            'title': title,
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
