from PySide6.QtWidgets import (
    QSystemTrayIcon, QMenu, QWidgetAction, QWidget,
    QHBoxLayout, QLabel, QSlider,
)
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtCore import Qt
from themes import THEMES
from config import FONTS
from pickers import ThemePickerDialog, FontPickerDialog, TemplatePickerDialog, ColorPickerDialog, DATETIME_TEMPLATES


def _create_icon():
    px = QPixmap(32, 32)
    px.fill(Qt.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.Antialiasing)
    p.setBrush(QColor("#00693E"))
    p.setPen(Qt.NoPen)
    p.drawRoundedRect(2, 2, 28, 28, 6, 6)
    p.setBrush(QColor("#A8F0D0"))
    p.drawRoundedRect(8, 8, 16, 16, 3, 3)
    p.end()
    return QIcon(px)


MENU_STYLE = """
    QMenu {
        background-color: #1e1e1e;
        color: #e0e0e0;
        border: 1px solid #333;
        padding: 4px;
    }
    QMenu::item {
        padding: 5px 24px 5px 16px;
    }
    QMenu::item:selected {
        background-color: #333;
    }
    QMenu::separator {
        height: 1px;
        background: #333;
        margin: 4px 8px;
    }
"""


class TrayManager:
    def __init__(self, app, config, widgets, save_fn, refresh_fn):
        self.app = app
        self.config = config
        self.widgets = widgets
        self.save_fn = save_fn
        self.refresh_fn = refresh_fn

        self.tray = QSystemTrayIcon(_create_icon(), app)
        self.tray.setToolTip("Desktop Widgets")

        self.menu = QMenu()
        self._build_menu()
        self.tray.setContextMenu(self.menu)
        self.tray.show()

    def _build_menu(self):
        self.menu.clear()
        self.menu.setStyleSheet(MENU_STYLE)

        # ── Widgets toggle ──
        header = self.menu.addAction("— Widgets —")
        header.setEnabled(False)
        for wid, widget in self.widgets.items():
            check = "✓" if widget.isVisible() else "○"
            action = self.menu.addAction(f"  {check}  {wid.capitalize()}")
            action.triggered.connect(self._make_toggle(wid))

        self.menu.addSeparator()

        # ── Per-widget size sliders ──
        size_menu = self.menu.addMenu("📐  Widget Sizes")
        size_menu.setStyleSheet(MENU_STYLE)
        for wid, widget in self.widgets.items():
            wc = self.config.get("widgets", {}).get(wid, {})
            current_scale = wc.get("scale", 1.0)
            pct = int(current_scale * 100)

            # Container widget for slider row
            row = QWidget()
            row.setStyleSheet("background: transparent;")
            lay = QHBoxLayout(row)
            lay.setContentsMargins(12, 4, 12, 4)

            lbl = QLabel(f"{wid.capitalize()}")
            lbl.setFixedWidth(80)
            lbl.setStyleSheet("color: #e0e0e0; font-size: 12px;")

            slider = QSlider(Qt.Horizontal)
            slider.setRange(40, 300)  # 0.4x to 3.0x
            slider.setValue(pct)
            slider.setFixedWidth(120)
            slider.setStyleSheet("""
                QSlider::groove:horizontal {
                    background: #444; height: 4px; border-radius: 2px;
                }
                QSlider::handle:horizontal {
                    background: #A8F0D0; width: 12px; height: 12px;
                    margin: -4px 0; border-radius: 6px;
                }
                QSlider::sub-page:horizontal {
                    background: #00693E; border-radius: 2px;
                }
            """)

            val_lbl = QLabel(f"{pct}%")
            val_lbl.setFixedWidth(40)
            val_lbl.setStyleSheet("color: #A8F0D0; font-size: 11px;")

            slider.valueChanged.connect(self._make_scale_handler(wid, val_lbl))

            lay.addWidget(lbl)
            lay.addWidget(slider)
            lay.addWidget(val_lbl)

            wa = QWidgetAction(size_menu)
            wa.setDefaultWidget(row)
            size_menu.addAction(wa)

        self.menu.addSeparator()

        # ── Theme picker ──
        current_theme = self.config.get("theme", "emerald")
        theme_name = THEMES.get(current_theme, {}).get("name", current_theme)
        theme_action = self.menu.addAction(f"🎨  Theme: {theme_name}")
        theme_action.triggered.connect(self._open_theme_picker)

        # ── Font picker ──
        current_font = self.config.get("font", "Bahnschrift")
        font_action = self.menu.addAction(f"🔤  Font: {current_font}")
        font_action.triggered.connect(self._open_font_picker)

        # ── Custom color picker ──
        has_custom = bool(self.config.get("custom_colors"))
        color_label = "🎯  Custom Colors" + ("  ●" if has_custom else "")
        color_action = self.menu.addAction(color_label)
        color_action.triggered.connect(self._open_color_picker)

        # ── DateTime template picker ──
        current_tmpl = self.config.get("widgets", {}).get("datetime", {}).get("template", "classic")
        tmpl_name = DATETIME_TEMPLATES.get(current_tmpl, {}).get("name", current_tmpl)
        tmpl_action = self.menu.addAction(f"🕐  DateTime Style: {tmpl_name}")
        tmpl_action.triggered.connect(self._open_template_picker)

        self.menu.addSeparator()

        # ── Background toggle ──
        no_bg = self.config.get("no_bg", False)
        bg_check = "✓" if no_bg else "○"
        bg_action = self.menu.addAction(f"  {bg_check}  Text Only (No Background)")
        bg_action.triggered.connect(self._toggle_bool("no_bg"))

        # ── Lock toggle ──
        locked = self.config.get("locked", False)
        lock_check = "🔒" if locked else "🔓"
        lock_action = self.menu.addAction(f"  {lock_check}  {'Locked' if locked else 'Unlocked'} (click to toggle)")
        lock_action.triggered.connect(self._toggle_bool("locked"))

        self.menu.addSeparator()

        auto = self.config.get("auto_start", False)
        check = "✓" if auto else "○"
        auto_action = self.menu.addAction(f"  {check}  Start with Windows")
        auto_action.triggered.connect(self._toggle_autostart)

        self.menu.addSeparator()
        exit_action = self.menu.addAction("✕  Exit")
        exit_action.triggered.connect(self._exit)

    def _make_scale_handler(self, wid, val_lbl):
        def handler(value):
            scale = value / 100.0
            val_lbl.setText(f"{value}%")
            self.config.setdefault("widgets", {}).setdefault(wid, {})
            self.config["widgets"][wid]["scale"] = round(scale, 2)
            w = self.widgets.get(wid)
            if w:
                w.apply_theme()
            self.save_fn()
        return handler

    def _make_toggle(self, wid):
        def toggle():
            w = self.widgets[wid]
            if w.isVisible():
                w.hide()
                self.config["widgets"][wid]["enabled"] = False
            else:
                w.show()
                self.config["widgets"][wid]["enabled"] = True
            self.save_fn()
            self._build_menu()
        return toggle

    def _make_setter(self, key, value):
        def setter():
            self.config[key] = value
            self.refresh_fn()
            self.save_fn()
            self._build_menu()
        return setter

    def _toggle_bool(self, key):
        def toggler():
            self.config[key] = not self.config.get(key, False)
            self.refresh_fn()
            self.save_fn()
            self._build_menu()
        return toggler

    def _open_theme_picker(self):
        current = self.config.get("theme", "emerald")
        dlg = ThemePickerDialog(current)
        dlg.theme_selected.connect(self._apply_theme_from_picker)
        dlg.exec()

    def _apply_theme_from_picker(self, theme_id):
        self.config["theme"] = theme_id
        self.refresh_fn()
        self.save_fn()
        self._build_menu()

    def _open_font_picker(self):
        current = self.config.get("font", "Bahnschrift")
        dlg = FontPickerDialog(current, FONTS)
        dlg.font_selected.connect(self._apply_font_from_picker)
        dlg.exec()

    def _apply_font_from_picker(self, font_name):
        self.config["font"] = font_name
        self.refresh_fn()
        self.save_fn()
        self._build_menu()

    def _open_color_picker(self):
        current = self.config.get("custom_colors") or {}
        dlg = ColorPickerDialog(current)
        dlg.colors_changed.connect(self._apply_custom_colors)
        dlg.exec()

    def _apply_custom_colors(self, colors):
        if colors:
            self.config["custom_colors"] = colors
        else:
            self.config.pop("custom_colors", None)
        self.refresh_fn()
        self.save_fn()
        self._build_menu()

    def _open_template_picker(self):
        current = self.config.get("widgets", {}).get("datetime", {}).get("template", "classic")
        theme_id = self.config.get("theme", "emerald")
        theme_colors = THEMES.get(theme_id, THEMES["emerald"])
        dlg = TemplatePickerDialog(current, theme_colors)
        dlg.template_selected.connect(self._apply_template)
        dlg.exec()

    def _apply_template(self, tmpl_id):
        self.config.setdefault("widgets", {}).setdefault("datetime", {})
        self.config["widgets"]["datetime"]["template"] = tmpl_id
        w = self.widgets.get("datetime")
        if w:
            w._cached_minute = -1  # force refresh
            w.apply_theme()
            w._update()
        self.save_fn()
        self._build_menu()

    def _toggle_autostart(self):
        from config import set_auto_start
        new_val = not self.config.get("auto_start", False)
        self.config["auto_start"] = new_val
        set_auto_start(new_val)
        self.save_fn()
        self._build_menu()

    def _exit(self):
        self.save_fn()
        self.tray.hide()
        self.app.quit()
