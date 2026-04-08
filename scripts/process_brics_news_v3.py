#!/usr/bin/env python3
"""
Daily BRICS+ News Digest - 新闻处理脚本 v3
功能：筛选、AI 翻译（使用当前对话大模型能力）、分类、生成报告
"""

import json
import os
from datetime import datetime
from ai_translate import (
    detect_language,
    collect_texts_for_translation,
    apply_translations
)

COUNTRY_NAMES = {
    "eu": "🇪🇺 Eurozone", "us": "🇺🇸 United States", "jp": "🇯🇵 Japan",
    "br": "🇧🇷 Brazil", "ru": "🇷🇺 Russia", "in": "🇮🇳 India",
    "cn": "🇨🇳 China", "za": "🇿🇦 South Africa", "eg": "🇪🇬 Egypt",
    "bd": "🇧🇩 Bangladesh", "ae": "🇦🇪 UAE"
}

EXCLUDE_SPORTS = ["nfl", "nba", "mlb", "nhl", "premier league", "cricket match", "ipl"]
EXCLUDE_ENTERTAINMENT = ["celebrity", "movie premiere", "music award", "snl"]

COUNTRY_KEYWORDS = {
    "br": ["brazil", "brasileiro", "brasilia", "sao paulo", "petrobras"],
    "ru": ["russia", "russian", "moscow", "kremlin", "россия"],
    "in": ["india", "indian", "new delhi", "mumbai", "भारत"],
    "cn": ["china", "chinese", "beijing", "shanghai", "中国"],
    "eg": ["egypt", "egyptian", "cairo", "مصر"],
    "ae": ["uae", "dubai", "abu dhabi", "الإمارات"],
}

FINANCE_KEYWORDS = ["stock", "market", "bond", "currency", "oil", "gold", "banking", "investment"]
ECON_KEYWORDS = ["gdp", "inflation", "employment", "trade", "economy", "cpi", "wage"]

def should_exclude(news_item):
    """排除体育/娱乐新闻"""
    title = (news_item.get("title") or "").lower()
    url = (news_item.get("url") or "").lower()
    for kw in EXCLUDE_SPORTS:
        if kw in title + " " + url:
            return True
    for kw in EXCLUDE_ENTERTAINMENT:
        if kw in title + " " + url:
            return True
    return False

def is_relevant(news_item, country_code):
    """检查新闻与该国相关性"""
    title = (news_item.get("title") or "").lower()
    text = (news_item.get("text") or "").lower()
    for kw in COUNTRY_KEYWORDS.get(country_code, []):
        if kw in title + " " + text:
            return True
    return False

def categorize(news_item):
    """分类新闻"""
    title = (news_item.get("title") or "").lower()
    text = (news_item.get("text") or "").lower()
    for kw in FINANCE_KEYWORDS:
        if kw in title + " " + text:
            return "Financial Markets"
    for kw in ECON_KEYWORDS:
        if kw in title + " " + text:
            return "Macroeconomics"
    return "Politics/Geopolitics"

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

def process_news_with_translation(news_list, translate_callback):
    """
    处理新闻并进行翻译
    
    参数:
        news_list: 新闻列表
        translate_callback: 翻译回调函数，接收 texts_to_translate 列表，返回 translations 列表
    
    返回:
        处理后的新闻列表（已翻译）
    """
    # 1. 收集需要翻译的文本
    texts_to_translate = collect_texts_for_translation(news_list)
    
    if texts_to_translate:
        print(f"  需要翻译的文本：{len(texts_to_translate)} 条")
        
        # 2. 调用 AI 翻译（使用当前对话的大模型能力）
        translations = translate_callback(texts_to_translate)
        
        # 3. 应用翻译结果
        news_list = apply_translations(news_list, translations)
        print(f"  已翻译：{len(translations)} 条")
    
    return news_list

def main():
    """主函数"""
    print("=== BRICS 新闻收集任务 (v3) ===")
    print(f"执行时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_news = {}
    stats_total = {"total": 0, "translated": 0}
    
    for country_code in COUNTRY_NAMES.keys():
        filepath = f"/tmp/news_collection/{country_code}.json"
        if not os.path.exists(filepath):
            print(f"  {country_code}: 文件不存在")
            continue
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        news_list = data.get("news", [])
        if not news_list:
            print(f"  {country_code}: 无新闻数据")
            continue
        
        filtered = []
        for item in news_list:
            if should_exclude(item):
                continue
            if not is_relevant(item, country_code):
                continue
            
            # 获取摘要
            summary = item.get("summary")
            if not summary or len(summary) < 20:
                text = item.get("text", "")
                summary = simple_summarize(text, max_length=150)
            
            if not summary:
                continue
            
            item["summary"] = summary
            filtered.append(item)
        
        if filtered:
            all_news[country_code] = filtered
            stats_total["total"] += len(filtered)
            print(f"  ✅ {country_code}: {len(filtered)} 条")
    
    print(f"\n总计：{stats_total['total']} 条新闻")
    print("下一步：调用 AI 翻译（使用当前对话的大模型能力）")
    
    return all_news

if __name__ == "__main__":
    main()
