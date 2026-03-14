from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QScrollArea, QWidget, QFrame, QLineEdit,
    QSlider, QPushButton, QColorDialog,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor


# ── Shared dark dialog style ──────────────────────────────────────────

DIALOG_STYLE = """
    QDialog {
        background-color: #1a1a1a;
    }
    QLabel#heading {
        color: #ffffff;
        font-size: 20px;
        font-weight: bold;
        background: transparent;
    }
    QLabel#subhead {
        color: #888888;
        font-size: 12px;
        background: transparent;
    }
    QScrollArea {
        border: none;
        background: transparent;
    }
    QLineEdit#searchBox {
        background-color: #2a2a2a;
        color: #e0e0e0;
        border: 1px solid #444;
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 13px;
    }
    QLineEdit#searchBox:focus {
        border: 1px solid #A8F0D0;
    }
"""

SCROLLBAR_STYLE = """
    QScrollBar:vertical {
        background: #222; width: 8px; border-radius: 4px;
    }
    QScrollBar::handle:vertical {
        background: #555; border-radius: 4px; min-height: 30px;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0;
    }
"""


# ══════════════════════════════════════════════════════════════════════
#  THEME PICKER
# ══════════════════════════════════════════════════════════════════════

class ThemeCard(QFrame):
    clicked = Signal(str)

    def __init__(self, theme_id, theme_data, is_selected=False, parent=None):
        super().__init__(parent)
        self.theme_id = theme_id
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(170, 120)

        bg = theme_data["bg"]
        fg = theme_data["fg"]
        accent = theme_data["accent"]
        dim = theme_data.get("dim", fg)

        sel_border = "#FFFFFF" if is_selected else "transparent"
        sel_width = 3 if is_selected else 0

        self.setStyleSheet(f"""
            ThemeCard {{
                background-color: {bg};
                border: {sel_width}px solid {sel_border};
                border-radius: 10px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(3)

        name_lbl = QLabel(theme_data["name"])
        name_lbl.setStyleSheet(f"color: {fg}; font-size: 13px; font-weight: bold; background: transparent; border: none;")

        day_lbl = QLabel("WEDNESDAY")
        day_lbl.setStyleSheet(f"color: {fg}; font-size: 16px; font-weight: bold; letter-spacing: 3px; background: transparent; border: none;")

        date_lbl = QLabel("12 MAR 2026")
        date_lbl.setStyleSheet(f"color: {dim}; font-size: 9px; letter-spacing: 2px; background: transparent; border: none;")

        time_lbl = QLabel("10 : 30 PM")
        time_lbl.setStyleSheet(f"color: {accent}; font-size: 10px; letter-spacing: 2px; background: transparent; border: none;")

        layout.addWidget(name_lbl)
        layout.addSpacing(2)
        layout.addWidget(day_lbl)
        layout.addWidget(date_lbl)
        layout.addWidget(time_lbl)
        layout.addStretch()

    def mousePressEvent(self, event):
        self.clicked.emit(self.theme_id)


class ThemePickerDialog(QDialog):
    theme_selected = Signal(str)

    def __init__(self, current_theme, parent=None):
        super().__init__(parent)
        from themes import THEMES
        self._themes = THEMES
        self.setWindowTitle("Theme Picker")
        self.setMinimumSize(580, 500)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setStyleSheet(DIALOG_STYLE)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 16, 20, 16)
        main_layout.setSpacing(8)

        heading = QLabel("🎨  Choose a Theme")
        heading.setObjectName("heading")
        main_layout.addWidget(heading)

        subhead = QLabel(f"{len(THEMES)} themes available  ·  Click to apply")
        subhead.setObjectName("subhead")
        main_layout.addWidget(subhead)

        self.search = QLineEdit()
        self.search.setObjectName("searchBox")
        self.search.setPlaceholderText("Search themes...")
        self.search.textChanged.connect(self._filter)
        main_layout.addWidget(self.search)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet(SCROLLBAR_STYLE)
        main_layout.addWidget(self.scroll)

        self._current = current_theme
        self._cards = []
        self._build_grid()

    def _build_grid(self, filter_text=""):
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        grid = QGridLayout(container)
        grid.setSpacing(12)
        grid.setContentsMargins(4, 4, 4, 4)

        self._cards = []
        col, cols = 0, 3
        row = 0
        for tid, tdata in self._themes.items():
            if filter_text and filter_text.lower() not in tdata["name"].lower():
                continue
            card = ThemeCard(tid, tdata, is_selected=(tid == self._current))
            card.clicked.connect(self._on_clicked)
            grid.addWidget(card, row, col)
            self._cards.append(card)
            col += 1
            if col >= cols:
                col = 0
                row += 1

        self.scroll.setWidget(container)

    def _filter(self, text):
        self._build_grid(text)

    def _on_clicked(self, theme_id):
        self.theme_selected.emit(theme_id)
        self.accept()


# ══════════════════════════════════════════════════════════════════════
#  FONT PICKER
# ══════════════════════════════════════════════════════════════════════

class FontCard(QFrame):
    clicked = Signal(str)

    def __init__(self, font_name, is_selected=False, parent=None):
        super().__init__(parent)
        self.font_name = font_name
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(64)
        self.setMinimumWidth(250)

        border_col = "#A8F0D0" if is_selected else "#333"
        bg = "#2a2a2a" if is_selected else "#222"

        self.setStyleSheet(f"""
            FontCard {{
                background-color: {bg};
                border: 2px solid {border_col};
                border-radius: 8px;
            }}
            FontCard:hover {{
                background-color: #303030;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 8, 14, 8)
        layout.setSpacing(2)

        name = QLabel(font_name)
        name.setStyleSheet(f"color: #888; font-size: 10px; background: transparent; border: none;")

        sample = QLabel("The quick brown fox jumps — 0123456789")
        sample.setStyleSheet(f'color: #e0e0e0; font-family: "{font_name}"; font-size: 16px; background: transparent; border: none;')

        layout.addWidget(name)
        layout.addWidget(sample)

    def mousePressEvent(self, event):
        self.clicked.emit(self.font_name)


class FontPickerDialog(QDialog):
    font_selected = Signal(str)

    def __init__(self, current_font, fonts_list, parent=None):
        super().__init__(parent)
        self._fonts = fonts_list
        self._current = current_font
        self.setWindowTitle("Font Picker")
        self.setMinimumSize(540, 500)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setStyleSheet(DIALOG_STYLE)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 16, 20, 16)
        main_layout.setSpacing(8)

        heading = QLabel("🔤  Choose a Font")
        heading.setObjectName("heading")
        main_layout.addWidget(heading)

        subhead = QLabel(f"{len(fonts_list)} fonts available  ·  Click to apply")
        subhead.setObjectName("subhead")
        main_layout.addWidget(subhead)

        self.search = QLineEdit()
        self.search.setObjectName("searchBox")
        self.search.setPlaceholderText("Search fonts...")
        self.search.textChanged.connect(self._filter)
        main_layout.addWidget(self.search)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet(SCROLLBAR_STYLE)
        main_layout.addWidget(self.scroll)

        self._build_list()

    def _build_list(self, filter_text=""):
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(container)
        layout.setSpacing(6)
        layout.setContentsMargins(4, 4, 4, 4)

        for fname in self._fonts:
            if filter_text and filter_text.lower() not in fname.lower():
                continue
            card = FontCard(fname, is_selected=(fname == self._current))
            card.clicked.connect(self._on_clicked)
            layout.addWidget(card)

        layout.addStretch()
        self.scroll.setWidget(container)

    def _filter(self, text):
        self._build_list(text)

    def _on_clicked(self, font_name):
        self.font_selected.emit(font_name)
        self.accept()


# ══════════════════════════════════════════════════════════════════════
#  DATETIME TEMPLATE PICKER
# ══════════════════════════════════════════════════════════════════════

# Template definitions — each describes how the DateTimeWidget looks
DATETIME_TEMPLATES = {

    "rainmeter_modern": {
        "name": "Modern Rain",
        "desc": "Sleek combination of numbers and text",
        "day_fmt": "dddd",
        "date_fmt": "MMM d",
        "time_fmt": "h:mm",
        "day_transform": "upper",
        "date_transform": "upper",
        "time_prefix": "",
        "time_suffix": "",
        "show_seconds": False,
        "show_ampm": True,
        "layout": "time_top",
    },
    "rainmeter_sidebar": {
        "name": "Sidebar Stack",
        "desc": "All elements stacked neatly",
        "day_fmt": "ddd",
        "date_fmt": "d / M / yyyy",
        "time_fmt": "h:mm:ss a",
        "day_transform": "none",
        "date_transform": "none",
        "time_prefix": "",
        "time_suffix": "",
        "show_seconds": True,
        "show_ampm": False,
        "layout": "vertical",
    },
    "cyberpunk": {
        "name": "Cyberpunk",
        "desc": "Glitchy styled dense data",
        "day_fmt": "ddd",
        "date_fmt": "yyyy-MM-dd",
        "time_fmt": "HH:mm:ss",
        "day_transform": "upper",
        "date_transform": "none",
        "time_prefix": "[ ",
        "time_suffix": " ]",
        "show_seconds": True,
        "show_ampm": False,
        "layout": "time_top",
    },

    "classic": {
        "name": "Classic",
        "desc": "Big day name, date below, time accent",
        "day_fmt": "dddd",
        "date_fmt": "d  MMMM,  yyyy.",
        "time_fmt": "h:mm",
        "day_transform": "upper",
        "date_transform": "upper",
        "time_prefix": "- ",
        "time_suffix": " -",
        "show_seconds": False,
        "show_ampm": True,
        "layout": "vertical",
    },
    "minimal": {
        "name": "Minimal",
        "desc": "Clean time-focused, small date",
        "day_fmt": "",
        "date_fmt": "ddd, MMM d",
        "time_fmt": "h:mm",
        "day_transform": "upper",
        "date_transform": "upper",
        "time_prefix": "",
        "time_suffix": "",
        "show_seconds": True,
        "show_ampm": True,
        "layout": "time_top",
    },
    "elegant": {
        "name": "Elegant",
        "desc": "Title-case day, spelled out date, 12h",
        "day_fmt": "dddd",
        "date_fmt": "MMMM d, yyyy",
        "time_fmt": "h:mm",
        "day_transform": "title",
        "date_transform": "none",
        "time_prefix": "",
        "time_suffix": "",
        "show_seconds": False,
        "show_ampm": True,
        "layout": "vertical",
    },
    "digital": {
        "name": "Digital",
        "desc": "Bold digital clock with date strip",
        "day_fmt": "ddd",
        "date_fmt": "dd/MM/yyyy",
        "time_fmt": "h:mm:ss",
        "day_transform": "upper",
        "date_transform": "none",
        "time_prefix": "",
        "time_suffix": "",
        "show_seconds": True,
        "show_ampm": True,
        "layout": "time_top",
    },
    "retro": {
        "name": "Retro",
        "desc": "Spaced letters, vintage feel",
        "day_fmt": "dddd",
        "date_fmt": "d . M M . yyyy",
        "time_fmt": "HH : mm",
        "day_transform": "spaced",
        "date_transform": "none",
        "time_prefix": "[ ",
        "time_suffix": " ]",
        "show_seconds": False,
        "show_ampm": True,
        "layout": "vertical",
    },
    "ampm_big": {
        "name": "AM/PM Big",
        "desc": "Large 12-hour time with AM/PM badge",
        "day_fmt": "dddd",
        "date_fmt": "MMMM d",
        "time_fmt": "h:mm",
        "day_transform": "upper",
        "date_transform": "upper",
        "time_prefix": "",
        "time_suffix": "",
        "show_seconds": False,
        "show_ampm": True,
        "layout": "time_top",
    },
    "iso": {
        "name": "ISO",
        "desc": "Developer-style ISO date, 24h",
        "day_fmt": "",
        "date_fmt": "yyyy-MM-dd",
        "time_fmt": "h:mm:ss",
        "day_transform": "none",
        "date_transform": "none",
        "time_prefix": "T",
        "time_suffix": "",
        "show_seconds": True,
        "show_ampm": True,
        "layout": "time_top",
    },
    "compact": {
        "name": "Compact",
        "desc": "Single-line date + time, tiny footprint",
        "day_fmt": "ddd",
        "date_fmt": "d MMM",
        "time_fmt": "h:mm",
        "day_transform": "upper",
        "date_transform": "upper",
        "time_prefix": "",
        "time_suffix": "",
        "show_seconds": False,
        "show_ampm": True,
        "layout": "compact",
    },
    "typewriter": {
        "name": "Typewriter",
        "desc": "Monospaced look, underscores",
        "day_fmt": "dddd",
        "date_fmt": "dd_MM_yyyy",
        "time_fmt": "h:mm:ss",
        "day_transform": "upper",
        "date_transform": "none",
        "time_prefix": "> ",
        "time_suffix": "",
        "show_seconds": True,
        "show_ampm": True,
        "layout": "vertical",
    },
    "headline": {
        "name": "Headline",
        "desc": "News-style bold date above time",
        "day_fmt": "dddd",
        "date_fmt": "MMMM d, yyyy",
        "time_fmt": "h:mm",
        "day_transform": "upper",
        "date_transform": "upper",
        "time_prefix": "",
        "time_suffix": "",
        "show_seconds": False,
        "show_ampm": True,
        "layout": "vertical",
    },
    "dots": {
        "name": "Dots",
        "desc": "Dotted separators, playful",
        "day_fmt": "dddd",
        "date_fmt": "d · MMM · yyyy",
        "time_fmt": "h:mm",
        "day_transform": "upper",
        "date_transform": "upper",
        "time_prefix": "• ",
        "time_suffix": " •",
        "show_seconds": False,
        "show_ampm": True,
        "layout": "vertical",
    },
    "stacked": {
        "name": "Stacked",
        "desc": "Time huge, day and date small below",
        "day_fmt": "dddd",
        "date_fmt": "d MMMM yyyy",
        "time_fmt": "h:mm",
        "day_transform": "upper",
        "date_transform": "upper",
        "time_prefix": "",
        "time_suffix": "",
        "show_seconds": False,
        "show_ampm": True,
        "layout": "time_top",
    },
    "slashes": {
        "name": "Slashes",
        "desc": "Date with slashes, seconds visible",
        "day_fmt": "ddd",
        "date_fmt": "MM/dd/yyyy",
        "time_fmt": "h:mm:ss",
        "day_transform": "upper",
        "date_transform": "none",
        "time_prefix": "",
        "time_suffix": "",
        "show_seconds": True,
        "show_ampm": True,
        "layout": "time_top",
    },
    "poetic": {
        "name": "Poetic",
        "desc": "Soft title case, graceful",
        "day_fmt": "dddd",
        "date_fmt": "d MMMM, yyyy",
        "time_fmt": "h:mm",
        "day_transform": "title",
        "date_transform": "none",
        "time_prefix": "~ ",
        "time_suffix": " ~",
        "show_seconds": False,
        "show_ampm": True,
        "layout": "vertical",
    },
    "military": {
        "name": "Military",
        "desc": "24h Zulu time, terse format",
        "day_fmt": "ddd",
        "date_fmt": "dd MMM yyyy",
        "time_fmt": "h:mm",
        "day_transform": "upper",
        "date_transform": "upper",
        "time_prefix": "",
        "time_suffix": "H",
        "show_seconds": False,
        "show_ampm": True,
        "layout": "time_top",
    },
}


class TemplateCard(QFrame):
    clicked = Signal(str)

    def __init__(self, tmpl_id, tmpl_data, theme_colors, is_selected=False, parent=None):
        super().__init__(parent)
        self.tmpl_id = tmpl_id
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(250, 100)

        bg = theme_colors.get("bg", "rgba(0,105,62,235)")
        fg = theme_colors.get("fg", "#FFFFFF")
        accent = theme_colors.get("accent", "#A8F0D0")
        dim = theme_colors.get("dim", "rgba(255,255,255,120)")

        border_col = "#FFFFFF" if is_selected else "transparent"
        bw = 3 if is_selected else 0

        self.setStyleSheet(f"""
            TemplateCard {{
                background-color: {bg};
                border: {bw}px solid {border_col};
                border-radius: 10px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 8, 14, 8)
        layout.setSpacing(2)

        from PySide6.QtCore import QTime, QDate
        now_time = QTime(22, 30, 45)
        now_date = QDate(2026, 3, 12)

        # Build preview text
        t = tmpl_data
        day_text = now_date.toString(t["day_fmt"]) if t["day_fmt"] else ""
        date_text = now_date.toString(t["date_fmt"]) if t["date_fmt"] else ""
        time_text = now_time.toString(t["time_fmt"])

        if t["day_transform"] == "upper":
            day_text = day_text.upper()
        elif t["day_transform"] == "title":
            day_text = day_text.title()
        elif t["day_transform"] == "spaced":
            day_text = "  ".join(day_text.upper())
        if t["date_transform"] == "upper":
            date_text = date_text.upper()

        time_str = f"{t['time_prefix']}{time_text}{t['time_suffix']}"
        if t["show_ampm"]:
            time_str += " PM"

        name_lbl = QLabel(f"{tmpl_data['name']}  —  {tmpl_data['desc']}")
        name_lbl.setStyleSheet(f"color: {dim}; font-size: 9px; background: transparent; border: none;")

        if t["layout"] == "time_top":
            line1_text = time_str
            line2_text = f"{day_text} {date_text}".strip()
            l1 = QLabel(line1_text)
            l1.setStyleSheet(f"color: {fg}; font-size: 20px; font-weight: bold; background: transparent; border: none;")
            l1.setAlignment(Qt.AlignCenter)
            l2 = QLabel(line2_text)
            l2.setStyleSheet(f"color: {accent}; font-size: 10px; letter-spacing: 2px; background: transparent; border: none;")
            l2.setAlignment(Qt.AlignCenter)
            layout.addWidget(name_lbl)
            layout.addWidget(l1)
            layout.addWidget(l2)
        elif t["layout"] == "compact":
            line = f"{day_text}  {date_text}  {time_str}"
            l1 = QLabel(line)
            l1.setStyleSheet(f"color: {fg}; font-size: 14px; font-weight: bold; background: transparent; border: none;")
            l1.setAlignment(Qt.AlignCenter)
            layout.addWidget(name_lbl)
            layout.addStretch()
            layout.addWidget(l1)
            layout.addStretch()
        else:
            d = QLabel(day_text)
            d.setStyleSheet(f"color: {fg}; font-size: 16px; font-weight: bold; letter-spacing: 3px; background: transparent; border: none;")
            d.setAlignment(Qt.AlignCenter)
            dt = QLabel(date_text)
            dt.setStyleSheet(f"color: {dim}; font-size: 9px; letter-spacing: 2px; background: transparent; border: none;")
            dt.setAlignment(Qt.AlignCenter)
            tm = QLabel(time_str)
            tm.setStyleSheet(f"color: {accent}; font-size: 10px; letter-spacing: 2px; background: transparent; border: none;")
            tm.setAlignment(Qt.AlignCenter)
            layout.addWidget(name_lbl)
            if day_text:
                layout.addWidget(d)
            layout.addWidget(dt)
            layout.addWidget(tm)

        layout.addStretch()

    def mousePressEvent(self, event):
        self.clicked.emit(self.tmpl_id)


class TemplatePickerDialog(QDialog):
    template_selected = Signal(str)

    def __init__(self, current_template, theme_colors, parent=None):
        super().__init__(parent)
        self._current = current_template
        self._theme_colors = theme_colors
        self.setWindowTitle("DateTime Template")
        self.setMinimumSize(560, 480)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setStyleSheet(DIALOG_STYLE)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 16, 20, 16)
        main_layout.setSpacing(8)

        heading = QLabel("🕐  DateTime Template")
        heading.setObjectName("heading")
        main_layout.addWidget(heading)

        subhead = QLabel(f"{len(DATETIME_TEMPLATES)} designs  ·  Click to apply")
        subhead.setObjectName("subhead")
        main_layout.addWidget(subhead)

        main_layout.addSpacing(4)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet(SCROLLBAR_STYLE)

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        grid = QGridLayout(container)
        grid.setSpacing(12)
        grid.setContentsMargins(4, 4, 4, 4)

        cols = 2
        for i, (tid, tdata) in enumerate(DATETIME_TEMPLATES.items()):
            card = TemplateCard(tid, tdata, theme_colors, is_selected=(tid == current_template))
            card.clicked.connect(self._on_clicked)
            grid.addWidget(card, i // cols, i % cols)

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def _on_clicked(self, tmpl_id):
        self.template_selected.emit(tmpl_id)
        self.accept()


# ══════════════════════════════════════════════════════════════════════
#  CUSTOM COLOR PICKER
# ══════════════════════════════════════════════════════════════════════

class _ColorButton(QPushButton):
    """Small colored square button that opens a QColorDialog."""
    color_changed = Signal(str, str)  # key, hex_color

    def __init__(self, key, label, current_hex, parent=None):
        super().__init__(parent)
        self.key = key
        self._color = current_hex
        self.setFixedSize(36, 36)
        self.setCursor(Qt.PointingHandCursor)
        self._update_style()
        self.setToolTip(label)
        self.clicked.connect(self._pick)

    def _update_style(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self._color};
                border: 2px solid #555;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                border: 2px solid #fff;
            }}
        """)

    def _pick(self):
        c = QColorDialog.getColor(QColor(self._color), self.parent(), f"Pick {self.key}")
        if c.isValid():
            self._color = c.name()
            self._update_style()
            self.color_changed.emit(self.key, self._color)


class ColorPickerDialog(QDialog):
    colors_changed = Signal(dict)  # {"fg": "#xxx", "accent": "#xxx", ...}

    def __init__(self, current_custom=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Custom Colors")
        self.setMinimumSize(380, 320)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setStyleSheet(DIALOG_STYLE)

        self._colors = dict(current_custom) if current_custom else {}

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 16, 20, 16)
        main_layout.setSpacing(12)

        heading = QLabel("🎯  Custom Colors")
        heading.setObjectName("heading")
        main_layout.addWidget(heading)

        subhead = QLabel("Override theme colors  ·  Click a swatch to change")
        subhead.setObjectName("subhead")
        main_layout.addWidget(subhead)

        main_layout.addSpacing(4)

        color_keys = [
            ("fg", "Text Color", "#FFFFFF"),
            ("accent", "Accent Color", "#A8F0D0"),
            ("bg", "Background", "rgba(0,105,62,235)"),
        ]

        for key, label, default in color_keys:
            row = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setStyleSheet("color: #ccc; font-size: 13px; background: transparent;")
            lbl.setFixedWidth(140)

            current = self._colors.get(key, default)
            btn = _ColorButton(key, label, current, self)
            btn.color_changed.connect(self._on_color_changed)

            hex_lbl = QLabel(current)
            hex_lbl.setObjectName(f"hex_{key}")
            hex_lbl.setStyleSheet("color: #888; font-size: 11px; font-family: 'Consolas'; background: transparent;")

            row.addWidget(lbl)
            row.addWidget(btn)
            row.addSpacing(8)
            row.addWidget(hex_lbl)
            row.addStretch()
            main_layout.addLayout(row)

        main_layout.addSpacing(12)

        btn_row = QHBoxLayout()
        apply_btn = QPushButton("Apply")
        apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #00693E; color: white; border: none;
                border-radius: 6px; padding: 8px 24px; font-size: 13px;
            }
            QPushButton:hover { background-color: #008050; }
        """)
        apply_btn.clicked.connect(self._apply)

        reset_btn = QPushButton("Reset to Theme")
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #333; color: #ccc; border: 1px solid #555;
                border-radius: 6px; padding: 8px 24px; font-size: 13px;
            }
            QPushButton:hover { background-color: #444; }
        """)
        reset_btn.clicked.connect(self._reset)

        btn_row.addWidget(reset_btn)
        btn_row.addWidget(apply_btn)
        main_layout.addLayout(btn_row)

        main_layout.addStretch()

    def _on_color_changed(self, key, hex_color):
        self._colors[key] = hex_color
        lbl = self.findChild(QLabel, f"hex_{key}")
        if lbl:
            lbl.setText(hex_color)

    def _apply(self):
        self.colors_changed.emit(dict(self._colors))
        self.accept()

    def _reset(self):
        self.colors_changed.emit({})
        self.accept()


# ══════════════════════════════════════════════════════════════════════
#  WIDGET STYLE TEMPLATES (per-widget customization)
# ══════════════════════════════════════════════════════════════════════

WIDGET_STYLES = {
    "clock": {
        "classic": {"name": "Classic", "desc": "24-hour with seconds below", "fmt": "HH:mm", "sec_fmt": ":ss", "show_sec": True, "ampm": False},
        "digital": {"name": "Digital", "desc": "24-hour with seconds inline", "fmt": "HH:mm:ss", "sec_fmt": "", "show_sec": False, "ampm": False},
        "twelve": {"name": "12-Hour", "desc": "12-hour with AM/PM", "fmt": "h:mm", "sec_fmt": " AP", "show_sec": True, "ampm": True},
        "minimal": {"name": "Minimal", "desc": "Just hours and minutes", "fmt": "HH:mm", "sec_fmt": "", "show_sec": False, "ampm": False},
        "dots": {"name": "Dots", "desc": "Dotted separator style", "fmt": "HH · mm", "sec_fmt": "", "show_sec": False, "ampm": False},
    },
    "system": {
        "default": {"name": "Default", "desc": "CPU, RAM, Disk with bars", "show_disk": True, "show_bars": True, "title": "S Y S T E M"},
        "compact": {"name": "Compact", "desc": "CPU and RAM only", "show_disk": False, "show_bars": True, "title": "S Y S T E M"},
        "minimal": {"name": "Minimal", "desc": "Percentages, no bars", "show_disk": True, "show_bars": False, "title": "S Y S T E M"},
        "monitor": {"name": "Monitor", "desc": "Full stats, all bars", "show_disk": True, "show_bars": True, "title": "⚡  S Y S T E M"},
    },
    "stopwatch": {
        "default": {"name": "Default", "desc": "MM:SS with .ms below", "show_ms": True, "title": "S T O P W A T C H"},
        "clean": {"name": "Clean", "desc": "MM:SS only, no ms", "show_ms": False, "title": "S T O P W A T C H"},
        "timer": {"name": "Timer", "desc": "With TIMER title", "show_ms": True, "title": "⏱  T I M E R"},
    },
    "quotes": {
        "default": {"name": "Default", "desc": "Bird icon with italic quote", "icon": "🕊", "show_icon": True, "italic": True},
        "minimal": {"name": "Minimal", "desc": "No icon, clean look", "icon": "", "show_icon": False, "italic": True},
        "elegant": {"name": "Elegant", "desc": "Sparkle icon, italic", "icon": "✨", "show_icon": True, "italic": True},
        "bold": {"name": "Bold", "desc": "Fire icon, strong text", "icon": "🔥", "show_icon": True, "italic": False},
        "zen": {"name": "Zen", "desc": "Lotus flower, peaceful", "icon": "🪷", "show_icon": True, "italic": True},
        "star": {"name": "Star", "desc": "Star icon, bright feel", "icon": "⭐", "show_icon": True, "italic": True},
    },
    "calendar": {
        "default": {"name": "Default", "desc": "Full month grid, MO start", "title_fmt": "%B  %Y", "title_transform": "upper", "week_start": 0},
        "minimal": {"name": "Minimal", "desc": "Short month name", "title_fmt": "%b %Y", "title_transform": "upper", "week_start": 0},
        "sunday": {"name": "Sunday Start", "desc": "Week starts on Sunday", "title_fmt": "%B  %Y", "title_transform": "upper", "week_start": 6},
        "elegant": {"name": "Elegant", "desc": "Title case month name", "title_fmt": "%B %Y", "title_transform": "title", "week_start": 0},
    },
    "countdown": {
        "default": {"name": "Default", "desc": "Big number + DAYS REMAINING", "unit": "days", "sub_text": "D A Y S   R E M A I N I N G"},
        "weeks": {"name": "Weeks", "desc": "Show in weeks + days", "unit": "weeks", "sub_text": ""},
        "detailed": {"name": "Detailed", "desc": "Months, weeks, and days", "unit": "detailed", "sub_text": ""},
    },
    "battery": {
        "default": {"name": "Default", "desc": "Big %, bar, and status", "show_bar": True, "title": "B A T T E R Y"},
        "minimal": {"name": "Minimal", "desc": "Just percentage + status", "show_bar": False, "title": "B A T T E R Y"},
        "power": {"name": "Power", "desc": "With power icon in title", "show_bar": True, "title": "🔋  B A T T E R Y"},
    },
    "uptime": {
        "default": {"name": "Default", "desc": "Hours + minutes, since time", "fmt": "short", "title": "U P T I M E"},
        "detailed": {"name": "Detailed", "desc": "Days, hours, minutes, seconds", "fmt": "full", "title": "U P T I M E"},
        "compact": {"name": "Compact", "desc": "Just hours and minutes", "fmt": "compact", "title": "U P T I M E"},
    },
    "network": {
        "default": {"name": "Default", "desc": "Up/Down speeds + total", "show_total": True, "title": "N E T W O R K"},
        "speed": {"name": "Speed Only", "desc": "Just upload/download", "show_total": False, "title": "N E T W O R K"},
        "globe": {"name": "Globe", "desc": "With globe icon", "show_total": True, "title": "🌐  N E T W O R K"},
    },
    "notes": {
        "default": {"name": "Default", "desc": "Centered title + text area", "title": "N O T E S", "show_title": True},
        "clean": {"name": "Clean", "desc": "No title, just text", "title": "", "show_title": False},
        "journal": {"name": "Journal", "desc": "With journal icon", "title": "📝  N O T E S", "show_title": True},
    },
    "greeting": {
        "default": {"name": "Default", "desc": "Good Morning + date + time", "fmt": "standard", "time_fmt": "h:mm AP"},
        "casual": {"name": "Casual", "desc": "Hey there! + time", "fmt": "casual", "time_fmt": "h:mm AP"},
        "formal": {"name": "Formal", "desc": "Full formal greeting", "fmt": "formal", "time_fmt": "h:mm"},
        "wave": {"name": "Wave", "desc": "Wave emoji greeting", "fmt": "wave", "time_fmt": "h:mm AP"},
    },
    "worldclock": {
        "default": {"name": "Default", "desc": "City name + 24h time", "time_fmt": "%H:%M", "title": "W O R L D   C L O C K"},
        "twelve": {"name": "12-Hour", "desc": "City name + 12h AM/PM", "time_fmt": "%I:%M %p", "title": "W O R L D   C L O C K"},
        "globe": {"name": "Globe", "desc": "Globe icon in title", "time_fmt": "%H:%M", "title": "🌍  W O R L D   C L O C K"},
    },
    "dayprogress": {
        "default": {"name": "Default", "desc": "Big %, bar, remaining time", "show_bar": True, "show_remaining": True, "title": "D A Y   P R O G R E S S"},
        "minimal": {"name": "Minimal", "desc": "Just percentage + bar", "show_bar": True, "show_remaining": False, "title": "D A Y   P R O G R E S S"},
        "text": {"name": "Text Only", "desc": "Percentage + remaining, no bar", "show_bar": False, "show_remaining": True, "title": "D A Y   P R O G R E S S"},
    },
    "spotify": {
        "default": {"name": "Default", "desc": "Album art + info + controls", "show_art": True, "show_controls": True},
        "compact": {"name": "Compact", "desc": "No album art, just info + controls", "show_art": False, "show_controls": True},
        "display": {"name": "Display", "desc": "Album art + info, no controls", "show_art": True, "show_controls": False},
    },
}


# ── Generic preview label builder for style cards ──

def _style_preview_lines(widget_id, style_data):
    """Return a list of (text, role) for the style card preview."""
    if widget_id == "clock":
        return [("12:30", "big"), (style_data.get("sec_fmt", ":45") or "", "accent")]
    elif widget_id == "system":
        return [("CPU 23%", "medium"), ("RAM 4.2 / 16 GB", "medium")]
    elif widget_id == "stopwatch":
        return [("03:42", "big"), (".87" if style_data.get("show_ms") else "", "accent")]
    elif widget_id == "quotes":
        icon = style_data.get("icon", "🕊")
        return [(icon, "icon"), ('"Stay hungry..."', "medium"), ("— Steve Jobs", "dim")]
    elif widget_id == "calendar":
        return [("MARCH  2026", "title"), ("MO TU WE TH FR", "dim")]
    elif widget_id == "countdown":
        return [("294", "big"), (style_data.get("sub_text", "") or "until target", "dim")]
    elif widget_id == "battery":
        return [("78%", "big"), ("⚡ Charging", "dim")]
    elif widget_id == "uptime":
        return [("11h 22m", "big"), ("since 10:53", "dim")]
    elif widget_id == "network":
        return [("↑ 12 KB/s", "accent"), ("↓ 340 KB/s", "medium")]
    elif widget_id == "notes":
        return [("Type your notes...", "dim")]
    elif widget_id == "greeting":
        return [("Good Morning", "big"), ("THURSDAY, MARCH 12", "dim")]
    elif widget_id == "worldclock":
        return [("NEW YORK  05:30", "accent"), ("TOKYO  19:30", "accent")]
    elif widget_id == "dayprogress":
        return [("58.3%", "big"), ("10h 2m remaining", "dim")]
    elif widget_id == "spotify":
        return [("🎵 Song Title", "medium"), ("Artist Name", "dim")]
    return [("Preview", "medium")]


class WidgetStyleCard(QFrame):
    clicked = Signal(str)

    def __init__(self, style_id, style_data, widget_id, theme_colors, is_selected=False, parent=None):
        super().__init__(parent)
        self.style_id = style_id
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(220, 110)

        bg = theme_colors.get("bg", "rgba(0,105,62,235)")
        fg = theme_colors.get("fg", "#FFFFFF")
        accent = theme_colors.get("accent", "#A8F0D0")
        dim = theme_colors.get("dim", "rgba(255,255,255,120)")

        border_col = "#FFFFFF" if is_selected else "transparent"
        bw = 3 if is_selected else 0

        self.setStyleSheet(f"""
            WidgetStyleCard {{
                background-color: {bg};
                border: {bw}px solid {border_col};
                border-radius: 10px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 8, 14, 8)
        layout.setSpacing(2)

        name_lbl = QLabel(f"{style_data['name']}  —  {style_data['desc']}")
        name_lbl.setStyleSheet(f"color: {dim}; font-size: 9px; background: transparent; border: none;")
        name_lbl.setWordWrap(True)
        layout.addWidget(name_lbl)

        color_map = {"big": fg, "medium": fg, "accent": accent, "dim": dim, "title": accent, "icon": fg}
        size_map = {"big": 18, "medium": 12, "accent": 12, "dim": 10, "title": 10, "icon": 20}

        for text, role in _style_preview_lines(widget_id, style_data):
            if not text:
                continue
            lbl = QLabel(text)
            c = color_map.get(role, fg)
            sz = size_map.get(role, 12)
            bold = "font-weight: bold;" if role in ("big", "title") else ""
            italic = "font-style: italic;" if role == "medium" and widget_id == "quotes" and style_data.get("italic") else ""
            lbl.setStyleSheet(f"color: {c}; font-size: {sz}px; {bold} {italic} background: transparent; border: none;")
            lbl.setAlignment(Qt.AlignCenter)
            layout.addWidget(lbl)

        layout.addStretch()

    def mousePressEvent(self, event):
        self.clicked.emit(self.style_id)


class WidgetStylePickerDialog(QDialog):
    style_selected = Signal(str)

    def __init__(self, widget_id, current_style, theme_colors, parent=None):
        super().__init__(parent)
        self._widget_id = widget_id
        self._current = current_style

        styles = WIDGET_STYLES.get(widget_id, {})
        nice_name = widget_id.replace("dayprogress", "Day Progress").replace("worldclock", "World Clock").capitalize()

        self.setWindowTitle(f"{nice_name} Style")
        self.setMinimumSize(500, 400)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setStyleSheet(DIALOG_STYLE)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 16, 20, 16)
        main_layout.setSpacing(8)

        heading = QLabel(f"🎨  {nice_name} Style")
        heading.setObjectName("heading")
        main_layout.addWidget(heading)

        subhead = QLabel(f"{len(styles)} styles  ·  Click to apply")
        subhead.setObjectName("subhead")
        main_layout.addWidget(subhead)

        main_layout.addSpacing(4)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet(SCROLLBAR_STYLE)

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        grid = QGridLayout(container)
        grid.setSpacing(12)
        grid.setContentsMargins(4, 4, 4, 4)

        cols = 2
        for i, (sid, sdata) in enumerate(styles.items()):
            card = WidgetStyleCard(sid, sdata, widget_id, theme_colors, is_selected=(sid == current_style))
            card.clicked.connect(self._on_clicked)
            grid.addWidget(card, i // cols, i % cols)

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def _on_clicked(self, style_id):
        self.style_selected.emit(style_id)
        self.accept()
