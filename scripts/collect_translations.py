#!/usr/bin/env python3
"""
新闻翻译模块 - 收集需要翻译的文本，批量处理
"""

import json
import os

def collect_texts_to_translate(news_list):
    """收集所有需要翻译的文本"""
    texts_to_translate = []
    
    for i, item in enumerate(news_list):
        title = item.get("title", "")
        summary = item.get("summary", "")
        
        # 检测是否需要翻译（非 ASCII 字符比例）
        for field_name, field_text in [("title", title), ("summary", summary)]:
            if not field_text:
                continue
            
            non_ascii = sum(1 for c in field_text if ord(c) > 127)
            if (non_ascii / len(field_text)) > 0.1:
                texts_to_translate.append({
                    "index": i,
                    "field": field_name,
                    "text": field_text[:200],
                    "original": field_text
                })
    
    return texts_to_translate

def apply_translations(news_list, translations):
    """应用翻译结果到新闻列表"""
    for trans in translations:
        idx = trans["index"]
        field = trans["field"]
        translated = trans["translated"]
        
        if 0 <= idx < len(news_list):
            news_list[idx][field] = translated
    
    return news_list

def format_translation_request(texts_to_translate):
    """格式化翻译请求，便于 AI 处理"""
    prompt = """请翻译以下新闻标题和摘要为英语。保持简洁、准确。
格式要求：按顺序返回翻译结果，每条一行。

"""
    for i, item in enumerate(texts_to_translate, 1):
        prompt += f"{i}. [{item['field']}] {item['text']}\n"
    
    prompt += "\n请直接返回翻译结果，不要解释："
    return prompt

if __name__ == "__main__":
    # 测试
    test_news = [
        {"title": "Project Maven': como os EUA usam IA como tecnologia de guerra", "summary": None},
        {"title": "Евросоюз начал готовиться к кризису и экономии", "summary": "Аналитики отмечают заметный сдвиг"},
        {"title": "إسرائيل تحتجز 4 من جنودها بتهمة التجسس", "summary": None},
    ]
    
    texts = collect_texts_to_translate(test_news)
    print(f"需要翻译的文本：{len(texts)} 条\n")
    
    for item in texts:
        print(f"{item['index']}. [{item['field']}] {item['text']}")
    
    print("\n=== 翻译请求格式 ===")
    print(format_translation_request(texts))
