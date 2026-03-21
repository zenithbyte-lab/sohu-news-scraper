"""搜狐国际新闻采集器 - 已读历史管理 (持久化)"""

import os
import json
from datetime import datetime

# 历史记录文件路径 (和程序同目录)
HISTORY_FILE = os.path.join(os.path.dirname(__file__), ".news_history.json")


def load_seen_ids() -> set:
    """加载已读文章ID集合"""
    if not os.path.exists(HISTORY_FILE):
        return set()
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return set(data.get("seen_ids", []))
    except (json.JSONDecodeError, IOError):
        return set()


def save_seen_ids(ids: set):
    """保存已读文章ID集合"""
    data = {
        "seen_ids": list(ids),
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "count": len(ids),
    }
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)


def mark_all_seen(article_ids: list) -> set:
    """将一批文章ID标记为已读, 返回更新后的集合"""
    seen = load_seen_ids()
    seen.update(article_ids)
    save_seen_ids(seen)
    return seen


def clear_history():
    """清空历史记录"""
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)


def get_history_info() -> dict:
    """获取历史记录统计"""
    seen = load_seen_ids()
    mtime = ""
    if os.path.exists(HISTORY_FILE):
        ts = os.path.getmtime(HISTORY_FILE)
        mtime = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    return {"count": len(seen), "last_update": mtime}
