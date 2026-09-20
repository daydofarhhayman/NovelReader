#!/usr/bin/env python3
import os, re, json
from pathlib import Path

novel_dir = Path("./novels/劍來")
txt_files = list(novel_dir.glob("*.txt"))
print(f"正在掃描 {len(txt_files)} 個章節檔案...")

chapters = []
total_words = 0

for f in txt_files:
    m = re.match(r"^(\d+)", f.stem)
    order = int(m.group(1)) if m else 999999
    title = re.sub(r"^\d+(_\d+)?[\._\s]*", "", f.stem).strip() or f.stem
    try:
        with open(f, "r", encoding="utf-8", errors="ignore") as fp:
            words = len(re.sub(r"\s+", "", fp.read()))
    except:
        words = 0
    total_words += words
    chapters.append({
        "order": order,
        "title": title,
        "filename": f.name,
        "url": f"novels/劍來/{f.name}",
        "wordCount": words
    })

chapters.sort(key=lambda x: (x["order"], x["filename"]))
for idx, chap in enumerate(chapters, 1):
    chap["id"] = idx

data = {
    "bookId": "jianlai",
    "title": "劍來",
    "author": "烽火戲諸侯",
    "totalChapters": len(chapters),
    "totalWords": total_words,
    "updatedAt": "2026-09-20",
    "chapters": chapters
}

with open("./novels/劍來/chapters.json", "w", encoding="utf-8") as out:
    json.dump(data, out, ensure_ascii=False, indent=2)

print(f"✅ 成功！已在 novels/劍來/chapters.json 產生 {len(chapters)} 章完整目錄！")
