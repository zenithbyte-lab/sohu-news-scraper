"""搜狐国际新闻采集器 - 爬虫核心模块"""

import re
import time
import random
import requests
from models import NewsItem, ScrapeResult
from config import (
    SOHU_API_URL, HEADERS, PAGE_SIZE, MAX_PAGES,
    API_PRODUCT_ID, API_PRODUCT_TYPE,
    API_MAIN_PRODUCT_ID, API_CATEGORY_ID, API_AUTHOR_ID,
)


def _build_body(page: int, size: int = PAGE_SIZE) -> dict:
    """构建API请求体"""
    ts = int(time.time() * 1000)
    rid = f"{ts}_{random.randint(100000, 999999)}"
    return {
        "pvId": rid,
        "pageId": f"{rid}_page",
        "mainContent": {
            "productType": API_PRODUCT_TYPE,
            "productId": API_MAIN_PRODUCT_ID,
            "secureScore": "50",
            "categoryId": API_CATEGORY_ID,
            "adTags": "20000111",
            "authorId": API_AUTHOR_ID,
        },
        "resourceList": [{
            "tplCompKey": "TPLFeedMul_2_9_feedData",
            "isServerRender": False,
            "isSingleAd": False,
            "configSource": "mp",
            "content": {
                "productId": API_PRODUCT_ID,
                "productType": API_PRODUCT_TYPE,
                "size": size,
                "pro": "0,1",
                "feedType": "XTOPIC_SYNTHETICAL",
                "view": "feedMode",
                "innerTag": "channel",
                "spm": "smpc.channel_114.block3_77_O0F7zf_1_fd",
                "page": page,
                "requestId": rid,
            },
            "adInfo": {
                "posCode": 10076, "rule": 2, "turn": 5,
                "number": 1, "begin": 5, "mergeType": 0,
                "fixArray": None,
            },
            "context": {"mkey": ""},
        }],
    }


def _parse_item(raw: dict):
    """解析单条新闻"""
    if str(raw.get("resourceType")) == "3":
        return None  # 广告
    item = NewsItem()
    item.title = raw.get("title", "").strip()
    if not item.title:
        return None
    item.url = raw.get("url", "")
    item.summary = raw.get("brief", "").strip()
    item.article_id = raw.get("id", 0)
    covers = raw.get("cover", [])
    if covers:
        item.cover_url = covers[0]
    for info in raw.get("extraInfoList", []):
        text = info.get("text", "")
        image = info.get("image", "")
        # 阅读量: "1157阅读", "3426阅读"
        rm = re.search(r"(\d+)阅读", text)
        if rm:
            item.read_count = int(rm.group(1))
            item.has_read_count = True
        elif image == "time":
            item.publish_time = text
        elif text:
            item.source = text
    return item


def fetch_all(progress_cb=None) -> ScrapeResult:
    """全量采集, 自动翻页直到无更多数据"""
    result = ScrapeResult()
    seen_ids = set()
    try:
        for page in range(1, MAX_PAGES + 1):
            if progress_cb:
                progress_cb(f"正在采集第 {page} 页...")
            body = _build_body(page)
            resp = requests.post(
                SOHU_API_URL, json=body, headers=HEADERS, timeout=15
            )
            resp.raise_for_status()
            data = resp.json()
            if data.get("code") != 0:
                break
            feed = data.get("data", {}).get("TPLFeedMul_2_9_feedData", {})
            raw_list = feed.get("list", [])
            if not raw_list:
                break
            added = 0
            for raw in raw_list:
                item = _parse_item(raw)
                if item and item.article_id not in seen_ids:
                    seen_ids.add(item.article_id)
                    result.news_list.append(item)
                    added += 1
            if added == 0:
                break
            time.sleep(0.3)
        result.update_count()
        result.success = True
    except requests.RequestException as e:
        result.error_msg = f"网络请求失败: {e}"
    except Exception as e:
        result.error_msg = f"数据解析失败: {e}"
    return result
