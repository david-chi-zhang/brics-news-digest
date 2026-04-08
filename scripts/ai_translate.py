#!/usr/bin/env python3
"""
AI 翻译服务 - 使用当前对话的大模型能力翻译
无需外部 API，直接使用 OpenClaw 内置的 AI 能力
"""

import json
import os

def translate_with_ai(text, source_lang="auto"):
    """
    使用当前对话的大模型能力翻译文本
    
    这是最优先的翻译方式：
    - 无需外部 API（Ollama/OpenAI）
    - 直接使用 OpenClaw 内置的 AI 能力
    - 支持所有语言
    - 高质量翻译
    
    参数:
        text: 待翻译的文本
        source_lang: 源语言代码 (pt/ru/ar/zh/ja/fr/hi 等)
    
    返回:
        翻译后的英语文本，或原文（如果翻译失败）
    """
    if not text or source_lang == "en":
        return text
    
    # 限制文本长度
    text_to_translate = text[:200] if len(text) > 200 else text
    
    # 构建翻译提示
    prompt = f"""Please translate the following {source_lang} text to English. 
Return ONLY the translation, no explanations or additional text.

Text to translate:
{text_to_translate}

English translation:"""
    
    # 注意：实际调用由主流程处理，通过 OpenClaw 的 AI 能力
    # 这里返回 prompt，由主流程调用 AI
    return prompt

def collect_texts_for_translation(news_list):
    """
    收集所有需要翻译的文本
    
    参数:
        news_list: 新闻列表
    
    返回:
        需要翻译的文本列表，格式：
        [
            {"index": 0, "field": "title", "text": "...", "lang": "ru"},
            {"index": 0, "field": "summary", "text": "...", "lang": "ru"},
            ...
        ]
    """
    texts_to_translate = []
    
    for i, item in enumerate(news_list):
        title = item.get("title", "")
        summary = item.get("summary", "")
        
        # 检测标题语言
        title_lang = detect_language(title)
        if title_lang != "en":
            texts_to_translate.append({
                "index": i,
                "field": "title",
                "text": title[:200],
                "lang": title_lang
            })
        
        # 检测摘要语言
        if summary:
            summary_lang = detect_language(summary)
            if summary_lang != "en":
                texts_to_translate.append({
                    "index": i,
                    "field": "summary",
                    "text": summary[:200],
                    "lang": summary_lang
                })
    
    return texts_to_translate

def detect_language(text):
    """
    检测文本语言
    
    支持的语言:
    - en: 英语 (ASCII >95%)
    - ja: 日语 (平假名/片假名)
    - ru: 俄语 (西里尔字母)
    - zh: 中文 (汉字)
    - pt: 葡萄牙语 (ãõç)
    - fr: 法语 (éàèùâêîôûç)
    - ar: 阿拉伯语 (阿拉伯字母)
    - hi: 印地语 (天城文)
    - other: 其他语言
    """
    if not text:
        return "en"
    
    # 计算非 ASCII 字符比例
    non_ascii = sum(1 for c in text if ord(c) > 127)
    ratio = non_ascii / len(text) if len(text) > 0 else 0
    
    if ratio < 0.05:
        return "en"
    
    text_lower = text.lower()
    
    # 按 Unicode 范围和特征字符检测
    if any('\u3040' <= c <= '\u30ff' for c in text):
        return "ja"  # 日语
    if any('\u0400' <= c <= '\u04ff' for c in text):
        return "ru"  # 俄语
    if any('\u4e00' <= c <= '\u9fff' for c in text):
        return "zh"  # 中文
    if any(c in text_lower for c in "ãõç"):
        return "pt"  # 葡萄牙语
    if any(c in text_lower for c in "éàèùâêîôûç"):
        return "fr"  # 法语
    if any('\u0600' <= c <= '\u06ff' for c in text):
        return "ar"  # 阿拉伯语
    if any('\u0900' <= c <= '\u097f' for c in text):
        return "hi"  # 印地语
    
    return "other"

def apply_translations(news_list, translations):
    """
    应用翻译结果到新闻列表
    
    参数:
        news_list: 原始新闻列表
        translations: 翻译结果列表，格式：
            [
                {"index": 0, "field": "title", "translated": "..."},
                ...
            ]
    
    返回:
        更新后的新闻列表
    """
    for trans in translations:
        idx = trans.get("index")
        field = trans.get("field")
        translated = trans.get("translated")
        
        if idx is not None and field and translated:
            if 0 <= idx < len(news_list):
                news_list[idx][field] = translated
    
    return news_list

if __name__ == "__main__":
    # 测试语言检测
    test_cases = [
        ("One third of Russians do not trust telemedicine", "en"),
        ("Треть россиян не доверяют телемедицине", "ru"),
        ("إسرائيل تحتجز 4 من جنودها", "ar"),
        ("Governo zera impostos da aviação", "pt"),
        ("きょう予算が成立見込み", "ja"),
        ("中国成为世界 Token 工厂", "zh"),
        ("Le gouvernement français annonce", "fr"),
        ("भारत सरकार ने घोषणा की", "hi"),
    ]
    
    print("=== 语言检测测试 ===\n")
    for text, expected_lang in test_cases:
        detected = detect_language(text)
        status = "✅" if detected == expected_lang else "❌"
        print(f"{status} {expected_lang}: {text[:50]}... → 检测：{detected}")
    
    print("\n=== 翻译支持 ===")
    print("支持的语言:")
    print("- 英语 (en): ASCII >95%")
    print("- 日语 (ja): 平假名/片假名")
    print("- 俄语 (ru): 西里尔字母")
    print("- 中文 (zh): 汉字")
    print("- 葡萄牙语 (pt): 特征字符 ãõç")
    print("- 法语 (fr): 特征字符 éàèùâêîôûç")
    print("- 阿拉伯语 (ar): 阿拉伯字母")
    print("- 印地语 (hi): 天城文")
    print("- 其他 (other): 无法识别的语言")
    print("\n翻译方式：使用当前对话的大模型能力（无需外部 API）")
