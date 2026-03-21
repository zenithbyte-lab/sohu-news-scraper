"""搜狐国际新闻采集器 - 导出模块 (每条新闻单独TXT, 只含正文)"""

import os
from datetime import datetime
from models import NewsItem
from scraper import fetch_article_text


def export_to_folder(news_list: list[NewsItem], folder: str, progress_cb=None):
    """导出: 每条新闻抓取正文, 写为单独TXT"""
    os.makedirs(folder, exist_ok=True)
    total = len(news_list)

    # 索引文件
    idx_path = os.path.join(folder, "_索引.txt")
    with open(idx_path, "w", encoding="utf-8") as idx:
        idx.write(f"搜狐国际新闻 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        idx.write(f"共 {total} 条\n\n")
        for i, item in enumerate(news_list, 1):
            tag = "[新]" if item.is_new else "[旧]"
            idx.write(f"{i}. {tag} {item.title}\n")

    # 逐条抓正文并保存
    for i, item in enumerate(news_list, 1):
        if progress_cb:
            progress_cb(f"正在抓取正文 ({i}/{total}): {item.title[:20]}...")
        text = fetch_article_text(item.url)
        if not text:
            text = item.summary  # 兜底用摘要
        filepath = os.path.join(folder, f"{item.safe_filename}.txt")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(text + "\n")

    return total
