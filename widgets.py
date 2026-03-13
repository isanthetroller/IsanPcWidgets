import random
import time
import asyncio
import threading
import psutil
from datetime import datetime, date
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QProgressBar, QGridLayout, QPushButton, QSizePolicy,
)
from PySide6.QtCore import Qt, QTimer, QTime, QDate
from PySide6.QtGui import (
    QGuiApplication, QPixmap, QImage, QIcon, QPainter, QColor, QPen,
    QPolygon,
)
from PySide6.QtCore import QPoint
from themes import build_stylesheet


def _screen_factor():
    """Return a multiplier based on primary screen DPI (1.0 at 96 DPI)."""
    try:
        scr = QGuiApplication.primaryScreen()
        if scr:
            return scr.logicalDotsPerInch() / 96.0
    except Exception:
        pass
    return 1.0

QUOTES = [
    ("The only way to do great work is to love what you do.", "Steve Jobs"),
    ("Stay hungry, stay foolish.", "Steve Jobs"),
    ("Simplicity is the ultimate sophistication.", "Leonardo da Vinci"),
    ("The future belongs to those who believe in the beauty of their dreams.", "Eleanor Roosevelt"),
    ("In the middle of difficulty lies opportunity.", "Albert Einstein"),
    ("Do what you can, with what you have, where you are.", "Theodore Roosevelt"),
    ("It does not matter how slowly you go as long as you do not stop.", "Confucius"),
    ("Everything you can imagine is real.", "Pablo Picasso"),
    ("The best time to plant a tree was 20 years ago. The second best time is now.", "Chinese Proverb"),
    ("Not all those who wander are lost.", "J.R.R. Tolkien"),
    ("Be the change you wish to see in the world.", "Mahatma Gandhi"),
    ("What we think, we become.", "Buddha"),
    ("The mind is everything. What you think you become.", "Buddha"),
    ("Life is what happens when you're busy making other plans.", "John Lennon"),
    ("The unexamined life is not worth living.", "Socrates"),
    ("To be yourself in a world that is constantly trying to make you something else is the greatest accomplishment.", "Ralph Waldo Emerson"),
    ("Two things are infinite: the universe and human stupidity; and I'm not sure about the universe.", "Albert Einstein"),
    ("You miss 100% of the shots you don't take.", "Wayne Gretzky"),
    ("The only impossible journey is the one you never begin.", "Tony Robbins"),
    ("Act as if what you do makes a difference. It does.", "William James"),
    ("Success is not final, failure is not fatal: it is the courage to continue that counts.", "Winston Churchill"),
    ("Believe you can and you're halfway there.", "Theodore Roosevelt"),
    ("The secret of getting ahead is getting started.", "Mark Twain"),
    ("I have not failed. I've just found 10,000 ways that won't work.", "Thomas Edison"),
    ("It is during our darkest moments that we must focus to see the light.", "Aristotle"),
    ("In three words I can sum up everything I've learned about life: it goes on.", "Robert Frost"),
    ("The only limit to our realization of tomorrow is our doubts of today.", "Franklin D. Roosevelt"),
    ("Do one thing every day that scares you.", "Eleanor Roosevelt"),
    ("The purpose of our lives is to be happy.", "Dalai Lama"),
    ("Life is really simple, but we insist on making it complicated.", "Confucius"),
    ("If you look at what you have in life, you'll always have more.", "Oprah Winfrey"),
    ("Whoever is happy will make others happy too.", "Anne Frank"),
    ("You only live once, but if you do it right, once is enough.", "Mae West"),
    ("The way to get started is to quit talking and begin doing.", "Walt Disney"),
    ("If you set your goals ridiculously high and it's a failure, you will fail above everyone else's success.", "James Cameron"),
    ("The greatest glory in living lies not in never falling, but in rising every time we fall.", "Nelson Mandela"),
]


def _make_divider():
    d = QLabel()
    d.setObjectName("divider")
    d.setFixedHeight(1)
    d.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    return d


class BaseWidget(QWidget):
    def __init__(self, widget_id, config, parent=None):
        super().__init__(parent)
        self.widget_id = widget_id
        self.config = config
        self._drag_pos = None

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        self.bg = QWidget(self)
        self.bg.setObjectName("widgetBg")

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.bg)

        self.content_layout = QVBoxLayout(self.bg)
        self.content_layout.setContentsMargins(24, 18, 24, 18)
        self.content_layout.setSpacing(2)

        self._widget_ready = False
        self.apply_theme()
        self._restore_position()

    def apply_theme(self):
        custom = self.config.get("custom_colors") or None
        self.setStyleSheet(build_stylesheet(
            self.config.get("theme", "emerald"),
            self.config.get("font", "Bahnschrift"),
            self._scale(),
            self.config.get("no_bg", False),
            custom,
        ))
        # Apply per-widget opacity
        opacity = self.config.get("widgets", {}).get(self.widget_id, {}).get("opacity", 1.0)
        self.setWindowOpacity(max(0.1, min(1.0, opacity)))
        if self._widget_ready:
            self._resize_for_scale()

    def _resize_for_scale(self):
        pass

    def _set_adaptive_size(self, base_w, base_h):
        """Set widget size accounting for scale and screen DPI.
        No max-width constraint so text is never clipped."""
        s = self._scale()
        dpi = _screen_factor()
        w = int(base_w * s * dpi)
        h = int(base_h * s * dpi)
        self.setMinimumSize(w, h)
        self.setMaximumSize(16777215, int(h * 2))  # no width cap
        self.resize(w, h)
        self.adjustSize()

    def _restore_position(self):
        wc = self.config.get("widgets", {}).get(self.widget_id, {})
        self.move(wc.get("x", 200), wc.get("y", 150))

    def _save_position(self):
        pos = self.pos()
        self.config.setdefault("widgets", {}).setdefault(self.widget_id, {})
        self.config["widgets"][self.widget_id]["x"] = pos.x()
        self.config["widgets"][self.widget_id]["y"] = pos.y()

    def mousePressEvent(self, event):
        if self.config.get("locked", False):
            event.ignore()
            return
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.config.get("locked", False):
            event.ignore()
            return
        if self._drag_pos and event.buttons() & Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        if self.config.get("locked", False):
            event.ignore()
            return
        if event.button() == Qt.LeftButton:
            self._drag_pos = None
            self._save_position()
            event.accept()

    def _scale(self):
        return max(0.4, min(3.0, self.config.get("widgets", {}).get(self.widget_id, {}).get("scale", 1.0)))

    def _get_style(self):
        """Get the current style dict for this widget from WIDGET_STYLES."""
        from pickers import WIDGET_STYLES
        styles = WIDGET_STYLES.get(self.widget_id, {})
        sid = self.config.get("widgets", {}).get(self.widget_id, {}).get("style", "default")
        first_key = next(iter(styles), "default")
        return styles.get(sid, styles.get(first_key, {}))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DATETIME — template-based day/date/time
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class DateTimeWidget(BaseWidget):
    def __init__(self, config):
        super().__init__("datetime", config)
        self.day_label = QLabel()
        self.day_label.setObjectName("day")
        self.day_label.setAlignment(Qt.AlignCenter)
        self.date_label = QLabel()
        self.date_label.setObjectName("date")
        self.date_label.setAlignment(Qt.AlignCenter)
        self.time_label = QLabel()
        self.time_label.setObjectName("time")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(self.day_label)
        self.content_layout.addWidget(self.date_label)
        self.content_layout.addWidget(self.time_label)
        self._cached_minute = -1
        self._widget_ready = True
        self._resize_for_scale()
        self._update()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update)
        self.timer.start(1000)

    def _get_template(self):
        from pickers import DATETIME_TEMPLATES
        tid = self.config.get("widgets", {}).get("datetime", {}).get("template", "classic")
        return DATETIME_TEMPLATES.get(tid, DATETIME_TEMPLATES["classic"])

    def _resize_for_scale(self):
        t = self._get_template()
        if t["layout"] == "compact":
            self._set_adaptive_size(460, 80)
        else:
            self._set_adaptive_size(460, 160)

    def _update(self):
        from pickers import DATETIME_TEMPLATES
        t = self._get_template()
        now = QTime.currentTime()
        today = QDate.currentDate()

        # Time string
        time_str = now.toString(t["time_fmt"])
        time_str = f"{t['time_prefix']}{time_str}{t['time_suffix']}"
        if t["show_ampm"]:
            time_str += " AM" if now.hour() < 12 else " PM"

        self.time_label.setText(time_str)

        m = now.minute()
        if m != self._cached_minute:
            self._cached_minute = m
            # Day string
            day_text = today.toString(t["day_fmt"]) if t["day_fmt"] else ""
            tr = t["day_transform"]
            if tr == "upper":
                day_text = day_text.upper()
            elif tr == "title":
                day_text = day_text.title()
            elif tr == "spaced":
                day_text = "  ".join(day_text.upper())
            self.day_label.setText(day_text)

            # Date string
            date_text = today.toString(t["date_fmt"]) if t["date_fmt"] else ""
            if t["date_transform"] == "upper":
                date_text = date_text.upper()
            self.date_label.setText(date_text)

        # Let widget grow to fit content
        self.adjustSize()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CLOCK — big time only, clean and minimal
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class ClockWidget(BaseWidget):
    def __init__(self, config):
        super().__init__("clock", config)
        self.time_label = QLabel()
        self.time_label.setObjectName("clock_big")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.sec_label = QLabel()
        self.sec_label.setObjectName("clock_sec")
        self.sec_label.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(self.time_label)
        self.content_layout.addWidget(self.sec_label)
        self._widget_ready = True
        self._resize_for_scale()
        self._update()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update)
        self.timer.start(1000)

    def _resize_for_scale(self):
        self._set_adaptive_size(340, 140)

    def _update(self):
        st = self._get_style()
        now = QTime.currentTime()
        fmt = st.get("fmt", "HH:mm")
        # Handle custom format strings that aren't Qt format
        if " · " in fmt:
            self.time_label.setText(now.toString("HH") + " · " + now.toString("mm"))
        else:
            self.time_label.setText(now.toString(fmt))
        if st.get("show_sec", True):
            sec_fmt = st.get("sec_fmt", ":ss")
            if st.get("ampm"):
                self.sec_label.setText(now.toString(":ss") + (" AM" if now.hour() < 12 else " PM"))
            else:
                self.sec_label.setText(now.toString(sec_fmt))
            self.sec_label.show()
        else:
            self.sec_label.hide()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SYSTEM MONITOR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class SystemWidget(BaseWidget):
    def __init__(self, config):
        super().__init__("system", config)
        self.title = QLabel("S Y S T E M")
        self.title.setObjectName("title")
        self.title.setAlignment(Qt.AlignCenter)
        self.cpu_label = QLabel()
        self.cpu_label.setObjectName("medium")
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setTextVisible(False)
        self.cpu_bar.setRange(0, 100)
        self.ram_label = QLabel()
        self.ram_label.setObjectName("medium")
        self.ram_bar = QProgressBar()
        self.ram_bar.setTextVisible(False)
        self.ram_bar.setRange(0, 100)
        self.disk_label = QLabel()
        self.disk_label.setObjectName("dim")
        self.disk_bar = QProgressBar()
        self.disk_bar.setTextVisible(False)
        self.disk_bar.setRange(0, 100)
        self.content_layout.addWidget(self.title)
        self.content_layout.setSpacing(4)
        for lbl, bar in [(self.cpu_label, self.cpu_bar), (self.ram_label, self.ram_bar), (self.disk_label, self.disk_bar)]:
            self.content_layout.addWidget(lbl)
            self.content_layout.addWidget(bar)
        self._prev = {"cpu": None, "ram": None, "disk": None}
        self._disk_tick = 0
        psutil.cpu_percent(interval=0)
        self._widget_ready = True
        self._resize_for_scale()
        self._update()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update)
        self.timer.start(3000)

    def _resize_for_scale(self):
        st = self._get_style()
        self._set_adaptive_size(320, 160 if st.get("show_disk", True) else 160)
        # Apply style-specific visibility
        show_disk = st.get("show_disk", True)
        self.disk_label.setVisible(show_disk)
        self.disk_bar.setVisible(show_disk and st.get("show_bars", True))
        self.cpu_bar.setVisible(st.get("show_bars", True))
        self.ram_bar.setVisible(st.get("show_bars", True))
        title_text = st.get("title", "S Y S T E M")
        self.title.setText(title_text)

    def _update(self):
        st = self._get_style()
        cpu = round(psutil.cpu_percent(interval=0))
        if cpu != self._prev["cpu"]:
            self._prev["cpu"] = cpu
            self.cpu_label.setText(f"C P U          {cpu}%")
            self.cpu_bar.setValue(cpu)
        mem = psutil.virtual_memory()
        ram = round(mem.percent)
        if ram != self._prev["ram"]:
            self._prev["ram"] = ram
            used = mem.used / (1024 ** 3)
            total = mem.total / (1024 ** 3)
            self.ram_label.setText(f"R A M          {used:.1f} / {total:.1f} GB")
            self.ram_bar.setValue(ram)
        if st.get("show_disk", True):
            self._disk_tick += 1
            if self._disk_tick >= 10 or self._prev["disk"] is None:
                self._disk_tick = 0
                disk = round(psutil.disk_usage("C:\\").percent)
                if disk != self._prev["disk"]:
                    self._prev["disk"] = disk
                    self.disk_label.setText(f"D I S K        {disk}%")
                    self.disk_bar.setValue(disk)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STOPWATCH — start/stop/reset
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class StopwatchWidget(BaseWidget):
    def __init__(self, config):
        super().__init__("stopwatch", config)
        self.title = QLabel("S T O P W A T C H")
        self.title.setObjectName("title")
        self.title.setAlignment(Qt.AlignCenter)
        self.display = QLabel("00:00")
        self.display.setObjectName("stopwatch_display")
        self.display.setAlignment(Qt.AlignCenter)
        self.ms_label = QLabel(".00")
        self.ms_label.setObjectName("stopwatch_ms")
        self.ms_label.setAlignment(Qt.AlignCenter)

        btn_row = QHBoxLayout()
        self.start_btn = QPushButton("START")
        self.start_btn.setObjectName("sw_btn")
        self.start_btn.clicked.connect(self._toggle)
        self.reset_btn = QPushButton("RESET")
        self.reset_btn.setObjectName("sw_btn")
        self.reset_btn.clicked.connect(self._reset)
        btn_row.addWidget(self.start_btn)
        btn_row.addWidget(self.reset_btn)

        self.content_layout.addWidget(self.title)
        self.content_layout.addWidget(self.display)
        self.content_layout.addWidget(self.ms_label)
        self.content_layout.addLayout(btn_row)

        self._running = False
        self._elapsed = 0.0
        self._last_tick = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update)
        self.timer.setInterval(50)
        self._widget_ready = True
        self._resize_for_scale()

    def _resize_for_scale(self):
        self._set_adaptive_size(280, 180)
        st = self._get_style()
        self.title.setText(st.get("title", "S T O P W A T C H"))
        self.ms_label.setVisible(st.get("show_ms", True))

    def _toggle(self):
        if self._running:
            self._running = False
            self.start_btn.setText("START")
            self.timer.stop()
        else:
            self._running = True
            self._last_tick = time.monotonic()
            self.start_btn.setText("STOP")
            self.timer.start()

    def _reset(self):
        self._running = False
        self._elapsed = 0.0
        self.start_btn.setText("START")
        self.timer.stop()
        self.display.setText("00:00")
        self.ms_label.setText(".00")

    def _update(self):
        now = time.monotonic()
        self._elapsed += now - self._last_tick
        self._last_tick = now
        total_sec = int(self._elapsed)
        ms = int((self._elapsed - total_sec) * 100)
        mins = total_sec // 60
        secs = total_sec % 60
        self.display.setText(f"{mins:02d}:{secs:02d}")
        self.ms_label.setText(f".{ms:02d}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# QUOTES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class QuotesWidget(BaseWidget):
    def __init__(self, config):
        super().__init__("quotes", config)
        self.bird = QLabel("🕊")
        self.bird.setObjectName("bird_icon")
        self.bird.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(self.bird)
        self.content_layout.addWidget(_make_divider())
        self.quote_label = QLabel()
        self.quote_label.setObjectName("quote_text")
        self.quote_label.setAlignment(Qt.AlignCenter)
        self.quote_label.setWordWrap(True)
        self.author_label = QLabel()
        self.author_label.setObjectName("quote_author")
        self.author_label.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(self.quote_label)
        self.content_layout.addWidget(self.author_label)
        self._show_quote()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._show_quote)
        self.timer.start(60000)
        self._widget_ready = True
        self._resize_for_scale()

    def _resize_for_scale(self):
        self._set_adaptive_size(360, 180)
        st = self._get_style()
        icon_text = st.get("icon", "🕊")
        if st.get("show_icon", True) and icon_text:
            self.bird.setText(icon_text)
            self.bird.show()
        else:
            self.bird.hide()

    def _show_quote(self):
        text, author = random.choice(QUOTES)
        st = self._get_style()
        if st.get("italic", True):
            self.quote_label.setText(f'\u201c{text}\u201d')
        else:
            self.quote_label.setText(text)
        self.author_label.setText(f"\u2014 {author}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MINI CALENDAR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class CalendarWidget(BaseWidget):
    def __init__(self, config):
        super().__init__("calendar", config)
        self.month_label = QLabel()
        self.month_label.setObjectName("title")
        self.month_label.setAlignment(Qt.AlignCenter)
        self.grid = QGridLayout()
        self.grid.setSpacing(2)
        self.content_layout.addWidget(self.month_label)
        self.content_layout.addWidget(_make_divider())
        self.content_layout.addLayout(self.grid)
        self._day_labels = []
        self._build_calendar()
        self._current_day = date.today().day
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._check_day_change)
        self.timer.start(60000)
        self._widget_ready = True
        self._resize_for_scale()

    def _resize_for_scale(self):
        self._set_adaptive_size(320, 260)

    def _check_day_change(self):
        if date.today().day != self._current_day:
            self._current_day = date.today().day
            self._build_calendar()

    def _build_calendar(self):
        st = self._get_style()
        for lbl in self._day_labels:
            lbl.deleteLater()
        self._day_labels = []
        today = date.today()
        title_fmt = st.get("title_fmt", "%B  %Y")
        title_text = today.strftime(title_fmt)
        if st.get("title_transform", "upper") == "upper":
            title_text = title_text.upper()
        elif st.get("title_transform") == "title":
            title_text = title_text.title()
        self.month_label.setText(title_text)

        week_start = st.get("week_start", 0)  # 0=Monday, 6=Sunday
        if week_start == 6:
            day_names = ["SU", "MO", "TU", "WE", "TH", "FR", "SA"]
        else:
            day_names = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]
        for i, d in enumerate(day_names):
            lbl = QLabel(d)
            lbl.setObjectName("dim")
            lbl.setAlignment(Qt.AlignCenter)
            self.grid.addWidget(lbl, 0, i)
            self._day_labels.append(lbl)
        import calendar as cal_mod
        c = cal_mod.Calendar(firstweekday=week_start)
        for row_idx, week in enumerate(c.monthdayscalendar(today.year, today.month)):
            for col_idx, day in enumerate(week):
                lbl = QLabel(str(day) if day else "")
                lbl.setObjectName("accent" if day == today.day else "dim")
                lbl.setAlignment(Qt.AlignCenter)
                self.grid.addWidget(lbl, row_idx + 1, col_idx)
                self._day_labels.append(lbl)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# COUNTDOWN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class CountdownWidget(BaseWidget):
    def __init__(self, config):
        super().__init__("countdown", config)
        wc = config.get("widgets", {}).get("countdown", {})
        self.target_str = wc.get("target", "2026-12-31")
        self.label_text = wc.get("label", "New Year")
        self.title = QLabel(self.label_text.upper())
        self.title.setObjectName("title")
        self.title.setAlignment(Qt.AlignCenter)
        self.days_label = QLabel()
        self.days_label.setObjectName("accent_big")
        self.days_label.setAlignment(Qt.AlignCenter)
        self.sub_label = QLabel("D A Y S   R E M A I N I N G")
        self.sub_label.setObjectName("dim")
        self.sub_label.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(self.title)
        self.content_layout.addWidget(_make_divider())
        self.content_layout.addWidget(self.days_label)
        self.content_layout.addWidget(self.sub_label)
        self._update()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update)
        self.timer.start(60000)
        self._widget_ready = True
        self._resize_for_scale()

    def _resize_for_scale(self):
        self._set_adaptive_size(280, 160)

    def _update(self):
        st = self._get_style()
        try:
            target = datetime.strptime(self.target_str, "%Y-%m-%d").date()
            delta = max(0, (target - date.today()).days)
            unit = st.get("unit", "days")
            if unit == "weeks":
                weeks = delta // 7
                days_r = delta % 7
                self.days_label.setText(str(weeks))
                self.sub_label.setText(f"W E E K S  +  {days_r}  D A Y S")
            elif unit == "detailed":
                months = delta // 30
                weeks = (delta % 30) // 7
                days_r = delta % 7
                self.days_label.setText(str(delta))
                self.sub_label.setText(f"{months}mo  {weeks}w  {days_r}d")
            else:
                self.days_label.setText(str(delta))
                self.sub_label.setText(st.get("sub_text", "D A Y S   R E M A I N I N G"))
        except ValueError:
            self.days_label.setText("?")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# BATTERY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class BatteryWidget(BaseWidget):
    def __init__(self, config):
        super().__init__("battery", config)
        self.title = QLabel("B A T T E R Y")
        self.title.setObjectName("title")
        self.title.setAlignment(Qt.AlignCenter)
        self.pct_label = QLabel()
        self.pct_label.setObjectName("accent_big")
        self.pct_label.setAlignment(Qt.AlignCenter)
        self.status_label = QLabel()
        self.status_label.setObjectName("dim")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.bar = QProgressBar()
        self.bar.setTextVisible(False)
        self.bar.setRange(0, 100)
        self.content_layout.addWidget(self.title)
        self.content_layout.addWidget(_make_divider())
        self.content_layout.addWidget(self.pct_label)
        self.content_layout.addWidget(self.bar)
        self.content_layout.addWidget(self.status_label)
        self._prev_pct = None
        self._widget_ready = True
        self._resize_for_scale()
        self._update()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update)
        self.timer.start(15000)

    def _resize_for_scale(self):
        self._set_adaptive_size(220, 170)
        st = self._get_style()
        self.title.setText(st.get("title", "B A T T E R Y"))
        self.bar.setVisible(st.get("show_bar", True))

    def _update(self):
        bat = psutil.sensors_battery()
        if bat is None:
            if self._prev_pct is None:
                self.pct_label.setText("N/A")
                self.status_label.setText("No battery detected")
                self.bar.setValue(0)
                self._prev_pct = -1
            return
        pct = round(bat.percent)
        if pct != self._prev_pct:
            self._prev_pct = pct
            self.pct_label.setText(f"{pct}%")
            self.bar.setValue(pct)
            if bat.power_plugged:
                self.status_label.setText("⚡  Charging" if pct < 100 else "⚡  Full")
            else:
                secs = bat.secsleft
                if secs > 0:
                    h, m = divmod(secs // 60, 60)
                    self.status_label.setText(f"~{h}h {m}m remaining")
                else:
                    self.status_label.setText("Discharging")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# UPTIME
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class UptimeWidget(BaseWidget):
    def __init__(self, config):
        super().__init__("uptime", config)
        self.title = QLabel("U P T I M E")
        self.title.setObjectName("title")
        self.title.setAlignment(Qt.AlignCenter)
        self.uptime_label = QLabel()
        self.uptime_label.setObjectName("big")
        self.uptime_label.setAlignment(Qt.AlignCenter)
        self.detail_label = QLabel()
        self.detail_label.setObjectName("dim")
        self.detail_label.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(self.title)
        self.content_layout.addWidget(_make_divider())
        self.content_layout.addWidget(self.uptime_label)
        self.content_layout.addWidget(self.detail_label)
        self._boot = psutil.boot_time()
        self._prev_min = -1
        self._widget_ready = True
        self._resize_for_scale()
        self._update()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update)
        self.timer.start(30000)

    def _resize_for_scale(self):
        self._set_adaptive_size(250, 140)
        st = self._get_style()
        self.title.setText(st.get("title", "U P T I M E"))

    def _update(self):
        st = self._get_style()
        elapsed = int(time.time() - self._boot)
        mins = elapsed // 60
        if mins == self._prev_min:
            return
        self._prev_min = mins
        days, rem = divmod(elapsed, 86400)
        hours, rem = divmod(rem, 3600)
        minutes = rem // 60
        seconds = rem % 60
        fmt = st.get("fmt", "short")
        if fmt == "full":
            if days > 0:
                self.uptime_label.setText(f"{days}d {hours}h {minutes}m")
            else:
                self.uptime_label.setText(f"{hours}h {minutes}m {seconds}s")
            self.detail_label.setText(f"{elapsed:,} seconds total")
        elif fmt == "compact":
            total_h = days * 24 + hours
            self.uptime_label.setText(f"{total_h}h {minutes}m")
            self.detail_label.setText("")
        else:
            if days > 0:
                self.uptime_label.setText(f"{days}d {hours}h")
                self.detail_label.setText(f"{minutes}m elapsed")
            else:
                self.uptime_label.setText(f"{hours}h {minutes}m")
                from datetime import datetime as dt
                self.detail_label.setText(f"since {dt.fromtimestamp(self._boot).strftime('%H:%M')}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NETWORK SPEED
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class NetworkWidget(BaseWidget):
    def __init__(self, config):
        super().__init__("network", config)
        self.title = QLabel("N E T W O R K")
        self.title.setObjectName("title")
        self.title.setAlignment(Qt.AlignCenter)
        self.up_label = QLabel("↑  0 KB/s")
        self.up_label.setObjectName("net_up")
        self.up_label.setAlignment(Qt.AlignCenter)
        self.down_label = QLabel("↓  0 KB/s")
        self.down_label.setObjectName("net_down")
        self.down_label.setAlignment(Qt.AlignCenter)
        self.total_label = QLabel()
        self.total_label.setObjectName("dim")
        self.total_label.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(self.title)
        self.content_layout.addWidget(_make_divider())
        self.content_layout.addWidget(self.up_label)
        self.content_layout.addWidget(self.down_label)
        self.content_layout.addWidget(_make_divider())
        self.content_layout.addWidget(self.total_label)
        counters = psutil.net_io_counters()
        self._prev_sent = counters.bytes_sent
        self._prev_recv = counters.bytes_recv
        self._update_total(counters)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update)
        self.timer.start(2000)
        self._widget_ready = True
        self._resize_for_scale()

    def _resize_for_scale(self):
        self._set_adaptive_size(240, 175)
        st = self._get_style()
        self.title.setText(st.get("title", "N E T W O R K"))
        show_total = st.get("show_total", True)
        self.total_label.setVisible(show_total)

    @staticmethod
    def _fmt(b):
        if b >= 1048576:
            return f"{b / 1048576:.1f} MB/s"
        return f"{b / 1024:.0f} KB/s"

    @staticmethod
    def _fmt_total(b):
        if b >= 1073741824:
            return f"{b / 1073741824:.2f} GB"
        return f"{b / 1048576:.0f} MB"

    def _update_total(self, c):
        self.total_label.setText(f"↑ {self._fmt_total(c.bytes_sent)}   ↓ {self._fmt_total(c.bytes_recv)}")

    def _update(self):
        c = psutil.net_io_counters()
        up = (c.bytes_sent - self._prev_sent) / 2
        dn = (c.bytes_recv - self._prev_recv) / 2
        self._prev_sent = c.bytes_sent
        self._prev_recv = c.bytes_recv
        self.up_label.setText(f"↑  {self._fmt(up)}")
        self.down_label.setText(f"↓  {self._fmt(dn)}")
        self._update_total(c)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NOTES — centered, divider, spaced
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class NotesWidget(BaseWidget):
    def __init__(self, config):
        super().__init__("notes", config)
        self.title = QLabel("N O T E S")
        self.title.setObjectName("title")
        self.title.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(self.title)
        self.content_layout.addSpacing(6)
        self.content_layout.addWidget(_make_divider())
        self.content_layout.addSpacing(6)
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Type your notes here...")
        self.text_edit.setAlignment(Qt.AlignCenter)
        saved = config.get("widgets", {}).get("notes", {}).get("text", "")
        if saved:
            self.text_edit.setPlainText(saved)
            cursor = self.text_edit.textCursor()
            self.text_edit.selectAll()
            fmt = cursor.blockFormat()
            fmt.setAlignment(Qt.AlignCenter)
            cursor.mergeBlockFormat(fmt)
            cursor.clearSelection()
            self.text_edit.setTextCursor(cursor)
        self.content_layout.addWidget(self.text_edit)
        self._save_timer = QTimer(self)
        self._save_timer.setSingleShot(True)
        self._save_timer.timeout.connect(self._do_save)
        self.text_edit.textChanged.connect(self._on_text_changed)
        self._widget_ready = True
        self._resize_for_scale()

    def _resize_for_scale(self):
        self._set_adaptive_size(300, 260)
        st = self._get_style()
        if st.get("show_title", True):
            self.title.setText(st.get("title", "N O T E S"))
            self.title.show()
        else:
            self.title.hide()

    def _on_text_changed(self):
        # Re-center all paragraphs on edit
        cursor = self.text_edit.textCursor()
        cursor.select(cursor.Document)
        fmt = cursor.blockFormat()
        fmt.setAlignment(Qt.AlignCenter)
        cursor.mergeBlockFormat(fmt)
        cursor.clearSelection()
        self.text_edit.setTextCursor(cursor)
        self._save_timer.start(1000)

    def _do_save(self):
        self.config.setdefault("widgets", {}).setdefault("notes", {})
        self.config["widgets"]["notes"]["text"] = self.text_edit.toPlainText()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GREETING — time-aware greeting message
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class GreetingWidget(BaseWidget):
    def __init__(self, config):
        super().__init__("greeting", config)
        self.greeting_label = QLabel()
        self.greeting_label.setObjectName("day")
        self.greeting_label.setAlignment(Qt.AlignCenter)
        self.sub_label = QLabel()
        self.sub_label.setObjectName("date")
        self.sub_label.setAlignment(Qt.AlignCenter)
        self.time_label = QLabel()
        self.time_label.setObjectName("time")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(self.greeting_label)
        self.content_layout.addWidget(_make_divider())
        self.content_layout.addWidget(self.sub_label)
        self.content_layout.addWidget(self.time_label)
        self._cached_hour = -1
        self._widget_ready = True
        self._resize_for_scale()
        self._update()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update)
        self.timer.start(30000)

    def _resize_for_scale(self):
        self._set_adaptive_size(370, 150)

    def _update(self):
        st = self._get_style()
        now = QTime.currentTime()
        h = now.hour()
        if h != self._cached_hour:
            self._cached_hour = h
            fmt = st.get("fmt", "standard")
            if fmt == "casual":
                if h < 6:
                    greet = "Hey, Night Owl"
                elif h < 12:
                    greet = "Hey There!"
                elif h < 17:
                    greet = "What's Up!"
                elif h < 21:
                    greet = "Hey, Evening!"
                else:
                    greet = "Hey, Night Owl"
            elif fmt == "formal":
                if h < 6:
                    greet = "Good Night"
                elif h < 12:
                    greet = "Good Morning"
                elif h < 17:
                    greet = "Good Afternoon"
                elif h < 21:
                    greet = "Good Evening"
                else:
                    greet = "Good Night"
            elif fmt == "wave":
                if h < 6:
                    greet = "🌙 Good Night"
                elif h < 12:
                    greet = "👋 Good Morning"
                elif h < 17:
                    greet = "☀️ Good Afternoon"
                elif h < 21:
                    greet = "🌅 Good Evening"
                else:
                    greet = "🌙 Good Night"
            else:
                if h < 6:
                    greet = "Good Night"
                elif h < 12:
                    greet = "Good Morning"
                elif h < 17:
                    greet = "Good Afternoon"
                elif h < 21:
                    greet = "Good Evening"
                else:
                    greet = "Good Night"
            self.greeting_label.setText(greet)
            today = QDate.currentDate()
            self.sub_label.setText(today.toString("dddd, MMMM d").upper())
        time_fmt = st.get("time_fmt", "h:mm AP")
        self.time_label.setText(now.toString(time_fmt))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# WORLD CLOCK — show a second timezone
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class WorldClockWidget(BaseWidget):
    def __init__(self, config):
        super().__init__("worldclock", config)
        self.title = QLabel("W O R L D   C L O C K")
        self.title.setObjectName("title")
        self.title.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(self.title)
        self.content_layout.addWidget(_make_divider())

        wc = config.get("widgets", {}).get("worldclock", {})
        self._offsets = wc.get("offsets", [
            {"name": "NEW YORK", "offset": -5},
            {"name": "LONDON", "offset": 0},
            {"name": "TOKYO", "offset": 9},
        ])
        self._time_labels = []
        for tz in self._offsets:
            row = QHBoxLayout()
            name_lbl = QLabel(tz["name"])
            name_lbl.setObjectName("dim")
            name_lbl.setAlignment(Qt.AlignLeft)
            time_lbl = QLabel()
            time_lbl.setObjectName("accent")
            time_lbl.setAlignment(Qt.AlignRight)
            row.addWidget(name_lbl)
            row.addWidget(time_lbl)
            self.content_layout.addLayout(row)
            self._time_labels.append(time_lbl)

        self._update()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update)
        self.timer.start(30000)
        self._widget_ready = True
        self._resize_for_scale()

    def _resize_for_scale(self):
        self._set_adaptive_size(280, 170)
        st = self._get_style()
        self.title.setText(st.get("title", "W O R L D   C L O C K"))

    def _update(self):
        st = self._get_style()
        from datetime import datetime as dt, timezone, timedelta
        utc_now = dt.now(timezone.utc)
        time_fmt = st.get("time_fmt", "%H:%M")
        for i, tz in enumerate(self._offsets):
            t = utc_now + timedelta(hours=tz["offset"])
            self._time_labels[i].setText(t.strftime(time_fmt))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DAY PROGRESS — visual bar showing how much of the day has passed
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class DayProgressWidget(BaseWidget):
    def __init__(self, config):
        super().__init__("dayprogress", config)
        self.title = QLabel("D A Y   P R O G R E S S")
        self.title.setObjectName("title")
        self.title.setAlignment(Qt.AlignCenter)
        self.pct_label = QLabel()
        self.pct_label.setObjectName("accent_big")
        self.pct_label.setAlignment(Qt.AlignCenter)
        self.bar = QProgressBar()
        self.bar.setTextVisible(False)
        self.bar.setRange(0, 1000)
        self.detail_label = QLabel()
        self.detail_label.setObjectName("dim")
        self.detail_label.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(self.title)
        self.content_layout.addWidget(_make_divider())
        self.content_layout.addWidget(self.pct_label)
        self.content_layout.addWidget(self.bar)
        self.content_layout.addWidget(self.detail_label)
        self._widget_ready = True
        self._resize_for_scale()
        self._update()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update)
        self.timer.start(60000)

    def _resize_for_scale(self):
        self._set_adaptive_size(270, 170)
        st = self._get_style()
        self.title.setText(st.get("title", "D A Y   P R O G R E S S"))
        self.bar.setVisible(st.get("show_bar", True))
        self.detail_label.setVisible(st.get("show_remaining", True))

    def _update(self):
        now = QTime.currentTime()
        secs = now.hour() * 3600 + now.minute() * 60 + now.second()
        pct = secs / 864.0  # percent of 86400 * 10 for 0.1% precision
        self.bar.setValue(int(pct))
        display_pct = secs / 864.0
        self.pct_label.setText(f"{display_pct:.1f}%")
        remaining = 86400 - secs
        h, m = divmod(remaining // 60, 60)
        self.detail_label.setText(f"{h}h {m}m remaining")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SPOTIFY / NOW PLAYING — media session from browser or desktop
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Persistent event loop running on a background thread for WinRT calls
_async_loop = asyncio.new_event_loop()
_async_thread = threading.Thread(target=_async_loop.run_forever, daemon=True)
_async_thread.start()


def _run_async(coro):
    """Schedule a coroutine on the background loop and wait for the result."""
    future = asyncio.run_coroutine_threadsafe(coro, _async_loop)
    try:
        return future.result(timeout=4)
    except Exception:
        return None


def _make_media_icon(icon_type, color="#FFFFFF", size=28):
    """Draw media control icons with QPainter. icon_type: prev|play|pause|next"""
    px = QPixmap(size, size)
    px.fill(Qt.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(Qt.NoPen)
    p.setBrush(QColor(color))
    m = size // 5  # margin

    if icon_type == "prev":
        # bar + left-pointing triangle
        p.fillRect(m, m, size // 8, size - 2 * m, QColor(color))
        tri = QPolygon([QPoint(size - m, m), QPoint(size - m, size - m), QPoint(m + size // 6, size // 2)])
        p.drawPolygon(tri)
    elif icon_type == "next":
        # right-pointing triangle + bar
        tri = QPolygon([QPoint(m, m), QPoint(m, size - m), QPoint(size - m - size // 6, size // 2)])
        p.drawPolygon(tri)
        p.fillRect(size - m - size // 8, m, size // 8, size - 2 * m, QColor(color))
    elif icon_type == "play":
        # right-pointing triangle
        tri = QPolygon([QPoint(m + 2, m), QPoint(m + 2, size - m), QPoint(size - m, size // 2)])
        p.drawPolygon(tri)
    elif icon_type == "pause":
        # two vertical bars
        bar_w = size // 5
        gap = size // 8
        x1 = size // 2 - gap - bar_w
        x2 = size // 2 + gap
        p.fillRect(x1, m, bar_w, size - 2 * m, QColor(color))
        p.fillRect(x2, m, bar_w, size - 2 * m, QColor(color))

    p.end()
    return QIcon(px)


class SpotifyWidget(BaseWidget):
    def __init__(self, config):
        super().__init__("spotify", config)

        # Album art
        self.art_label = QLabel()
        self.art_label.setObjectName("spotify_art")
        self.art_label.setAlignment(Qt.AlignCenter)
        self.art_label.setFixedSize(80, 80)
        self._default_art()

        # Song info
        self.title_label = QLabel("No media playing")
        self.title_label.setObjectName("spotify_title")
        self.title_label.setWordWrap(True)
        self.artist_label = QLabel("")
        self.artist_label.setObjectName("spotify_artist")
        self.artist_label.setWordWrap(True)

        # Top row: art + info
        top_row = QHBoxLayout()
        top_row.setSpacing(12)
        top_row.addWidget(self.art_label)
        info_col = QVBoxLayout()
        info_col.setSpacing(2)
        info_col.addStretch()
        info_col.addWidget(self.title_label)
        info_col.addWidget(self.artist_label)
        info_col.addStretch()
        top_row.addLayout(info_col)

        # Control buttons with painted icons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        self.prev_btn = QPushButton()
        self.prev_btn.setObjectName("media_btn")
        self.prev_btn.setIcon(_make_media_icon("prev"))
        self.prev_btn.clicked.connect(self._prev_track)
        self.play_btn = QPushButton()
        self.play_btn.setObjectName("media_btn")
        self.play_btn.setIcon(_make_media_icon("play"))
        self.play_btn.clicked.connect(self._play_pause)
        self.next_btn = QPushButton()
        self.next_btn.setObjectName("media_btn")
        self.next_btn.setIcon(_make_media_icon("next"))
        self.next_btn.clicked.connect(self._next_track)
        btn_row.addStretch()
        btn_row.addWidget(self.prev_btn)
        btn_row.addWidget(self.play_btn)
        btn_row.addWidget(self.next_btn)
        btn_row.addStretch()

        self.content_layout.addLayout(top_row)
        self.content_layout.addWidget(_make_divider())
        self.content_layout.addLayout(btn_row)

        self._last_title = None
        self._is_playing = False
        self._widget_ready = True
        self._resize_for_scale()
        self._update()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update)
        self.timer.start(2000)

    def _resize_for_scale(self):
        self._set_adaptive_size(340, 150)
        st = self._get_style()
        self.art_label.setVisible(st.get("show_art", True))
        show_controls = st.get("show_controls", True)
        self.prev_btn.setVisible(show_controls)
        self.play_btn.setVisible(show_controls)
        self.next_btn.setVisible(show_controls)

    def _default_art(self):
        """Show a music note placeholder when no art is available."""
        self.art_label.setText("\U0001f3b5")
        self.art_label.setStyleSheet(
            "font-size: 36px; background: rgba(128,128,128,30); border-radius: 8px;"
        )

    def _get_session(self):
        """Get the current media session via WinRT."""
        try:
            from winrt.windows.media.control import (
                GlobalSystemMediaTransportControlsSessionManager as MediaManager,
                GlobalSystemMediaTransportControlsSessionPlaybackStatus as PlaybackStatus,
            )
            async def _get():
                mgr = await MediaManager.request_async()
                session = mgr.get_current_session()
                if session is not None:
                    return session
                # Fallback: iterate all sessions, prefer one that is playing
                sessions = mgr.get_sessions()
                best = None
                for i in range(sessions.size):
                    s = sessions.get_at(i)
                    if best is None:
                        best = s
                    try:
                        pb = s.get_playback_info()
                        if pb and pb.playback_status == PlaybackStatus.PLAYING:
                            return s
                    except Exception:
                        pass
                return best
            return _run_async(_get())
        except Exception:
            return None

    def _update(self):
        """Fetch media info + thumbnail + playback status in one async call."""
        try:
            from winrt.windows.media.control import (
                GlobalSystemMediaTransportControlsSessionPlaybackStatus as PlaybackStatus,
            )

            async def _fetch_all():
                session = None
                try:
                    from winrt.windows.media.control import (
                        GlobalSystemMediaTransportControlsSessionManager as MM,
                    )
                    mgr = await MM.request_async()
                    session = mgr.get_current_session()
                    if session is None:
                        sessions = mgr.get_sessions()
                        for i in range(sessions.size):
                            s = sessions.get_at(i)
                            if session is None:
                                session = s
                            try:
                                pb = s.get_playback_info()
                                if pb and pb.playback_status == PlaybackStatus.PLAYING:
                                    session = s
                                    break
                            except Exception:
                                pass
                except Exception:
                    pass

                if session is None:
                    return None

                info = await session.try_get_media_properties_async()
                title = (info.title or "Unknown") if info else "Unknown"
                artist = (info.artist or "") if info else ""

                # Read thumbnail bytes inside the same async context
                thumb_data = None
                if info and info.thumbnail:
                    try:
                        stream = await info.thumbnail.open_read_async()
                        size = stream.size
                        from winrt.windows.storage.streams import Buffer
                        buf = Buffer(size)
                        await stream.read_async(buf, size, 0)
                        thumb_data = bytes(buf)
                    except Exception:
                        pass

                # Playback status
                playing = False
                try:
                    pb = session.get_playback_info()
                    if pb:
                        playing = pb.playback_status == PlaybackStatus.PLAYING
                except Exception:
                    pass

                return {"title": title, "artist": artist, "thumb": thumb_data, "playing": playing}

            result = _run_async(_fetch_all())
        except Exception:
            result = None

        if result is None:
            if self._last_title is not None:
                self.title_label.setText("No media playing")
                self.artist_label.setText("")
                self._default_art()
                self._last_title = None
                self._is_playing = False
                self.play_btn.setIcon(_make_media_icon("play"))
            return

        title = result["title"]
        artist = result["artist"]
        self.title_label.setText(title)
        self.artist_label.setText(artist)

        # Always try to load thumbnail on song change
        if title != self._last_title:
            self._last_title = title
            thumb_data = result["thumb"]
            if thumb_data:
                img = QImage.fromData(thumb_data)
                if not img.isNull():
                    px = QPixmap.fromImage(img).scaled(
                        80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation
                    )
                    self.art_label.setPixmap(px)
                    self.art_label.setStyleSheet(
                        "background: transparent; border-radius: 8px;"
                    )
                else:
                    self._default_art()
            else:
                self._default_art()

        playing = result["playing"]
        if playing != self._is_playing:
            self._is_playing = playing
            self.play_btn.setIcon(
                _make_media_icon("pause" if playing else "play")
            )

    def _load_thumbnail(self, info):
        pass

    def _play_pause(self):
        try:
            async def _action():
                from winrt.windows.media.control import (
                    GlobalSystemMediaTransportControlsSessionManager as MM,
                )
                mgr = await MM.request_async()
                session = mgr.get_current_session()
                if session:
                    await session.try_toggle_play_pause_async()
            _run_async(_action())
            self._is_playing = not self._is_playing
            self.play_btn.setIcon(
                _make_media_icon("pause" if self._is_playing else "play")
            )
        except Exception:
            pass

    def _next_track(self):
        try:
            async def _action():
                from winrt.windows.media.control import (
                    GlobalSystemMediaTransportControlsSessionManager as MM,
                )
                mgr = await MM.request_async()
                session = mgr.get_current_session()
                if session:
                    await session.try_skip_next_async()
            _run_async(_action())
            # Force title refresh so next poll picks up new song
            self._last_title = None
        except Exception:
            pass

    def _prev_track(self):
        try:
            async def _action():
                from winrt.windows.media.control import (
                    GlobalSystemMediaTransportControlsSessionManager as MM,
                )
                mgr = await MM.request_async()
                session = mgr.get_current_session()
                if session:
                    await session.try_skip_previous_async()
            _run_async(_action())
            self._last_title = None
        except Exception:
            pass


# ──────────────────────────────────────────────────────────────────────
WIDGET_CLASSES = {
    "datetime":     DateTimeWidget,
    "clock":        ClockWidget,
    "system":       SystemWidget,
    "stopwatch":    StopwatchWidget,
    "quotes":       QuotesWidget,
    "calendar":     CalendarWidget,
    "countdown":    CountdownWidget,
    "battery":      BatteryWidget,
    "uptime":       UptimeWidget,
    "network":      NetworkWidget,
    "notes":        NotesWidget,
    "greeting":     GreetingWidget,
    "worldclock":   WorldClockWidget,
    "dayprogress":  DayProgressWidget,
    "spotify":      SpotifyWidget,
}
