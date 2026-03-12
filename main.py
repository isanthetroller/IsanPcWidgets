import sys
import os
import signal
import gc

signal.signal(signal.SIGINT, signal.SIG_DFL)

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from config import load_config, save_config
from widgets import WIDGET_CLASSES
from tray_manager import TrayManager


def main():
    # Set process to below-normal priority for minimal system impact
    try:
        import psutil
        proc = psutil.Process(os.getpid())
        proc.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    except Exception:
        pass

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    # Enable smooth font rendering globally
    font = app.font()
    font.setHintingPreference(QFont.PreferNoHinting)
    font.setStyleStrategy(QFont.PreferAntialias)
    app.setFont(font)

    config = load_config()

    # Create all widgets from registry
    widgets = {}
    for wid, cls in WIDGET_CLASSES.items():
        widgets[wid] = cls(config)

    # Show only enabled widgets
    for wid, widget in widgets.items():
        if config.get("widgets", {}).get(wid, {}).get("enabled", False):
            widget.show()

    def do_save():
        save_config(config)

    def refresh_all():
        """Reapply theme/font/size/bg to every widget."""
        for w in widgets.values():
            w.apply_theme()

    tray = TrayManager(app, config, widgets, do_save, refresh_all)
    app.aboutToQuit.connect(do_save)

    gc.collect()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
