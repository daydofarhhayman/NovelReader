#!/usr/bin/env python3
import os, sys, re, json, zipfile, shutil, argparse
from pathlib import Path

def add_novel_from_zip(zip_filename, author="佚名", category="玄幻仙俠", description=""):
    root_dir = Path(__file__).parent.resolve()
    zip_path = root_dir / zip_filename if not Path(zip_filename).is_absolute() else Path(zip_filename)
    if not zip_path.exists():
        print(f"❌ 錯誤：找不到壓縮檔 {zip_path.name}")
        return

    book_title = zip_path.stem
    target_dir = root_dir / "novels" / book_title
    target_dir.mkdir(parents=True, exist_ok=True)

    print(f"📦 正在解壓 {zip_path.name} 至 novels/{book_title}...")
    with zipfile.ZipFile(zip_path, 'r') as zf:
        for m in zf.infolist():
            fn = Path(m.filename).name
            if fn.lower().endswith(".txt") and not fn.startswith("."):
                with zf.open(m) as src, open(target_dir / fn, "wb") as dst:
                    shutil.copyfileobj(src, dst)

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
            "order": order, "title": title, "filename": f.name,
            "url": f"novels/{book_title}/{f.name}", "wordCount": w
        })

    chapters.sort(key=lambda x: (x["order"], x["filename"]))
    for idx, chap in enumerate(chapters, 1):
        chap["id"] = idx

    import hashlib
    book_id = "book_" + hashlib.md5(book_title.encode('utf-8')).hexdigest()[:8]
    data = {
        "bookId": book_id, "title": book_title, "author": author,
        "totalChapters": len(chapters), "totalWords": total_words, "chapters": chapters
    }
    with open(target_dir / "chapters.json", "w", encoding="utf-8") as out:
        json.dump(data, out, ensure_ascii=False, indent=2)

    books_file = root_dir / "books.json"
    books = json.load(open(books_file, "r", encoding="utf-8")) if books_file.exists() else []
    existing = next((b for b in books if b.get("title") == book_title), None)
    entry = {
        "bookId": book_id, "title": book_title, "author": author,
        "description": description or f"《{book_title}》全本在線閱讀。",
        "totalChapters": len(chapters), "category": category, "status": "連載中",
        "indexUrl": f"./novels/{book_title}/chapters.json", "chaptersBase": f"./novels/{book_title}/"
    }
    if existing: existing.update(entry)
    else: books.append(entry)
    json.dump(books, open(books_file, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    zip_path.unlink()
    print(f"✅ 大功告成！已解壓、完成排版並登記入書架！")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("zipfile")
    p.add_argument("--author", default="佚名")
    p.add_argument("--category", default="玄幻仙俠")
    a = p.parse_args()
    add_novel_from_zip(a.zipfile, author=a.author, category=a.category)
