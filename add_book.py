#!/usr/bin/env python3
"""
NovelReader 一鍵自動新增小說腳本 (add_book.py)
用法：
  python add_book.py 小說名稱.zip [--author 作者名] [--category 分類] [--desc 簡介] [--cover 封面圖片檔名或URL] [--delete-zip]
"""
import os
import sys
import re
import json
import zipfile
import shutil
import argparse
from datetime import datetime
from pathlib import Path

IMAGE_EXTS = ['.jpg', '.jpeg', '.png', '.webp', '.avif']

def add_novel_from_zip(zip_filename, author="佚名", category="玄幻仙俠", description="", custom_cover="", delete_zip=False):
    root_dir = Path(__file__).parent.resolve()
    zip_path = root_dir / zip_filename if not Path(zip_filename).is_absolute() else Path(zip_filename)
    if not zip_path.exists():
        print(f"❌ 錯誤：找不到壓縮檔 {zip_path.name}")
        return

    book_title = zip_path.stem
    target_dir = root_dir / "novels" / book_title
    target_dir.mkdir(parents=True, exist_ok=True)

    print(f"📦 正在解壓 {zip_path.name} 至 novels/{book_title}...")
    found_cover = None

    with zipfile.ZipFile(zip_path, 'r') as zf:
        for m in zf.infolist():
            fn = Path(m.filename).name
            if not fn or fn.startswith("."):
                continue
            # 提取純文字 txt
            if fn.lower().endswith(".txt"):
                with zf.open(m) as src, open(target_dir / fn, "wb") as dst:
                    shutil.copyfileobj(src, dst)
            # 提取封面圖片 (jpg, png, webp 等)
            elif any(fn.lower().endswith(ext) for ext in IMAGE_EXTS):
                with zf.open(m) as src, open(target_dir / fn, "wb") as dst:
                    shutil.copyfileobj(src, dst)
                if not found_cover or "cover" in fn.lower():
                    found_cover = fn

    txt_files = list(target_dir.glob("*.txt"))
    if not txt_files:
        print("⚠️ 警告：壓縮檔內未找到任何 .txt 檔案！")
        return

    print(f"📚 成功解壓 {len(txt_files)} 個章節，正在生成目錄索引...")
    chapters = []
    total_words = 0
    for f in txt_files:
        m = re.match(r"^(\d+)", f.stem)
        order = int(m.group(1)) if m else 999999
        title = re.sub(r"^\d+(_\d+)?[\._\s]*", "", f.stem).strip() or f.stem
        try:
            with open(f, "r", encoding="utf-8", errors="ignore") as fp:
                w = len(re.sub(r"\s+", "", fp.read()))
        except:
            w = 0
        total_words += w
        chapters.append({
            "order": order,
            "title": title,
            "filename": f.name,
            "url": f"novels/{book_title}/{f.name}",
            "wordCount": w
        })

    chapters.sort(key=lambda x: (x["order"], x["filename"]))
    for idx, chap in enumerate(chapters, 1):
        chap["id"] = idx

    import hashlib
    book_id = "book_" + hashlib.md5(book_title.encode('utf-8')).hexdigest()[:8]
    data = {
        "bookId": book_id,
        "title": book_title,
        "author": author,
        "totalChapters": len(chapters),
        "totalWords": total_words,
        "updatedAt": datetime.now().strftime("%Y-%m-%d"),
        "chapters": chapters
    }

    chapters_json_path = target_dir / "chapters.json"
    with open(chapters_json_path, "w", encoding="utf-8") as out:
        json.dump(data, out, ensure_ascii=False, indent=2)
    print(f"✅ 已產生章節目錄：novels/{book_title}/chapters.json (共 {len(chapters)} 章)")

    # 封面路徑解析
    final_cover = ""
    if custom_cover:
        final_cover = custom_cover
    elif found_cover:
        final_cover = f"./novels/{book_title}/{found_cover}"
    else:
        # 檢查該目錄下是否已存在圖片
        for ext in IMAGE_EXTS:
            c_candidate = target_dir / f"cover{ext}"
            if c_candidate.exists():
                final_cover = f"./novels/{book_title}/cover{ext}"
                break

    # 更新 books.json
    books_file = root_dir / "books.json"
    books = json.load(open(books_file, "r", encoding="utf-8")) if books_file.exists() else []
    existing = next((b for b in books if b.get("title") == book_title), None)
    entry = {
        "bookId": book_id,
        "title": book_title,
        "author": author,
        "cover": final_cover,
        "description": description or f"《{book_title}》全本在線閱讀。",
        "totalChapters": len(chapters),
        "category": category,
        "status": "連載中",
        "indexUrl": f"./novels/{book_title}/chapters.json",
        "chaptersBase": f"./novels/{book_title}/"
    }

    if existing:
        existing.update(entry)
        print(f"🔄 已更新 books.json 中的《{book_title}》！")
    else:
        books.append(entry)
        print(f"📖 已將《{book_title}》登記入 books.json 書庫清單！")

    with open(books_file, "w", encoding="utf-8") as f:
        json.dump(books, f, ensure_ascii=False, indent=2)

    if delete_zip:
        zip_path.unlink()
        print(f"🗑️ 已依指令清理壓縮檔 {zip_path.name}")
    else:
        print(f"💾 已保留原始壓縮檔：{zip_path.name}（如需自動清理請加上 --delete-zip 參數）")

    print(f"🎉 全部完成！封面狀態: {'已設定 (' + final_cover + ')' if final_cover else '無 (自動使用質感文字封面)'}")

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="一鍵解壓並新增小說")
    p.add_argument("zipfile", help="放在同層級的小說壓縮檔檔名 (例如 雪中悍刀行.zip)")
    p.add_argument("--author", default="佚名", help="小說作者 (預設: 佚名)")
    p.add_argument("--category", default="玄幻仙俠", help="小說分類 (預設: 玄幻仙俠)")
    p.add_argument("--desc", default="", help="小說簡介 (選填)")
    p.add_argument("--cover", default="", help="封面圖片路徑或線上網址 (選填)")
    p.add_argument("--delete-zip", action="store_true", default=False, help="解壓完成後自動刪除來源 .zip 壓縮檔 (預設保留)")

    a = p.parse_args()
    add_novel_from_zip(a.zipfile, author=a.author, category=a.category, description=a.desc, custom_cover=a.cover, delete_zip=a.delete_zip)
