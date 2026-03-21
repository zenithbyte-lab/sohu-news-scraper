"""搜狐国际新闻采集器 - 导出模块 (每条新闻单独TXT)"""

import os
from datetime import datetime
from models import NewsItem


def export_to_folder(news_list: list[NewsItem], folder: str):
    """将每条新闻导出为单独的TXT文件到指定文件夹"""
    os.makedirs(folder, exist_ok=True)

    # 写一个索引文件
    index_path = os.path.join(folder, "_索引.txt")
    with open(index_path, "w", encoding="utf-8") as idx:
        idx.write("搜狐国际新闻采集结果\n")
        idx.write(f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        idx.write(f"共 {len(news_list)} 条新闻\n")
        idx.write("=" * 60 + "\n\n")
        for i, item in enumerate(news_list, 1):
            tag = "[新]" if item.is_new else "[旧]"
            idx.write(f"{i}. {tag} {item.title}\n")
            idx.write(f"   文件: {item.safe_filename}.txt\n\n")

    # 每条新闻单独一个文件
    for item in news_list:
        filename = f"{item.safe_filename}.txt"
        filepath = os.path.join(folder, filename)
        _write_single(item, filepath)

    return len(news_list)


def _write_single(item: NewsItem, filepath: str):
    """写单条新闻文件"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"标题: {item.title}\n")
        f.write(f"来源: {item.source}\n")
        f.write(f"时间: {item.publish_time}\n")
        f.write(f"链接: {item.full_url}\n")
        if item.has_read_count:
            f.write(f"阅读量: {item.read_count}\n")
        f.write(f"状态: {'新采集' if item.is_new else '已有'}\n")
        f.write("-" * 50 + "\n\n")
        f.write(item.summary + "\n")
