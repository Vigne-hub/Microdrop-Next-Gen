# frontend_plugins/dropbot_test_GUI.py
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel
from envisage.api import Plugin
from refrac_qt_microdrop.control_plugins.event_hub import EventHubPlugin


class MainWindow(QMainWindow):
    def __init__(self, event_hub):
        super().__init__()
        self.event_hub = event_hub
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Controller Test GUI")
        self.setGeometry(100, 100, 600, 400)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        # Dropbot Controls
        self.status_label_dropbot = QLabel("Dropbot Status: Ready", self)
        layout.addWidget(self.status_label_dropbot)

        init_btn = QPushButton("Initialize Dropbot", self)
        init_btn.clicked.connect(lambda: self.event_hub.init_dropbot(self.update_status_dropbot))
        layout.addWidget(init_btn)

        voltage_btn = QPushButton("Set Voltage to 10", self)
        voltage_btn.clicked.connect(lambda: self.event_hub.set_voltage(10, self.update_status_dropbot))
        layout.addWidget(voltage_btn)

        frequency_btn = QPushButton("Set Frequency to 10000", self)
        frequency_btn.clicked.connect(lambda: self.event_hub.set_frequency(10000, self.update_status_dropbot))
        layout.addWidget(frequency_btn)

        hv_btn = QPushButton("Enable High Voltage", self)
        hv_btn.clicked.connect(lambda: self.event_hub.set_hv(True, self.update_status_dropbot))
        layout.addWidget(hv_btn)

        channels_btn = QPushButton("Get Channels", self)
        channels_btn.clicked.connect(lambda: self.event_hub.get_channels(self.update_status_dropbot))
        layout.addWidget(channels_btn)

        central_widget.setLayout(layout)

    def update_status_dropbot(self, status):
        self.status_label_dropbot.setText(status)


class GUIPlugin(Plugin):
    id = 'refrac_qt_microdrop.gui_plugin'

    def start(self):
        super().start()
        event_hub = self.application.get_service(EventHubPlugin)
        self.window = MainWindow(event_hub)
        self.window.show()
