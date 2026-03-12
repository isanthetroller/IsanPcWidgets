import random
import time
import psutil
from datetime import datetime, date
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QProgressBar, QGridLayout, QPushButton, QSizePolicy,
)
from PySide6.QtCore import Qt, QTimer, QTime, QDate
from themes import build_stylesheet

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

        self.apply_theme()
        self._restore_position()

    def apply_theme(self):
        self.setStyleSheet(build_stylesheet(
            self.config.get("theme", "emerald"),
            self.config.get("font", "Bahnschrift"),
            self._scale(),
            self.config.get("no_bg", False),
        ))
        self._resize_for_scale()

    def _resize_for_scale(self):
        pass

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
        self._update()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update)
        self.timer.start(1000)

    def _get_template(self):
        from pickers import DATETIME_TEMPLATES
        tid = self.config.get("widgets", {}).get("datetime", {}).get("template", "classic")
        return DATETIME_TEMPLATES.get(tid, DATETIME_TEMPLATES["classic"])

    def _resize_for_scale(self):
        s = self._scale()
        t = self._get_template()
        if t["layout"] == "compact":
            self.setFixedSize(int(380 * s), int(80 * s))
        else:
            self.setFixedSize(int(380 * s), int(140 * s))

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
        self._update()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update)
        self.timer.start(1000)

    def _resize_for_scale(self):
        s = self._scale()
        self.setFixedSize(int(320 * s), int(120 * s))

    def _update(self):
        now = QTime.currentTime()
        self.time_label.setText(now.toString("HH:mm"))
        self.sec_label.setText(now.toString(":ss"))


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
        self._update()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update)
        self.timer.start(3000)

    def _resize_for_scale(self):
        s = self._scale()
        self.setFixedSize(int(300 * s), int(210 * s))

    def _update(self):
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

    def _resize_for_scale(self):
        s = self._scale()
        self.setFixedSize(int(280 * s), int(180 * s))

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

    def _resize_for_scale(self):
        s = self._scale()
        self.setFixedSize(int(360 * s), int(170 * s))

    def _show_quote(self):
        text, author = random.choice(QUOTES)
        self.quote_label.setText(f'"{text}"')
        self.author_label.setText(f"— {author}")


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

    def _resize_for_scale(self):
        s = self._scale()
        self.setFixedSize(int(280 * s), int(230 * s))

    def _check_day_change(self):
        if date.today().day != self._current_day:
            self._current_day = date.today().day
            self._build_calendar()

    def _build_calendar(self):
        for lbl in self._day_labels:
            lbl.deleteLater()
        self._day_labels = []
        today = date.today()
        self.month_label.setText(today.strftime("%B  %Y").upper())
        for i, d in enumerate(["MO", "TU", "WE", "TH", "FR", "SA", "SU"]):
            lbl = QLabel(d)
            lbl.setObjectName("dim")
            lbl.setAlignment(Qt.AlignCenter)
            self.grid.addWidget(lbl, 0, i)
            self._day_labels.append(lbl)
        import calendar
        for row_idx, week in enumerate(calendar.monthcalendar(today.year, today.month)):
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

    def _resize_for_scale(self):
        s = self._scale()
        self.setFixedSize(int(280 * s), int(160 * s))

    def _update(self):
        try:
            target = datetime.strptime(self.target_str, "%Y-%m-%d").date()
            self.days_label.setText(str(max(0, (target - date.today()).days)))
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
        self._update()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update)
        self.timer.start(15000)

    def _resize_for_scale(self):
        s = self._scale()
        self.setFixedSize(int(220 * s), int(170 * s))

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
        self._update()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update)
        self.timer.start(30000)

    def _resize_for_scale(self):
        s = self._scale()
        self.setFixedSize(int(250 * s), int(140 * s))

    def _update(self):
        elapsed = int(time.time() - self._boot)
        mins = elapsed // 60
        if mins == self._prev_min:
            return
        self._prev_min = mins
        days, rem = divmod(elapsed, 86400)
        hours, rem = divmod(rem, 3600)
        minutes = rem // 60
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

    def _resize_for_scale(self):
        s = self._scale()
        self.setFixedSize(int(240 * s), int(175 * s))

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

    def _resize_for_scale(self):
        s = self._scale()
        self.setFixedSize(int(300 * s), int(260 * s))

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


# ──────────────────────────────────────────────────────────────────────
WIDGET_CLASSES = {
    "datetime":  DateTimeWidget,
    "clock":     ClockWidget,
    "system":    SystemWidget,
    "stopwatch": StopwatchWidget,
    "quotes":    QuotesWidget,
    "calendar":  CalendarWidget,
    "countdown": CountdownWidget,
    "battery":   BatteryWidget,
    "uptime":    UptimeWidget,
    "network":   NetworkWidget,
    "notes":     NotesWidget,
}
