from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel
from envisage.api import Plugin
from traits.api import List, Instance
from refrac_qt_microdrop.interfaces.dropbot_interface import IDropbotControllerService


class MainWindow(QMainWindow):
    def __init__(self, dropbot_service):
        super().__init__()
        self.dropbot_service = dropbot_service
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Dropbot Controller Test GUI")
        self.setGeometry(100, 100, 400, 300)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        self.status_label = QLabel("Status: Ready", self)
        layout.addWidget(self.status_label)

        init_btn = QPushButton("Initialize Dropbot", self)
        init_btn.clicked.connect(self.init_dropbot)
        layout.addWidget(init_btn)

        voltage_btn = QPushButton("Set Voltage to 10", self)
        voltage_btn.clicked.connect(lambda: self.set_voltage(10))
        layout.addWidget(voltage_btn)

        central_widget.setLayout(layout)

    def init_dropbot(self):
        self.dropbot_service.init_dropbot_proxy()
        self.status_label.setText("Status: Dropbot Initialized")

    def set_voltage(self, voltage):
        print(f"Attempting to set voltage to {voltage}")
        print(f"dropbot_service: {self.dropbot_service}")
        self.dropbot_service.set_voltage(voltage)
        self.status_label.setText(f"Status: Voltage set to {voltage}")


class GUIPlugin(Plugin):
    id = 'refrac_qt_microdrop.gui_plugin'

    def start(self):
        super().start()
        dropbot_service = self.application.get_service(IDropbotControllerService)
        self.window = MainWindow(dropbot_service)
        self.window.show()
