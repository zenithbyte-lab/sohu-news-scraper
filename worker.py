"""搜狐国际新闻采集器 - 后台工作线程"""

from PyQt5.QtCore import QThread, pyqtSignal, QTimer, QObject
from models import ScrapeResult, NewsItem
from scraper import fetch_all
from exporter import export_to_folder


class ScrapeWorker(QThread):
    """爬取工作线程"""
    finished = pyqtSignal(ScrapeResult)
    progress = pyqtSignal(str)

    def run(self):
        self.progress.emit("正在采集国际新闻...")
        result = fetch_all(progress_cb=lambda msg: self.progress.emit(msg))
        self.finished.emit(result)


class ExportWorker(QThread):
    """导出工作线程 (逐条抓正文, 较耗时)"""
    finished = pyqtSignal(int, str)  # (导出数量, 文件夹路径)
    progress = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, news_list: list, folder: str, parent=None):
        super().__init__(parent)
        self._news_list = news_list
        self._folder = folder

    def run(self):
        try:
            count = export_to_folder(
                self._news_list, self._folder,
                progress_cb=lambda m: self.progress.emit(m)
            )
            self.finished.emit(count, self._folder)
        except Exception as e:
            self.error.emit(str(e))


class TimerManager(QObject):
    """定时采集管理器"""
    tick = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.tick.emit)
        self._running = False
        self._remaining = 0
        self._interval = 0
        self._countdown = QTimer(self)
        self._countdown.setInterval(1000)
        self._countdown.timeout.connect(self._tick_down)

    countdown_update = pyqtSignal(int)  # 剩余秒数

    @property
    def is_running(self) -> bool:
        return self._running

    def start(self, interval_sec: int):
        self._interval = interval_sec
        self._remaining = interval_sec
        self._timer.start(interval_sec * 1000)
        self._countdown.start()
        self._running = True

    def stop(self):
        self._timer.stop()
        self._countdown.stop()
        self._running = False
        self._remaining = 0

    def _tick_down(self):
        self._remaining -= 1
        if self._remaining < 0:
            self._remaining = self._interval
        self.countdown_update.emit(self._remaining)
