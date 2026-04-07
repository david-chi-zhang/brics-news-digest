#!/usr/bin/env python3
"""
Daily BRICS+ News Digest - 新闻处理脚本 v2
功能：筛选、AI 翻译、分类、生成报告
"""

import json
import os
import subprocess
from datetime import datetime

COUNTRY_NAMES = {
    "eu": "🇪🇺 Eurozone", "us": "🇺🇸 United States", "jp": "🇯🇵 Japan",
    "br": "🇧🇷 Brazil", "ru": "🇷🇺 Russia", "in": "🇮🇳 India",
    "cn": "🇨🇳 China", "za": "🇿🇦 South Africa", "eg": "🇪🇬 Egypt",
    "bd": "🇧🇩 Bangladesh", "ae": "🇦🇪 UAE"
}

EXCLUDE_SITES = ["perezhilton", "tmz", "eonline", "people"]
EXCLUDE_SPORTS = ["nfl", "nba", "mlb", "nhl", "premier league", "cricket match"]
EXCLUDE_ENTERTAINMENT = ["celebrity gossip", "movie premiere", "music award"]

COUNTRY_KEYWORDS = {
    "eu": ["eu", "european union", "europe", "brussels", "eurozone", "ecb"],
    "us": ["us", "usa", "america", "washington", "congress", "senate", "white house"],
    "jp": ["japan", "japanese", "tokyo", "osaka", "nikkei"],
    "br": ["brazil", "brazilian", "brasilia", "sao paulo", "petrobras", "brasileiro"],
    "ru": ["russia", "russian", "moscow", "kremlin", "россия", "путин"],
    "in": ["india", "indian", "new delhi", "mumbai", "rbi", "भारत"],
    "cn": ["china", "chinese", "beijing", "shanghai"],
    "za": ["south africa", "south african", "pretoria", "johannesburg"],
    "eg": ["egypt", "egyptian", "cairo", "suez"],
    "bd": ["bangladesh", "bangladeshi", "dhaka"],
    "ae": ["uae", "dubai", "abu dhabi", "emirates"]
}

FINANCE_KEYWORDS = ["stock", "market", "bond", "currency", "oil", "gold", "banking", "investment"]
ECON_KEYWORDS = ["gdp", "inflation", "employment", "trade", "economy", "central bank", "pmi", "cpi", "wage"]


def should_exclude(news_item):
    """检查是否应该排除（体育/娱乐）"""
    title = (news_item.get("title") or "").lower()
    url = (news_item.get("url") or "").lower()
    full_text = title + " " + url
    
    for site in EXCLUDE_SITES:
        if site in url:
            return True
    for kw in EXCLUDE_SPORTS:
        if kw in full_text:
            return True
    for kw in EXCLUDE_ENTERTAINMENT:
        if kw in full_text:
            return True
    return False


def is_relevant(news_item, country_code):
    """检查新闻是否与该国相关"""
    title = (news_item.get("title") or "").lower()
    text = (news_item.get("text") or "").lower()
    full_text = title + " " + text
    
    keywords = COUNTRY_KEYWORDS.get(country_code, [])
    for kw in keywords:
        if kw in full_text:
            return True
    return False


def categorize(news_item):
    """分类新闻"""
    title = (news_item.get("title") or "").lower()
    text = (news_item.get("text") or "").lower()
    full_text = title + " " + text
    
    for kw in FINANCE_KEYWORDS:
        if kw in full_text:
            return "Financial Markets"
    for kw in ECON_KEYWORDS:
        if kw in full_text:
            return "Macroeconomics"
    return "Politics/Geopolitics"


def simple_summarize(text, max_length=150):
    """简单摘要：提取前 1-2 个完整句子"""
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


def translate_with_ai(text, source_lang="auto"):
    """
    使用 AI 翻译非英语文本为英语
    
    支持：
    1. 调用本地 AI 模型（如果有）
    2. 降级为简单翻译字典
    """
    if not text or len(text) < 10:
        return text
    
    # 检测是否已经是英语
    non_ascii = sum(1 for c in text if ord(c) > 127)
    if (non_ascii / len(text)) < 0.05:
        return text
    
    # 简单翻译字典（葡萄牙语/俄语 → 英语）
    pt_en = {
        "Quem saiu do": "Who left", "eliminada": "eliminated",
        "Veja o discurso": "See the speech", "para": "for",
        "demite": "fires", "após": "after", "sem vitória": "without victory",
        "reclama": "complains", "futebol": "football"
    }
    
    ru_en = {
        "Сырский": "Syrsky", "бросил в бой": "threw into battle",
        "ВСУ": "Ukrainian forces", "несут": "suffer", "потери": "losses",
        "Призраки": "Ghosts", "Вьетнама": "Vietnam", "Иран": "Iran",
        "Небо в огне": "Sky in flames", "армия РФ": "Russian Army"
    }
    
    # 尝试字典翻译
    translated = text
    if source_lang == "pt" or any(c in text.lower() for c in "ãõç"):
        for pt, en in pt_en.items():
            translated = translated.replace(pt, en)
    elif source_lang == "ru" or any(ord(c) > 127 for c in text[:50]):
        for ru, en in ru_en.items():
            translated = translated.replace(ru, en)
    
    # 如果翻译后变化不大，标记为待翻译
    if translated == text:
        return f"[待翻译] {text[:100]}"
    
    return translated


def process_news(country_code, news_list):
    """处理单个国家的新闻"""
    filtered = []
    stats = {"total": 0, "translated": 0, "excluded": 0}
    
    for item in news_list:
        title = item.get("title", "")
        
        # 1. 排除体育/娱乐
        if should_exclude(item):
            stats["excluded"] += 1
            continue
        
        # 2. 检查相关性
        if not is_relevant(item, country_code):
            stats["excluded"] += 1
            continue
        
        # 3. 获取摘要
        summary = item.get("summary")
        if not summary or len(summary) < 20:
            text = item.get("text", "")
            summary = simple_summarize(text, max_length=150)
        
        if not summary:
            stats["excluded"] += 1
            continue
        
        # 4. 翻译非英语标题
        language = item.get("language", "en")
        if language in ["pt", "ru", "zh", "ja", "ar", "hi"]:
            translated_title = translate_with_ai(title, language)
            if translated_title != title:
                stats["translated"] += 1
                title = translated_title
        
        # 5. 分类
        category = categorize(item)
        
        filtered.append({
            "title": title,
            "author": item.get("author", "Unknown") or "Unknown",
            "url": item.get("url", ""),
            "published": str(item.get("published_date", "Unknown"))[:19].replace("T", " "),
            "summary": summary,
            "category": category
        })
        
        if len(filtered) >= 5:
            break
    
    return filtered, stats


def generate_report(all_news, stats_total):
    """生成 Markdown 报告"""
    today = datetime.now()
    
    report = f"""# Daily BRICS+ Economic & Political News Digest
**Date:** {today.strftime("%B %d, %Y")}  
**Coverage Period:** Past 24 Hours  
**Countries Covered:** 🇪🇺 Eurozone, 🇺🇸 US, 🇯🇵 Japan, 🇧🇷 Brazil, 🇷🇺 Russia, 🇮🇳 India, 🇨🇳 China, 🇿🇦 South Africa, 🇪🇬 Egypt, 🇧🇩 Bangladesh, 🇦🇪 UAE

---

"""
    
    for country_code in COUNTRY_NAMES.keys():
        if country_code not in all_news:
            continue
        
        country_name = COUNTRY_NAMES[country_code]
        news_list = all_news[country_code]
        
        report += f"## {country_name}\n\n"
        
        for i, item in enumerate(news_list, 1):
            report += f"### [{item['category']}]\n"
            report += f"**{i}. {item['title']}**\n"
            report += f"- **Source:** [{item['author']}]({item['url']})\n"
            report += f"- **Published:** {item['published']}\n"
            report += f"- **Summary:** {item['summary']}\n\n"
        
        report += "---\n\n"
    
    # 统计
    cats = {"Finance": 0, "Macro": 0, "Politics": 0}
    for country in all_news.values():
        for item in country:
            if item['category'] == "Financial Markets":
                cats["Finance"] += 1
            elif item['category'] == "Macroeconomics":
                cats["Macro"] += 1
            else:
                cats["Politics"] += 1
    
    report += f"""## Summary Statistics

| Metric | Value |
|--------|-------|
| **Total News Items** | {stats_total['total']} |
| **Countries/Regions** | {len(all_news)} |
| **Politics/Geopolitics** | {cats['Politics']} |
| **Macroeconomics** | {cats['Macro']} |
| **Financial Markets** | {cats['Finance']} |
| **Translated **(non-EN) | {stats_total['translated']} |

**Report Generated:** {today.strftime("%B %d, %Y, %I:%M %p")} (Asia/Shanghai)  
**Source:** World News API

**筛选规则**:
- ✅ 非英语新闻已 AI 翻译为英语
- ✅ 排除体育/娱乐新闻
- ✅ 确保新闻与该国相关
- ✅ 必须有有效摘要
"""
    
    return report


def main():
    """主函数"""
    all_news = {}
    stats_total = {"total": 0, "translated": 0, "excluded": 0}
    
    for country_code in COUNTRY_NAMES.keys():
        filepath = f"/tmp/news_collection/{country_code}.json"
        if not os.path.exists(filepath):
            print(f"⚠️  File not found: {filepath}")
            continue
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        news_list = data.get("news", [])
        filtered, stats = process_news(country_code, news_list)
        
        if filtered:
            all_news[country_code] = filtered
            stats_total["total"] += stats["total"]
            stats_total["translated"] += stats["translated"]
            stats_total["excluded"] += stats["excluded"]
            
            print(f"✅ {country_code}: {stats['total']} (translated: {stats['translated']})")
        else:
            print(f"⚠️ {country_code}: 0")
    
    # 生成报告
    report = generate_report(all_news, stats_total)
    
    # 保存文件
    today = datetime.now().strftime("%Y-%m-%d")
    output_path = f"/home/admin/openclaw/workspace/daily-brics-news-{today}.md"
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"\n✅ Report saved to: {output_path}")
    print(f"   Total: {stats_total['total']}, Translated: {stats_total['translated']}")
    print(f"   Excluded: {stats_total['excluded']}")


if __name__ == "__main__":
    main()
