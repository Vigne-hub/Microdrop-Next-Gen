# frontend_plugins/dropbot_test_GUI.py
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt
from envisage.api import Plugin
from refrac_qt_microdrop.event_hub import EventHubPlugin


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

        # Electrode Controls
        self.status_label_electrode = QLabel("Electrode Status: Ready", self)
        layout.addWidget(self.status_label_electrode)

        toggle_all_off_btn = QPushButton("Toggle All Electrodes Off", self)
        toggle_all_off_btn.clicked.connect(lambda: self.event_hub.toggle_all_electrodes_off(self.update_status_electrode))
        layout.addWidget(toggle_all_off_btn)

        toggle_batch_btn = QPushButton("Toggle Batch Electrodes On", self)
        toggle_batch_btn.clicked.connect(lambda: self.event_hub.toggle_on_batch(["electrode1", "electrode2"], self.update_status_electrode))
        layout.addWidget(toggle_batch_btn)

        sync_states_btn = QPushButton("Sync Electrode States", self)
        sync_states_btn.clicked.connect(lambda: self.event_hub.sync_electrode_states([0, 1, 0, 1], self.update_status_electrode))
        layout.addWidget(sync_states_btn)

        sync_metastates_btn = QPushButton("Sync Electrode Metastates", self)
        sync_metastates_btn.clicked.connect(lambda: self.event_hub.sync_electrode_metastates(["state1", "state2"], self.update_status_electrode))
        layout.addWidget(sync_metastates_btn)

        check_range_btn = QPushButton("Check Electrode Range", self)
        check_range_btn.clicked.connect(lambda: self.event_hub.check_electrode_range(128, self.update_status_electrode))
        layout.addWidget(check_range_btn)

        central_widget.setLayout(layout)

    def update_status_dropbot(self, status):
        self.status_label_dropbot.setText(status)

    def update_status_electrode(self, status):
        self.status_label_electrode.setText(status)


class GUIPlugin(Plugin):
    id = 'refrac_qt_microdrop.gui_plugin'

    def start(self):
        super().start()
        event_hub = self.application.get_service(EventHubPlugin)
        self.window = MainWindow(event_hub)
        self.window.show()
