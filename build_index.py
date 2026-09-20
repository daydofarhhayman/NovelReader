#!/usr/bin/env python3
"""
NovelReader 目錄與索引產生腳本 (build_index.py)
用途：遍歷小說資料夾（內含章節 txt 檔案），自動解析章節序號、標題與字數，
      輸出適用於方案 A 的 chapters.json 靜態索引檔。
"""

import os
import re
import json
import glob
from pathlib import Path

def extract_chapter_info(filename):
    """
    從檔名解析章節編號與章節標題
    支援格式範例：
    - 262_262.第262章 有劍從雲海來.txt
    - 1400_第56章 利劍在掌心.txt
    - 第1章 驚蟄.txt
    - 001.txt
    """
    name = Path(filename).stem
    
    # 嘗試比對前綴序號（例如 262_262 或 1400_）
    order = 999999
    match_order = re.match(r"^(\d+)", name)
    if match_order:
        order = int(match_order.group(1))
    
    # 清理標題文字
    # 移除開頭的數字與底線 (e.g. '262_262.' -> '')
    cleaned_title = re.sub(r"^\d+(_\d+)?[\._\s]*", "", name).strip()
    if not cleaned_title:
        cleaned_title = name

    return order, cleaned_title

def generate_index(novel_dir, output_json, book_id="jianlai", book_title="劍來", author="烽火戲諸侯"):
    novel_path = Path(novel_dir)
    if not novel_path.exists():
        print(f"錯誤：資料夾不存在：{novel_dir}")
        return

    txt_files = list(novel_path.glob("*.txt"))
    if not txt_files:
        print(f"警告：在 {novel_dir} 中找不到任何 .txt 檔案")
        return

    print(f"正在掃描 {len(txt_files)} 個章節檔案...")
    
    chapters = []
    total_words = 0

    for file_path in txt_files:
        order, title = extract_chapter_info(file_path.name)
        
        # 計算字數
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                # 去除空白字元後的純文字字數
                word_count = len(re.sub(r"\s+", "", content))
        except Exception as e:
            word_count = 0

        total_words += word_count
        
        chapters.append({
            "order": order,
            "title": title,
            "filename": file_path.name,
            # 前端可直接存取的相對路徑或 CDN URL
            "url": f"chapters/{file_path.name}",
            "wordCount": word_count
        })

    # 按照序號排序
    chapters.sort(key=lambda x: (x["order"], x["filename"]))

    # 給定標準的 1-based index id
    for idx, chap in enumerate(chapters, 1):
        chap["id"] = idx

    index_data = {
        "bookId": book_id,
        "title": book_title,
        "author": author,
        "totalChapters": len(chapters),
        "totalWords": total_words,
        "updatedAt": "2026-09-20",
        "chapters": chapters
    }

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)

    print(f"✅ 成功生成目錄索引：{output_json}")
    print(f"📚 總章節數：{len(chapters)} 章 | 總字數約：{total_words:,} 字")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="產生小說靜態索引 chapters.json")
    parser.add_argument("--dir", default="./Novel/劍來", help="小說章節 .txt 存放資料夾路徑")
    parser.add_argument("--output", default="./chapters.json", help="輸出的 json 路徑")
    parser.add_argument("--title", default="劍來", help="小說書名")
    parser.add_argument("--author", default="烽火戲諸侯", help="小說作者")
    
    args = parser.parse_args()
    generate_index(args.dir, args.output, book_title=args.title, author=args.author)
