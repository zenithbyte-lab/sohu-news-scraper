"""搜狐国际新闻采集器 - 主窗口"""

import webbrowser
from datetime import datetime
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QTableWidgetItem, QFileDialog, QMessageBox,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from config import APP_NAME, APP_VERSION, WINDOW_WIDTH, WINDOW_HEIGHT, TIMER_OPTIONS
from models import NewsItem, ScrapeResult
from worker import ScrapeWorker, TimerManager
from exporter import export_to_folder
from history import load_seen_ids, mark_all_seen, clear_history, get_history_info
from ui_widgets import (
    build_toolbar, build_new_banner, build_filter_bar,
    build_stats_bar, build_table, build_bottom_bar,
)

_NEW = (QColor("#e8f5e9"), QColor("#1b5e20"))
_OLD = (QColor("#ffffff"), QColor("#666666"))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self._all_news, self._filtered = [], []
        self._seen_ids = load_seen_ids()
        self._worker = None
        self._timer_mgr = TimerManager(self)
        self._timer_mgr.tick.connect(self._on_start_scrape)
        self._timer_mgr.countdown_update.connect(self._on_countdown)
        self._init_ui()
        self._update_history_label()

    def _init_ui(self):
        c = QWidget()
        self.setCentralWidget(c)
        lay = QVBoxLayout(c)
        lay.setSpacing(6)
        lay.setContentsMargins(12, 10, 12, 10)
        lay.addLayout(build_toolbar(self))
        lay.addLayout(build_new_banner(self))
        lay.addLayout(build_filter_bar(self))
        lay.addLayout(build_stats_bar(self))
        lay.addWidget(build_table(self), 1)
        lay.addLayout(build_bottom_bar(self))
        self.statusBar().showMessage("就绪 — 点击 [开始采集] 全量抓取国际新闻")

    # ---- 采集 ----
    def _on_start_scrape(self):
        if self._worker and self._worker.isRunning():
            return
        self.btn_scrape.setEnabled(False)
        self.btn_scrape.setText("采集中...")
        self.progress.setVisible(True)
        self._worker = ScrapeWorker()
        self._worker.progress.connect(lambda m: self.statusBar().showMessage(m))
        self._worker.finished.connect(self._on_scrape_done)
        self._worker.start()

    def _on_scrape_done(self, result: ScrapeResult):
        self.progress.setVisible(False)
        self.btn_scrape.setEnabled(True)
        self.btn_scrape.setText("  开始采集  ")
        if not result.success:
            QMessageBox.warning(self, "采集失败", result.error_msg)
            return

        # 用持久化的 _seen_ids 判断新旧
        for item in result.news_list:
            item.is_new = item.article_id not in self._seen_ids
        new_count = sum(1 for n in result.news_list if n.is_new)
        self._all_news = result.news_list
        self._all_news.sort(key=lambda n: (not n.is_new,))

        self._apply_filters()
        self.btn_export.setEnabled(bool(self._all_news))
        self.btn_mark_read.setEnabled(new_count > 0)

        # 醒目横幅
        self._show_banner(new_count, len(self._all_news))
        self.statusBar().showMessage(
            f"采集完成: 共{len(self._all_news)}条, 新增{new_count}条"
        )

    def _show_banner(self, new_c, total):
        base = "font-size:15px;font-weight:bold;padding:8px 16px;border-radius:5px;"
        if new_c > 0:
            self.lbl_banner.setText(f"  本次发现 {new_c} 条新增新闻！（共{total}条）")
            self.lbl_banner.setStyleSheet(base + "background:#e8f5e9;color:#2e7d32;border:1px solid #a5d6a7;")
        else:
            self.lbl_banner.setText("  暂无新增，全部已读")
            self.lbl_banner.setStyleSheet(base + "background:#fff3e0;color:#e65100;border:1px solid #ffcc80;")
        self.lbl_banner.setVisible(True)

    def _on_mark_all_read(self):
        ids = [n.article_id for n in self._all_news]
        self._seen_ids = mark_all_seen(ids)
        for n in self._all_news:
            n.is_new = False
        self.btn_mark_read.setEnabled(False)
        self.lbl_banner.setText("  已全部标记已读，下次采集将突出新内容")
        self.lbl_banner.setStyleSheet(
            "background:#e3f2fd;color:#1565c0;font-size:15px;font-weight:bold;"
            "padding:8px 16px;border-radius:5px;border:1px solid #90caf9;"
        )
        self._apply_filters()
        self._update_history_label()

    # ---- 筛选 ----
    def _apply_filters(self):
        d_from = self.date_from.date().toPyDate()
        d_to = self.date_to.date().toPyDate()
        filtered = []
        for item in self._all_news:
            dt = item.estimate_datetime()
            if dt and (dt.date() < d_from or dt.date() > d_to):
                continue
            if self.chk_read.isChecked() and not item.has_read_count:
                continue
            if self.chk_new.isChecked() and not item.is_new:
                continue
            filtered.append(item)
        self._filtered = filtered
        self._refresh_table()
        self._update_stats()

    def _refresh_table(self):
        news = self._filtered
        self.table.setRowCount(len(news))
        bold_font = QFont(); bold_font.setBold(True)
        for r, item in enumerate(news):
            bg, fg = _NEW if item.is_new else _OLD
            rc = str(item.read_count) if item.has_read_count else ""
            row_data = ["新" if item.is_new else "—",
                        item.title, item.source, item.publish_time,
                        rc, item.summary[:100]]
            for c, val in enumerate(row_data):
                cell = QTableWidgetItem(val)
                cell.setBackground(bg)
                cell.setForeground(fg)
                if c == 0:
                    cell.setTextAlignment(Qt.AlignCenter)
                if item.is_new and c <= 1:
                    cell.setFont(bold_font)
                self.table.setItem(r, c, cell)

    def _update_stats(self):
        a = self._all_news
        new_c = sum(1 for n in a if n.is_new)
        self.lbl_total.setText(f"总计: {len(a)}")
        self.lbl_new.setText(f"新增: {new_c}")
        self.lbl_old.setText(f"已读: {len(a) - new_c}")
        self.lbl_read_count.setText(f"有阅读量: {sum(1 for n in a if n.has_read_count)}")
        self.lbl_showing.setText(f"显示: {len(self._filtered)}")

    def _update_history_label(self):
        self.lbl_history.setText(f"历史已读: {get_history_info()['count']}条")

    def _on_cell_dblclick(self, row, _col):
        if row < len(self._filtered):
            webbrowser.open(self._filtered[row].full_url)

    def _on_toggle_timer(self, checked):
        if checked:
            key = self.cmb_timer.currentText()
            self._timer_mgr.start(TIMER_OPTIONS[key])
            self.btn_timer.setText("停止")
        else:
            self._timer_mgr.stop()
            self.btn_timer.setText("启动")
            self.lbl_countdown.setText("")

    def _on_countdown(self, sec):
        self.lbl_countdown.setText(f"{sec//60:02d}:{sec%60:02d}")

    def _on_clear_history(self):
        if QMessageBox.question(
            self, "确认", "清空后下次采集全部显示为新增，确定？"
        ) == QMessageBox.Yes:
            clear_history()
            self._seen_ids = set()
            self._update_history_label()

    def _on_export(self):
        if not self._filtered:
            return QMessageBox.information(self, "提示", "没有可导出的数据")
        folder = QFileDialog.getExistingDirectory(self, "选择导出位置")
        if not folder:
            return
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        sub = f"{folder}/搜狐国际新闻_{ts}"
        count = export_to_folder(self._filtered, sub)
        QMessageBox.information(self, "导出成功",
            f"已导出 {count} 条到:\n{sub}")
