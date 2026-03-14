import re

with open("widgets.py", "r", encoding="utf-8") as f:
    text = f.read()

system_widget_init = """    def __init__(self, config):
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
        self._resize_for_scale()"""

system_widget_init_new = """    def __init__(self, config):
        super().__init__("system", config)
        self.title = QLabel("S Y S T E M")
        self.title.setObjectName("title")
        self.title.setAlignment(Qt.AlignCenter)
        
        # CPU
        self.cpu_label = QLabel()
        self.cpu_label.setObjectName("accent")
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setTextVisible(False)
        self.cpu_bar.setRange(0, 100)
        self.cpu_bar.setFixedHeight(8)
        
        # RAM
        self.ram_label = QLabel()
        self.ram_label.setObjectName("medium")
        self.ram_bar = QProgressBar()
        self.ram_bar.setTextVisible(False)
        self.ram_bar.setRange(0, 100)
        self.ram_bar.setFixedHeight(8)

        # DISK
        self.disk_label = QLabel()
        self.disk_label.setObjectName("dim")
        self.disk_bar = QProgressBar()
        self.disk_bar.setTextVisible(False)
        self.disk_bar.setRange(0, 100)
        self.disk_bar.setFixedHeight(4)
        
        self.content_layout.addWidget(self.title)
        self.content_layout.setSpacing(6)
        
        # Layout them nicely in pairs
        for lbl, bar in [(self.cpu_label, self.cpu_bar), (self.ram_label, self.ram_bar), (self.disk_label, self.disk_bar)]:
            row = QWidget()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.addWidget(lbl)
            self.content_layout.addWidget(row)
            self.content_layout.addWidget(bar)
            
        self._prev = {"cpu": None, "ram": None, "disk": None}
        self._disk_tick = 0
        psutil.cpu_percent(interval=0)
        self._widget_ready = True
        self._resize_for_scale()"""

# We substitute the init for SystemWidget
if system_widget_init in text:
    text = text.replace(system_widget_init, system_widget_init_new)
else:
    print("Could not find SystemWidget.__init__ exact match to replace.")

with open("widgets.py", "w", encoding="utf-8") as f:
    f.write(text)
