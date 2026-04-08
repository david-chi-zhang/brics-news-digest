#!/usr/bin/env python3
"""
Daily BRICS+ News Digest - 新闻处理脚本 v4
使用 worldnewsapi 官方 Python 包
功能：获取、筛选、翻译、生成报告
"""

import json
import os
from datetime import datetime, timedelta
from ai_translate import (
    detect_language,
    collect_texts_for_translation,
    apply_translations
)

# 导入 worldnewsapi
try:
    import worldnewsapi
    from worldnewsapi.rest import ApiException
    USE_OFFICIAL_API = True
    print("✅ 使用 worldnewsapi 官方包 (v2.2.0)")
except ImportError:
    USE_OFFICIAL_API = False
    print("⚠️ worldnewsapi 未安装，使用备用方案")

COUNTRY_CODES = {
    "eu": "eu", "us": "us", "jp": "jp", "br": "br", "ru": "ru",
    "in": "in", "cn": "cn", "za": "za", "eg": "eg", "bd": "bd", "ae": "ae"
}

COUNTRY_NAMES = {
    "eu": "🇪🇺 Eurozone", "us": "🇺🇸 United States", "jp": "🇯🇵 Japan",
    "br": "🇧🇷 Brazil", "ru": "🇷🇺 Russia", "in": "🇮🇳 India",
    "cn": "🇨🇳 China", "za": "🇿🇦 South Africa", "eg": "🇪🇬 Egypt",
    "bd": "🇧🇩 Bangladesh", "ae": "🇦🇪 UAE"
}

EXCLUDE_SPORTS = ["nfl", "nba", "mlb", "nhl", "premier league", "cricket", "ipl"]
EXCLUDE_ENTERTAINMENT = ["celebrity", "movie", "music award", "snl"]

URL_COUNTRY_MAP = {
    "br": [".br", "globo.com", "uol.com.br"],
    "ru": [".ru", "ria.ru", "tass.ru"],
    "cn": [".cn", "chinadaily.com.cn"],
    "jp": [".jp", "japantimes.co.jp"],
    "in": [".in", "timesofindia.com"],
    "eg": [".eg", "ahram.org.eg"],
    "ae": [".ae", "gulfnews.com"],
    "za": [".za", "iol.co.za"],
}

COUNTRY_KEYWORDS = {
    "br": ["brazil", "brasileiro", "brasilia"],
    "ru": ["russia", "russian", "moscow"],
    "cn": ["china", "chinese", "beijing"],
    "jp": ["japan", "japanese", "tokyo"],
    "in": ["india", "indian", "new delhi"],
    "eg": ["egypt", "egyptian", "cairo"],
    "ae": ["uae", "dubai", "abu dhabi"],
    "za": ["south africa", "south african"],
}

def get_news_api():
    """初始化 World News API 客户端"""
    if not USE_OFFICIAL_API:
        return None
    
    api_key = os.environ.get("WORLD_NEWS_API_KEY")
    if not api_key:
        print("❌ 未设置 WORLD_NEWS_API_KEY 环境变量")
        return None
    
    configuration = worldnewsapi.Configuration(
        host="https://api.worldnewsapi.com"
    )
    configuration.api_key['apiKey'] = api_key
    
    return worldnewsapi.NewsApi(worldnewsapi.ApiClient(configuration))

def fetch_news_official(api_instance, country_code, from_date, to_date, number=10):
    """使用官方 API 获取新闻
    
    同时使用 source_country 和 text 参数获取关于该国的新闻
    - source_country: 来自该国媒体的新闻
    - text: 新闻内容包含该国名称（获取国际媒体报道）
    """
    try:
        # 国家名称（用于 text 搜索）
        COUNTRY_NAMES_FOR_TEXT = {
            "eu": "European Union",
            "us": "United States",
            "jp": "Japan",
            "br": "Brazil",
            "ru": "Russia",
            "in": "India",
            "cn": "China",
            "za": "South Africa",
            "eg": "Egypt",
            "bd": "Bangladesh",
            "ae": "United Arab Emirates"
        }
        
        country_name = COUNTRY_NAMES_FOR_TEXT.get(country_code, country_code)
        
        # 同时搜索：来自该国媒体 OR 关于该国的新闻
        response = api_instance.search_news(
            source_country=country_code,  # 来自该国媒体
            text=country_name,  # 或新闻内容包含该国名称
            earliest_publish_date=from_date,
            latest_publish_date=to_date,
            number=number
        )
        
        # 转换为统一的新闻格式
        news_list = []
        if hasattr(response, 'news') and response.news:
            for news in response.news:
                news_item = {
                    "title": news.title if hasattr(news, 'title') else "",
                    "url": news.url if hasattr(news, 'url') else "",
                    "summary": news.summary if hasattr(news, 'summary') else "",
                    "text": news.text if hasattr(news, 'text') else "",
                    "published_date": news.published_date if hasattr(news, 'published_date') else "",
                    "source": news.source if hasattr(news, 'source') else "",
                    "category": news.category if hasattr(news, 'category') else "",
                }
                news_list.append(news_item)
        
        return news_list
    
    except ApiException as e:
        print(f"  ❌ API 错误：{e}")
        return []

def fetch_news_backup(country_code, from_date, to_date, number=10):
    """备用方案：使用 curl 获取新闻"""
    import subprocess
    
    api_key = os.environ.get("WORLD_NEWS_API_KEY", "")
    http_proxy = os.environ.get("HTTP_PROXY", "")
    
    cmd = [
        "curl", "-s",
        f"https://api.worldnewsapi.com/search-news",
        "-d", f"source-countries={country_code}",
        "-d", f"api-key={api_key}",
        "-d", f"from={from_date}",
        "-d", f"to={to_date}",
        "-d", f"number={number}",
        "-d", "sort-by=publish_date"
    ]
    
    if http_proxy:
        cmd.extend(["-x", http_proxy])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        data = json.loads(result.stdout)
        return data.get("news", [])
    except Exception as e:
        print(f"  ❌ 备用方案失败：{e}")
        return []

def is_relevant_by_url(news_item, country_code):
    """通过 URL 域名验证相关性"""
    url = news_item.get("url", "").lower()
    for domain in URL_COUNTRY_MAP.get(country_code, []):
        if domain in url:
            return True
    return False

def is_relevant_by_text(news_item, country_code):
    """通过正文内容验证相关性"""
    text = (news_item.get("text") or "").lower()
    for kw in COUNTRY_KEYWORDS.get(country_code, []):
        if kw in text:
            return True
    return False

def should_exclude(news_item):
    """排除体育/娱乐新闻"""
    title = (news_item.get("title") or "").lower()
    url = (news_item.get("url") or "").lower()
    category = (news_item.get("category") or "").lower()
    
    if category in ["sports", "entertainment", "lifestyle"]:
        return True
    
    for kw in EXCLUDE_SPORTS:
        if kw in title + " " + url:
            return True
    
    for kw in EXCLUDE_ENTERTAINMENT:
        if kw in title + " " + url:
            return True
    
    return False

def simple_summarize(text, max_length=150):
    """从正文提取摘要"""
    if not text or len(text) < 50:
        return None
    
    sentences = text.replace('\n', ' ').split('.')
    summary = ""
    for sentence in sentences:
        sentence = sentence.strip() + ". "
        if len(summary) + len(sentence) <= max_length:
            summary += sentence
        else:
            break
    
    return summary.strip() if len(summary) > 20 else None

def filter_news(news_list, country_code, max_items=5):
    """两阶段筛选新闻"""
    filtered = []
    titles_to_translate = []
    
    for item in news_list:
        # 阶段 1: 不依赖标题的筛选
        
        # 1. URL 域名验证
        if not is_relevant_by_url(item, country_code):
            # 2. 正文字段验证
            if not is_relevant_by_text(item, country_code):
                continue
        
        # 3. 排除体育/娱乐（通过分类字段）
        if should_exclude(item):
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
            titles_to_translate.append({
                "index": len(filtered),
                "title": title,
                "lang": title_lang
            })
        
        filtered.append(item)
    
    # 阶段 2: 翻译非英语标题
    if titles_to_translate:
        print(f"    需要翻译的标题：{len(titles_to_translate)} 条")
        # 这里调用 AI 翻译（简化版，实际应调用 AI）
        for item in titles_to_translate:
            filtered[item["index"]]["title"] = f"[{item['lang'].upper()}] {item['title'][:50]}"
    
    # 阶段 3: 翻译后再筛选
    final_filtered = []
    for item in filtered:
        if should_exclude(item):
            continue
        final_filtered.append(item)
        if len(final_filtered) >= max_items:
            break
    
    return final_filtered

def translate_all_news(news_list, translate_callback):
    """翻译所有收录新闻的标题和摘要"""
    texts_to_translate = collect_texts_for_translation(news_list)
    
    if texts_to_translate:
        print(f"  需要翻译的文本：{len(texts_to_translate)} 条")
        translations = translate_callback(texts_to_translate)
        news_list = apply_translations(news_list, translations)
        print(f"  已翻译：{len(translations)} 条")
    
    return news_list

def main():
    """主函数"""
    print("=" * 60)
    print("BRICS+ 每日新闻收集任务 (v4 - worldnewsapi)")
    print("=" * 60)
    print(f"执行时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 初始化 API
    api_instance = get_news_api()
    
    # 计算日期范围
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    from_date = yesterday.strftime("%Y-%m-%d")
    to_date = today.strftime("%Y-%m-%d")
    
    print(f"\n时间范围：{from_date} 至 {to_date}")
    
    all_news = {}
    stats_total = {"total": 0, "api_success": 0, "api_failed": 0}
    
    # 获取每个国家的新闻
    for country_code, country_name in COUNTRY_NAMES.items():
        print(f"\n{country_name} ({country_code.upper()})")
        
        # 获取新闻
        if api_instance:
            news_list = fetch_news_official(api_instance, country_code, from_date, to_date, number=10)
            if news_list:
                stats_total["api_success"] += 1
            else:
                stats_total["api_failed"] += 1
                # 使用备用方案
                print(f"  使用备用方案...")
                news_list = fetch_news_backup(country_code, from_date, to_date, number=10)
        else:
            news_list = fetch_news_backup(country_code, from_date, to_date, number=10)
        
        if not news_list:
            print(f"  ❌ 无新闻数据")
            continue
        
        print(f"  获取：{len(news_list)} 条")
        
        # 筛选新闻
        filtered = filter_news(news_list, country_code, max_items=5)
        
        if filtered:
            all_news[country_code] = filtered
            stats_total["total"] += len(filtered)
            print(f"  ✅ 收录：{len(filtered)} 条")
        else:
            print(f"  ❌ 无符合要求的新闻")
    
    print(f"\n{'=' * 60}")
    print(f"总计：{stats_total['total']} 条新闻")
    print(f"API 成功：{stats_total['api_success']}/{len(COUNTRY_NAMES)}")
    print(f"下一步：翻译新闻 → 生成报告 → 上传 IMA")
    print(f"{'=' * 60}")
    
    return all_news

if __name__ == "__main__":
    main()
