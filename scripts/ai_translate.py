#!/usr/bin/env python3
"""
AI 翻译服务 - 使用大模型翻译新闻标题和摘要
支持多种翻译后端：Ollama、OpenAI、DeepL
"""

import json
import os
import subprocess

# 翻译字典（后备方案）
TRANSLATION_DICT = {
    "pt": {
        "como": "how", "os EUA": "the US", "usam": "use", "guerra": "war",
        "governo": "government", "impostos": "taxes", "combustível": "fuel",
        "aviação": "aviation", "Quem": "Who", "saiu": "left", "é": "is",
        "do": "of", "da": "of", "para": "for", "reclama": "complains",
        "futebol": "football", "mulher": "woman", "homem": "man",
        "anos": "years", "surpreende": "surprises", "própria": "own",
        "filha": "daughter", "Vítima": "Victim", "luta": "fights",
        "conscientizar": "raise awareness", "mulheres": "women"
    },
    "ru": {
        "Евросоюз": "EU", "начал": "began", "готовиться": "prepare",
        "кризису": "crisis", "экономии": "austerity", "Аналитики": "Analysts",
        "назвали": "named", "самый": "most", "востребованный": "in-demand",
        "ценовой": "price", "сегмент": "segment", "новых": "new", "авто": "cars",
        "ВТБ": "VTB Bank", "четверть": "quarter", "дальневосточников": "Far Easterners",
        "ближайшие": "next", "будут": "will", "копить": "save", "депозит": "deposit"
    },
    "ar": {
        "إسرائيل": "Israel", "تحتجز": "detains", "جنودها": "its soldiers",
        "بتهمة": "on charges of", "التجسس": "espionage", "لصالح": "for",
        "إيران": "Iran", "الجيش": "army", "يعلن": "announces", "موجة": "wave",
        "الضربات": "strikes", "الجوية": "airstrikes", "العراق": "Iraq",
        "مقتل": "killing", "رجل": "man", "امرأة": "woman", "سقوط": "fall of",
        "مسيرة": "drone", "على": "on", "منزلهما": "their home"
    },
    "zh": {
        "中国": "China", "成为": "becomes", "世界": "world", "Token": "Token",
        "工厂": "factory", "如何": "how", "为": "for", "加速": "accelerate",
        "变革": "transformation", "中": "in", "汽车业": "auto industry",
        "赋能": "empower", "日本": "Japan", "确认": "confirms", "释放": "release",
        "公民": "citizen", "被": "was", "拘留": "detained", "伊朗": "Iran"
    }
}

def translate_with_ollama(text, source_lang="auto"):
    """使用 Ollama 本地模型翻译"""
    try:
        prompt = f"Translate this {source_lang} text to English. Return ONLY the translation:\n\n{text[:200]}"
        
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
    except:
        pass
    return None

def translate_with_openai(text, source_lang="auto"):
    """使用 OpenAI API 翻译"""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None
    
    try:
        prompt = f"Translate this {source_lang} text to English. Return ONLY the translation:\n\n{text[:200]}"
        
        result = subprocess.run(
            ['curl', '-s', '-X', 'POST', 'https://api.openai.com/v1/chat/completions',
             '-H', f'Authorization: Bearer {api_key}',
             '-H', 'Content-Type: application/json',
             '-d', json.dumps({
                 "model": "gpt-3.5-turbo",
                 "messages": [{"role": "user", "content": prompt}],
                 "max_tokens": 300
             })],
            capture_output=True, text=True, timeout=30
        )
        
        if result.returncode == 0:
            response = json.loads(result.stdout)
            translated = response.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            if translated and len(translated) > 10:
                return translated
    except:
        pass
    return None

def translate_with_dict(text, source_lang):
    """使用翻译字典（后备方案）"""
    if not text or source_lang == "en":
        return text
    
    translated = text
    trans_dict = TRANSLATION_DICT.get(source_lang, {})
    
    # 按长度排序，先翻译长词组
    for original, translation in sorted(trans_dict.items(), key=lambda x: len(x[0]), reverse=True):
        translated = translated.replace(original, translation)
    
    return translated

def translate_news(text, source_lang="auto"):
    """
    翻译新闻标题/摘要
    优先级：Ollama > OpenAI > 翻译字典
    """
    if not text or source_lang == "en":
        return text
    
    # 1. 尝试 Ollama
    translated = translate_with_ollama(text, source_lang)
    if translated:
        return translated
    
    # 2. 尝试 OpenAI
    translated = translate_with_openai(text, source_lang)
    if translated:
        return translated
    
    # 3. 使用翻译字典
    translated = translate_with_dict(text, source_lang)
    
    # 4. 如果翻译后没变化，添加语言标记
    if translated == text:
        lang_names = {"pt": "PT", "ru": "RU", "zh": "CN", "ar": "AR", "mr": "IN", "ja": "JP"}
        lang_name = lang_names.get(source_lang, source_lang.upper())
        return f"[{lang_name}] {text[:100]}"
    
    return translated

if __name__ == "__main__":
    # 测试
    test_cases = [
        ("Project Maven': como os EUA usam IA como tecnologia de guerra", "pt"),
        ("Евросоюз начал готовиться к кризису и экономии", "ru"),
        ("إسرائيل تحتجز 4 من جنودها بتهمة التجسس لصالح إيران", "ar"),
    ]
    
    print("=== AI 翻译测试 ===\n")
    for text, lang in test_cases:
        translated = translate_news(text, lang)
        print(f"原文 ({lang}): {text}")
        print(f"翻译：{translated}\n")
