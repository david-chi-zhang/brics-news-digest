#!/usr/bin/env python3
import json
import os
from datetime import datetime

# Country configurations
COUNTRIES = {
    'eu': {'name': 'EUROZONE / EUROPEAN UNION', 'flag': '🇪🇺'},
    'us': {'name': 'UNITED STATES', 'flag': '🇺🇸'},
    'jp': {'name': 'JAPAN', 'flag': '🇯🇵'},
    'br': {'name': 'BRAZIL', 'flag': '🇧🇷'},
    'ru': {'name': 'RUSSIA', 'flag': '🇷🇺'},
    'in': {'name': 'INDIA', 'flag': '🇮🇳'},
    'cn': {'name': 'CHINA', 'flag': '🇨🇳'},
    'za': {'name': 'SOUTH AFRICA', 'flag': '🇿🇦'},
    'eg': {'name': 'EGYPT', 'flag': '🇪🇬'},
    'bd': {'name': 'BANGLADESH', 'flag': '🇧🇩'},
    'ae': {'name': 'UNITED ARAB EMIRATES', 'flag': '🇦🇪'},
}

# Keywords for filtering relevant news
ECONOMIC_KEYWORDS = ['economy', 'economic', 'gdp', 'inflation', 'trade', 'finance', 'bank', 'market', 'stock', 'bond', 'currency', 'interest rate', 'central bank', 'fiscal', 'monetary', 'budget', 'deficit', 'employment', 'unemployment', 'wage', 'salary', 'tax', 'tariff', 'export', 'import', 'investment', 'industry', 'manufacturing', 'energy', 'oil', 'gas', 'commodity']
POLITICAL_KEYWORDS = ['government', 'politics', 'election', 'policy', 'minister', 'president', 'parliament', 'congress', 'senate', 'diplomatic', 'foreign', 'military', 'defense', 'security', 'sanction', 'treaty', 'summit', 'geopolitical', 'conflict', 'war', 'peace', 'reform', 'legislation', 'regulation']
FINANCIAL_KEYWORDS = ['stock', 'market', 'exchange', 'trading', 'investor', 'share', 'bond', 'yield', 'currency', 'forex', 'crypto', 'bitcoin', 'fund', 'asset', 'portfolio', 'merger', 'acquisition', 'ipo', 'earnings', 'profit', 'loss', 'revenue', 'quarterly', 'annual report']

def is_relevant(title, text, description=''):
    """Check if news is relevant (economy, finance, or politics)"""
    content = (title + ' ' + text + ' ' + (description or '')).lower()
    
    # Check for economic/financial/political keywords
    for keyword in ECONOMIC_KEYWORDS + POLITICAL_KEYWORDS + FINANCIAL_KEYWORDS:
        if keyword in content:
            return True
    
    # Also accept if it's from a reputable news source and seems serious
    return False

def categorize_news(title, text, description=''):
    """Categorize news into Politics, Macroeconomics, or Financial Markets"""
    content = (title + ' ' + text + ' ' + (description or '')).lower()
    
    # Check financial markets first
    for keyword in FINANCIAL_KEYWORDS:
        if keyword in content:
            return 'Financial Markets'
    
    # Check macroeconomics
    for keyword in ['gdp', 'inflation', 'employment', 'trade', 'economic', 'economy', 'central bank', 'interest rate', 'fiscal', 'monetary']:
        if keyword in content:
            return 'Macroeconomics'
    
    # Default to Politics/Geopolitics
    return 'Politics/Geopolitics'

def process_country(country_code, config):
    """Process news for a single country"""
    filepath = f'/home/admin/openclaw/workspace/temp/news-digest/{country_code}.json'
    
    if not os.path.exists(filepath):
        return []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    news_items = []
    for article in data.get('news', [])[:10]:  # Get up to 10 articles
        title = article.get('title', '')
        text = article.get('text', '') or article.get('description', '') or ''
        url = article.get('url', '')
        source = article.get('source_country', country_code).upper()
        pub_date = article.get('publish_date', '')
        author = article.get('author', '')
        
        # Filter for relevant news
        if not is_relevant(title, text):
            continue
        
        category = categorize_news(title, text)
        
        news_items.append({
            'title': title,
            'url': url,
            'source': source,
            'pub_date': pub_date,
            'author': author,
            'text': text[:500] + '...' if len(text) > 500 else text,
            'category': category
        })
    
    # Return top 5 most relevant items
    return news_items[:5]

def generate_summary_stats(all_news):
    """Generate summary statistics"""
    total = sum(len(items) for items in all_news.values())
    politics = sum(1 for items in all_news.values() for item in items if item['category'] == 'Politics/Geopolitics')
    macro = sum(1 for items in all_news.values() for item in items if item['category'] == 'Macroeconomics')
    financial = sum(1 for items in all_news.values() for item in items if item['category'] == 'Financial Markets')
    
    return {
        'total': total,
        'countries': len(all_news),
        'politics': politics,
        'macro': macro,
        'financial': financial
    }

def generate_report():
    """Generate the full markdown report"""
    all_news = {}
    
    # Process all countries
    for country_code, config in COUNTRIES.items():
        news_items = process_country(country_code, config)
        all_news[country_code] = news_items
    
    # Generate markdown
    today = datetime.now()
    report_date = today.strftime('%B %d, %Y')
    report_time = today.strftime('%I:%M %p')
    
    md = []
    md.append('# Daily BRICS+ Economic & Political News Digest')
    md.append(f'**Date:** {report_date}')
    md.append('**Coverage Period:** Past 24 Hours')
    md.append('**Countries Covered:** 🇪🇺 Eurozone, 🇺🇸 US, 🇯🇵 Japan, 🇧🇷 Brazil, 🇷🇺 Russia, 🇮🇳 India, 🇨🇳 China, 🇿🇦 South Africa, 🇪🇬 Egypt, 🇧🇩 Bangladesh, 🇦🇪 UAE')
    md.append('')
    md.append('---')
    md.append('')
    
    # Generate sections for each country
    for country_code, config in COUNTRIES.items():
        news_items = all_news[country_code]
        
        md.append(f"## {config['flag']} {config['name']}")
        md.append('')
        
        if not news_items:
            md.append('*No relevant economic/political news found in the past 24 hours.*')
            md.append('')
        else:
            current_category = None
            for item in news_items:
                if item['category'] != current_category:
                    current_category = item['category']
                    md.append(f"### {current_category}")
                    md.append('')
                
                md.append(f"**{item['title']}**")
                md.append(f"- **Source:** [{item['source']}]({item['url']})")
                md.append(f"- **Published:** {item['pub_date']}")
                
                # Create a brief summary
                summary = item['text'].split('\n')[0][:200]
                if len(item['text']) > 200:
                    summary += '...'
                md.append(f"- **Summary:** {summary}")
                md.append('')
        
        md.append('---')
        md.append('')
    
    # Summary statistics
    stats = generate_summary_stats(all_news)
    md.append('## Summary Statistics')
    md.append('')
    md.append('| Metric | Value |')
    md.append('|--------|-------|')
    md.append(f"| **Total News Items** | {stats['total']} |")
    md.append(f"| **Countries/Regions** | {stats['countries']} (including EU) |")
    md.append(f"| **Politics/Geopolitics** | {stats['politics']} |")
    md.append(f"| **Macroeconomics** | {stats['macro']} |")
    md.append(f"| **Financial Markets** | {stats['financial']} |")
    md.append('')
    md.append(f"**Report Generated:** {report_date}, {report_time} (Asia/Shanghai)")
    md.append('**Source:** World News API')
    
    return '\n'.join(md), all_news

if __name__ == '__main__':
    report, all_news = generate_report()
    
    # Save the report
    os.makedirs('/home/admin/openclaw/workspace/temp/news-digest', exist_ok=True)
    with open('/home/admin/openclaw/workspace/temp/news-digest/daily-news-digest.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"Report generated: /home/admin/openclaw/workspace/temp/news-digest/daily-news-digest.md")
    print(f"Total news items: {sum(len(items) for items in all_news.values())}")
    
    # Print summary
    for country_code, items in all_news.items():
        print(f"{country_code.upper()}: {len(items)} items")
