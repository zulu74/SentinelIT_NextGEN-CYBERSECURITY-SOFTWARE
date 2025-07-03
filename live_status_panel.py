from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QFrame
from PyQt5.QtCore import Qt, QTimer
from sentinelIT import sentinel_hub

class StatusPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SentinelIT - Module Monitor")
        self.layout = QVBoxLayout()
        self.status_labels = {}

        self.setStyleSheet("""
            QLabel { font-size: 14px; }
            QPushButton { padding: 6px; }
        """)

        # Title
        title = QLabel("🟢 SentinelIT Module Status")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.layout.addWidget(title)

        # Dynamic status rows
        for module_name in sentinel_hub.MODULE_REGISTRY.keys():
            row = QHBoxLayout()
            label = QLabel(f"{module_name}")
            status = QLabel("Loading...")
            self.status_labels[module_name] = status

            row.addWidget(label)
            row.addStretch()
            row.addWidget(status)
            self.layout.addLayout(row)

        # Separator + Controls
        self.layout.addWidget(self._hrule())

        control_row = QHBoxLayout()
        start_btn = QPushButton("Start All Modules")
        start_btn.clicked.connect(sentinel_hub.start_all)
        control_row.addStretch()
        control_row.addWidget(start_btn)
        control_row.addStretch()

        self.layout.addLayout(control_row)

        self.setLayout(self.layout)

        # Timer to refresh module statuses
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_status)
        self.timer.start(3000)  # every 3 seconds

        self.refresh_status()

    def refresh_status(self):
        statuses = sentinel_hub.get_status()
        for module, label in self.status_labels.items():
            status = statuses.get(module, "Unknown")
            color = "green" if "Running" in status else "red" if "Failed" in status else "orange"
            label.setText(status)
            label.setStyleSheet(f"color: {color}; font-weight: bold;")

    def _hrule(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("margin-top: 10px; margin-bottom: 10px;")
        return line