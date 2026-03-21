"""搜狐国际新闻采集器 - UI组件构建"""

from PyQt5.QtWidgets import (
    QHBoxLayout, QPushButton, QLabel,
    QComboBox, QCheckBox, QTableWidget, QHeaderView,
    QGroupBox, QProgressBar, QDateEdit, QFrame,
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QDate
from config import TIMER_OPTIONS


def build_toolbar(win) -> QHBoxLayout:
    """顶部: 采集按钮 + 标记已读 + 定时器"""
    row = QHBoxLayout()

    win.btn_scrape = QPushButton("  开始采集  ")
    win.btn_scrape.setFixedHeight(42)
    win.btn_scrape.setStyleSheet(
        "QPushButton{background:#ff6600;color:#fff;font-size:15px;"
        "font-weight:bold;border-radius:5px;padding:0 28px;border:none}"
        "QPushButton:hover{background:#e55b00}"
        "QPushButton:disabled{background:#ccc}"
    )
    win.btn_scrape.clicked.connect(win._on_start_scrape)
    row.addWidget(win.btn_scrape)

    win.progress = QProgressBar()
    win.progress.setVisible(False)
    win.progress.setRange(0, 0)
    win.progress.setFixedWidth(140)
    row.addWidget(win.progress)

    row.addSpacing(10)

    # 标记已读按钮
    win.btn_mark_read = QPushButton("全部标记已读")
    win.btn_mark_read.setFixedHeight(36)
    win.btn_mark_read.setStyleSheet(
        "QPushButton{background:#43a047;color:#fff;font-size:13px;"
        "border-radius:4px;padding:0 16px;border:none}"
        "QPushButton:hover{background:#388e3c}"
        "QPushButton:disabled{background:#ccc}"
    )
    win.btn_mark_read.clicked.connect(win._on_mark_all_read)
    win.btn_mark_read.setEnabled(False)
    row.addWidget(win.btn_mark_read)

    row.addStretch()

    # 定时器
    grp = QGroupBox("定时采集")
    gl = QHBoxLayout(grp)
    gl.setContentsMargins(10, 4, 10, 4)
    win.cmb_timer = QComboBox()
    for k in TIMER_OPTIONS:
        win.cmb_timer.addItem(k)
    win.cmb_timer.setCurrentIndex(1)
    win.btn_timer = QPushButton("启动")
    win.btn_timer.setCheckable(True)
    win.btn_timer.clicked.connect(win._on_toggle_timer)
    win.lbl_countdown = QLabel("")
    win.lbl_countdown.setStyleSheet("color:#ff6600;font-weight:bold;")
    gl.addWidget(win.cmb_timer)
    gl.addWidget(win.btn_timer)
    gl.addWidget(win.lbl_countdown)
    row.addWidget(grp)
    return row


def build_new_banner(win) -> QHBoxLayout:
    """新增提示横幅"""
    row = QHBoxLayout()
    win.lbl_banner = QLabel("")
    win.lbl_banner.setStyleSheet(
        "background:#e8f5e9; color:#2e7d32; font-size:15px;"
        "font-weight:bold; padding:8px 16px; border-radius:5px;"
        "border:1px solid #a5d6a7;"
    )
    win.lbl_banner.setVisible(False)
    row.addWidget(win.lbl_banner)
    return row


def build_filter_bar(win) -> QHBoxLayout:
    """筛选栏"""
    row = QHBoxLayout()

    row.addWidget(QLabel("从"))
    win.date_from = QDateEdit()
    win.date_from.setCalendarPopup(True)
    win.date_from.setDate(QDate.currentDate().addDays(-30))
    win.date_from.setDisplayFormat("yyyy-MM-dd")
    win.date_from.dateChanged.connect(win._apply_filters)
    row.addWidget(win.date_from)

    row.addWidget(QLabel("到"))
    win.date_to = QDateEdit()
    win.date_to.setCalendarPopup(True)
    win.date_to.setDate(QDate.currentDate())
    win.date_to.setDisplayFormat("yyyy-MM-dd")
    win.date_to.dateChanged.connect(win._apply_filters)
    row.addWidget(win.date_to)

    sep = QFrame()
    sep.setFrameShape(QFrame.VLine)
    sep.setStyleSheet("color:#ccc;")
    row.addWidget(sep)

    win.chk_read = QCheckBox("仅有阅读量")
    win.chk_read.stateChanged.connect(win._apply_filters)
    row.addWidget(win.chk_read)

    win.chk_new = QCheckBox("仅看新增")
    win.chk_new.stateChanged.connect(win._apply_filters)
    row.addWidget(win.chk_new)

    row.addStretch()
    return row


def build_stats_bar(win) -> QHBoxLayout:
    """统计信息栏"""
    row = QHBoxLayout()
    s = "font-size:13px;padding:4px 12px;border-radius:3px;"

    win.lbl_total = QLabel("总计: 0")
    win.lbl_total.setStyleSheet(s + "background:#e3f2fd;color:#1565c0;")
    row.addWidget(win.lbl_total)

    win.lbl_new = QLabel("新增: 0")
    win.lbl_new.setStyleSheet(s + "background:#e8f5e9;color:#2e7d32;font-weight:bold;")
    row.addWidget(win.lbl_new)

    win.lbl_old = QLabel("已读: 0")
    win.lbl_old.setStyleSheet(s + "background:#fff3e0;color:#e65100;")
    row.addWidget(win.lbl_old)

    win.lbl_read_count = QLabel("有阅读量: 0")
    win.lbl_read_count.setStyleSheet(s + "background:#fce4ec;color:#c62828;")
    row.addWidget(win.lbl_read_count)

    win.lbl_showing = QLabel("显示: 0")
    win.lbl_showing.setStyleSheet(s + "background:#f3e5f5;color:#6a1b9a;")
    row.addWidget(win.lbl_showing)

    row.addStretch()

    win.lbl_history = QLabel("历史已读: 0")
    win.lbl_history.setStyleSheet("color:#888;font-size:12px;")
    row.addWidget(win.lbl_history)
    return row


def build_table(win) -> QTableWidget:
    """新闻表格"""
    win.table = QTableWidget()
    win.table.setColumnCount(6)
    win.table.setHorizontalHeaderLabels(
        ["状态", "标题", "来源", "时间", "阅读量", "摘要"]
    )
    h = win.table.horizontalHeader()
    h.setSectionResizeMode(0, QHeaderView.Fixed)
    win.table.setColumnWidth(0, 50)
    h.setSectionResizeMode(1, QHeaderView.Stretch)
    for c in (2, 3, 4):
        h.setSectionResizeMode(c, QHeaderView.ResizeToContents)
    h.setSectionResizeMode(5, QHeaderView.Stretch)
    win.table.setSelectionBehavior(QTableWidget.SelectRows)
    win.table.setEditTriggers(QTableWidget.NoEditTriggers)
    win.table.setAlternatingRowColors(False)
    win.table.cellDoubleClicked.connect(win._on_cell_dblclick)
    return win.table


def build_bottom_bar(win) -> QHBoxLayout:
    """底部操作栏"""
    row = QHBoxLayout()

    win.btn_clear_history = QPushButton("清空历史记录")
    win.btn_clear_history.setStyleSheet(
        "QPushButton{color:#999;border:1px solid #ddd;font-size:12px;}"
    )
    win.btn_clear_history.clicked.connect(win._on_clear_history)
    row.addWidget(win.btn_clear_history)

    row.addStretch()

    win.btn_export = QPushButton("  导出到文件夹 (每条新闻单独TXT)  ")
    win.btn_export.setFixedHeight(38)
    win.btn_export.setStyleSheet(
        "QPushButton{background:#1976d2;color:#fff;font-size:13px;"
        "border-radius:4px;padding:0 24px;border:none}"
        "QPushButton:hover{background:#1565c0}"
        "QPushButton:disabled{background:#ccc}"
    )
    win.btn_export.clicked.connect(win._on_export)
    win.btn_export.setEnabled(False)
    row.addWidget(win.btn_export)
    return row
