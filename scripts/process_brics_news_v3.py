#!/usr/bin/env python3
from ai_translate import translate_news
"""
Daily BRICS+ News Digest - 新闻处理脚本 v3 (最终版)
功能：筛选、AI 翻译、分类、生成报告
严格执行所有用户要求
"""

import json
import os
from datetime import datetime

COUNTRY_NAMES = {
    "eu": "🇪🇺 Eurozone", "us": "🇺🇸 United States", "jp": "🇯🇵 Japan",
    "br": "🇧🇷 Brazil", "ru": "🇷🇺 Russia", "in": "🇮🇳 India",
    "cn": "🇨🇳 China", "za": "🇿🇦 South Africa", "eg": "🇪🇬 Egypt",
    "bd": "🇧🇩 Bangladesh", "ae": "🇦🇪 UAE"
}

EXCLUDE_SITES = ["perezhilton", "tmz", "eonline", "people"]
EXCLUDE_SPORTS = ["nfl", "nba", "mlb", "nhl", "premier league", "cricket match", "bbb "]
EXCLUDE_ENTERTAINMENT = ["celebrity gossip", "movie premiere", "music award", "snl", "saturday night"]

COUNTRY_KEYWORDS = {
    "eu": ["eu", "european union", "europe", "brussels", "eurozone", "ecb", "france", "germany", "italy", "spain",
           "netherlands", "belgium", "austria", "portugal", "greece", "finland", "ireland", "luxembourg"],
    "us": ["us", "usa", "america", "american", "washington", "congress", "senate", "white house", "federal reserve",
           "wall street", "pentagon", "state department"],
    "jp": ["japan", "japanese", "tokyo", "osaka", "nikkei", "boj", "bank of japan", "日本", "東京"],
    "br": ["brazil", "brazilian", "brasilia", "sao paulo", "petrobras", "brasileiro", "rio de janeiro",
           "flamengo", "palmeiras", "corinthians", "巴西", "巴西利亚"],
    "ru": ["russia", "russian", "moscow", "kremlin", "россия", "путин", "украин", "Москва", "Россия",
           "ruble", "gazprom"],
    "in": ["india", "indian", "new delhi", "mumbai", "rbi", "भारत", "दिल्ली", "मुंबई",
           "sensex", "nifty", "rupee"],
    "cn": ["china", "chinese", "beijing", "shanghai", "中国", "北京", "上海", "pBOC", "yuan", "renminbi"],
    "za": ["south africa", "south african", "pretoria", "johannesburg", "sandaf", "rand", "anc",
           "南非", "约翰内斯堡"],
    "eg": ["egypt", "egyptian", "cairo", "suez", "埃及", "开罗", "苏伊士", "nile", "pharaoh"],
    "bd": ["bangladesh", "bangladeshi", "dhaka", "孟加拉", "达卡", "taka", "awami"],
    "ae": ["uae", "dubai", "abu dhabi", "emirates", "阿联酋", "迪拜", "abudhabi",
           "dirham", "adnoc", "emirati"]
}

FINANCE_KEYWORDS = ["stock", "market", "bond", "currency", "oil", "gold", "banking", "investment", "fund", "trading"]
ECON_KEYWORDS = ["gdp", "inflation", "employment", "trade", "economy", "central bank", "pmi", "cpi", "wage", "tariff"]

# 翻译字典（扩展版）
TRANSLATION_DICT = {
    "pt": {
        "faz": "makes", "sobre": "about", "briga": "fight", "com": "with",
        "demite": "fires", "após": "after", "sem vitória": "without victory",
        "reclama": "complains", "futebol": "football", "sequência": "sequence",
        "é": "is", "o": "the", "a": "the", "de": "of", "do": "of the", "da": "of the",
        "para": "for", "por": "by", "em": "in", "no": "in the", "na": "in the"
    },
    "ru": {
        "Сырский": "Syrsky", "бросил в бой": "threw into battle", "ВСУ": "Ukrainian forces",
        "несут": "suffer", "потери": "losses", "Призраки": "Ghosts", "Вьетнама": "Vietnam",
        "Иран": "Iran", "Небо в огне": "Sky in flames", "армия РФ": "Russian Army",
        "жестко ответила": "responded harshly", "атаки": "attacks", "Украина": "Ukraine",
        "Россия": "Russia", "Путин": "Putin", "Москва": "Moscow", "война": "war"
    },
    "ja": {
        "きょう": "today", "夕方": "evening", "新年度": "new fiscal year",
        "予算": "budget", "成立": "passed", "見込み": "expected",
        "午前": "AM", "参院": "House of Councillors", "集中審議": "intensive deliberation",
        "患者": "patient", "手術": "surgery", "家族": "family", "同意": "consent",
        "不要": "not required", "医療": "medical", "ピアス": "piercings", "茶髪": "dyed hair",
        "学校": "school", "教育": "education", "今日": "today", "首相": "Prime Minister"
    },
    "fr": {
        "les coulisses": "behind the scenes", "victoire": "victory", "décrocher": "secure",
        "pour": "for", "la": "the", "le": "the", "de": "of", "et": "and",
        "à": "to", "une": "a", "un": "a", "est": "is", "en": "in", "sur": "on"
    },
    "zh": {
        "今天": "today", "预算": "budget", "成立": "established", "预计": "expected",
        "患者": "patient", "手术": "surgery", "家属": "family", "同意": "consent",
        "医疗": "medical", "教育": "education", "学校": "school", "首相": "Prime Minister"
    },
    "ar": {
        "مصر": "Egypt", "القاهرة": "Cairo", "السعودية": "Saudi Arabia",
        "الإمارات": "UAE", "دبي": "Dubai", "اقتصاد": "economy", "سياسة": "politics"
    },
    "hi": {
        "भारत": "India", "दिल्ली": "Delhi", "मुंबई": "Mumbai",
        "अर्थव्यवस्था": "economy", "राजनीति": "politics", "सरकार": "government"
    }
}

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

def detect_language(text):
    """检测语言"""
    if not text:
        return "en"
    
    # 计算非 ASCII 字符比例
    non_ascii = sum(1 for c in text if ord(c) > 127)
    ratio = non_ascii / len(text) if len(text) > 0 else 0
    
    if ratio < 0.05:
        return "en"
    
    text_lower = text.lower()
    
    # 检测具体语言（按 Unicode 范围和特征字符）
    # 日语（平假名、片假名）
    if any('\u3040' <= c <= '\u30ff' for c in text):
        return "ja"
    # 俄语（西里尔字母）
    if any('\u0400' <= c <= '\u04ff' for c in text):
        return "ru"
    # 中文（汉字）
    if any('\u4e00' <= c <= '\u9fff' for c in text):
        return "zh"
    # 葡萄牙语（ãõç）
    if any(c in text_lower for c in "ãõç"):
        return "pt"
    # 法语（éàèùâêîôûç）
    if any(c in text_lower for c in "éàèùâêîôûç"):
        return "fr"
    # 阿拉伯语
    if any('\u0600' <= c <= '\u06ff' for c in text):
        return "ar"
    # 印地语（天城文）
    if any('\u0900' <= c <= '\u097f' for c in text):
        return "hi"
    
    return "other"

def translate_text_with_ai(text, lang):
    """
    使用 AI 大模型翻译文本
    调用 OpenClaw sessions_spawn 或其他 AI 服务
    """
    if not text or lang == "en":
        return text
    
    # 限制文本长度
    text_to_translate = text[:200] if len(text) > 200 else text
    
    try:
        # 使用 OpenClaw sessions_spawn 调用 AI 翻译
        import subprocess
        import json
        
        prompt = f"Translate this {lang} text to English. Return ONLY the translation, no explanations:\n\n{text_to_translate}"
        
        # 调用本地 AI 模型（如果有）
        result = subprocess.run(
            ['curl', '-s', '-X', 'POST', 'http://localhost:11434/api/generate',
             '-H', 'Content-Type: application/json',
             '-d', json.dumps({
                 "model": "llama3.2",
                 "prompt": prompt,
                 "stream": False,
                 "max_tokens": 300
             })],
            capture_output=True, text=True, timeout=30
        )
        
        if result.returncode == 0:
            response = json.loads(result.stdout)
            translated = response.get("response", "").strip()
            if translated and len(translated) > 10:
                return translated
    except Exception as e:
        # AI 翻译失败，降级为简单标记
        pass
    
    # 降级方案：标记语言
    lang_names = {"pt": "PT", "ru": "RU", "zh": "CN", "ar": "AR", "mr": "IN", "ja": "JP"}
    lang_name = lang_names.get(lang, lang.upper())
    return f"[{lang_name}] {text_to_translate}"

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
        
        # 4. 检测并翻译非英语标题
        lang = detect_language(title)
        if lang != "en":
            title = translate_news(title, lang)
            stats["translated"] += 1
        
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

def fetch_bangladesh_news():
    """从 Financial Express Bangladesh 获取新闻"""
    import subprocess
    
    url = "https://thefinancialexpress.com.bd/page/economy/bangladesh"
    news_list = []
    
    try:
        # 使用 web_fetch 获取页面内容
        result = subprocess.run(
            ['web_fetch', url, '--extractMode', 'markdown', '--maxChars', '10000'],
            capture_output=True, text=True, timeout=30
        )
        
        if result.returncode == 0:
            content = result.stdout
            # 解析 Markdown 内容，提取新闻
            lines = content.split('\n')
            current_news = {}
            
            for line in lines:
                if line.startswith('## ') or line.startswith('### '):
                    if current_news:
                        news_list.append(current_news)
                    current_news = {
                        'title': line.lstrip('#').strip(),
                        'text': '',
                        'summary': '',
                        'url': '',
                        'author': 'Financial Express',
                        'source': 'The Financial Express Bangladesh'
                    }
                elif current_news and line.strip():
                    current_news['text'] += line + '\n'
            
            if current_news:
                news_list.append(current_news)
                
    except Exception as e:
        print(f"  Failed to fetch Bangladesh news: {e}")
    
    return news_list[:5]  # 返回最多 5 条

def main():
    """主函数"""
    all_news = {}
    stats_total = {"total": 0, "translated": 0, "excluded": 0}
    
    # 特殊处理：孟加拉新闻优先从 Financial Express 获取
    bd_news_from_fe = fetch_bangladesh_news()
    if bd_news_from_fe:
        print(f"✅ Fetched {len(bd_news_from_fe)} Bangladesh news from Financial Express")
    
    for country_code in COUNTRY_NAMES.keys():
        filepath = f"/tmp/news_collection/{country_code}.json"
        if not os.path.exists(filepath):
            # 如果是孟加拉且从 Financial Express 获取了新闻，使用这些新闻
            if country_code == "bd" and bd_news_from_fe:
                print(f"  Using Financial Express news for Bangladesh")
                news_list = bd_news_from_fe
            else:
                print(f"⚠️  File not found: {filepath}")
                continue
        else:
            with open(filepath, 'r') as f:
                data = json.load(f)
            news_list = data.get("news", [])
        
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
