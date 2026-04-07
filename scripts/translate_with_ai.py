#!/usr/bin/env python3
"""
使用 AI 大模型翻译新闻
流程：
1. 收集所有需要翻译的文本
2. 输出翻译请求（由 AI 处理）
3. 应用翻译结果
"""

import json
import os
import sys
from datetime import datetime

def detect_language(text):
    """检测语言"""
    if not text:
        return "en"
    non_ascii = sum(1 for c in text if ord(c) > 127)
    if (non_ascii / len(text)) < 0.05:
        return "en"
    if any('\u0400' <= c <= '\u04ff' for c in text):
        return "ru"
    if any('\u4e00' <= c <= '\u9fff' for c in text):
        return "zh"
    if any('\u0600' <= c <= '\u06ff' for c in text):
        return "ar"
    if any(c in text.lower() for c in "ãõç"):
        return "pt"
    if any('\u3040' <= c <= '\u30ff' for c in text):
        return "ja"
    return "other"

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 translate_with_ai.py <country_code>")
        sys.exit(1)
    
    country_code = sys.argv[1]
    filepath = f"/tmp/news_collection/{country_code}.json"
    
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        sys.exit(1)
    
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    news_list = data.get("news", [])
    
    # 收集需要翻译的文本
    texts_to_translate = []
    for i, item in enumerate(news_list[:5]):  # 最多处理前 5 条
        title = item.get("title", "")
        summary = item.get("summary", "")
        
        # 检测标题语言
        title_lang = detect_language(title)
        if title_lang != "en":
            texts_to_translate.append({
                "index": i,
                "field": "title",
                "text": title[:150],
                "lang": title_lang
            })
        
        # 检测摘要语言
        if summary:
            summary_lang = detect_language(summary)
            if summary_lang != "en":
                texts_to_translate.append({
                    "index": i,
                    "field": "summary",
                    "text": summary[:150],
                    "lang": summary_lang
                })
    
    if not texts_to_translate:
        print("✅ 无需翻译（全是英语）")
        sys.exit(0)
    
    # 输出翻译请求
    print(f"\n=== 需要翻译的文本：{len(texts_to_translate)} 条 ===\n")
    print("请翻译以下新闻标题和摘要为英语。保持简洁、准确。")
    print("格式要求：按顺序返回翻译结果，每条一行，不要解释。\n")
    
    for i, item in enumerate(texts_to_translate, 1):
        print(f"{i}. [{item['lang'].upper()}] {item['text']}")
    
    print("\n--- 翻译结果 ---")
    print("（等待 AI 返回翻译结果...）\n")

if __name__ == "__main__":
    main()
