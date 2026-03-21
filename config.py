"""搜狐国际新闻采集器 - 配置文件"""

# 搜狐API端点
SOHU_API_URL = "https://odin.sohu.com/odin/api/blockdata"

# 国际新闻页面URL (referer用)
SOHU_PAGE_URL = (
    "https://www.sohu.com/xchannel/tag?"
    "key=%E6%96%B0%E9%97%BB-%E5%9B%BD%E9%99%85"
)

# 请求头
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Content-Type": "application/json;charset=UTF-8",
    "Origin": "https://www.sohu.com",
    "Referer": SOHU_PAGE_URL,
}

# API固定参数
API_PRODUCT_ID = "1649"
API_PRODUCT_TYPE = "13"
API_MAIN_PRODUCT_ID = "1524"
API_CATEGORY_ID = "47"
API_AUTHOR_ID = 121135924

# 每页大小 / 最大采集页数
PAGE_SIZE = 20
MAX_PAGES = 10

# 定时器间隔选项(秒)
TIMER_OPTIONS = {
    "1分钟": 60,
    "5分钟": 300,
    "10分钟": 600,
    "30分钟": 1800,
    "1小时": 3600,
}

# 应用信息
APP_NAME = "搜狐国际新闻采集器"
APP_VERSION = "2.0.0"
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 820
