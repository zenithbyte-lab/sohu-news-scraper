"""搜狐国际新闻采集器 - 数据模型"""

import re
from typing import Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta


@dataclass
class NewsItem:
    """新闻条目"""
    title: str = ""
    url: str = ""
    source: str = ""
    publish_time: str = ""     # "30分钟前", "昨天23:57", "03-20 14:00"
    read_count: int = 0
    has_read_count: bool = False
    summary: str = ""
    cover_url: str = ""
    article_id: int = 0
    is_new: bool = True        # 是否为本次新采集的

    def to_dict(self) -> dict:
        return asdict(self)

    @property
    def full_url(self) -> str:
        if self.url.startswith("http"):
            return self.url
        return f"https://www.sohu.com{self.url}"

    @property
    def safe_filename(self) -> str:
        """生成安全的文件名"""
        name = re.sub(r'[\\/:*?"<>|]', '_', self.title)
        return name[:80].strip() or str(self.article_id)

    def estimate_datetime(self) -> Optional[datetime]:
        """尝试将相对时间解析为绝对datetime"""
        t = self.publish_time
        if not t:
            return None
        now = datetime.now()
        if "刚刚" in t:
            return now
        m = re.search(r"(\d+)分钟前", t)
        if m:
            return now - timedelta(minutes=int(m.group(1)))
        m = re.search(r"(\d+)小时前", t)
        if m:
            return now - timedelta(hours=int(m.group(1)))
        m = re.search(r"昨天\s*(\d{1,2}):(\d{2})", t)
        if m:
            d = now - timedelta(days=1)
            return d.replace(hour=int(m.group(1)), minute=int(m.group(2)))
        m = re.search(r"前天\s*(\d{1,2}):(\d{2})", t)
        if m:
            d = now - timedelta(days=2)
            return d.replace(hour=int(m.group(1)), minute=int(m.group(2)))
        m = re.search(r"(\d{1,2})-(\d{1,2})\s+(\d{1,2}):(\d{2})", t)
        if m:
            return now.replace(
                month=int(m.group(1)), day=int(m.group(2)),
                hour=int(m.group(3)), minute=int(m.group(4))
            )
        return None


@dataclass
class ScrapeResult:
    """爬取结果"""
    news_list: list = field(default_factory=list)
    scrape_time: str = ""
    total_count: int = 0
    new_count: int = 0
    success: bool = False
    error_msg: str = ""

    def __post_init__(self):
        if not self.scrape_time:
            self.scrape_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def update_count(self):
        self.total_count = len(self.news_list)
        self.new_count = sum(1 for n in self.news_list if n.is_new)
