from envisage.api import Plugin, ServiceOffer
from traits.api import List
from PySide6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget
from PySide6.QtCore import Slot
from refrac_qt_microdrop.interfaces import IVoltageService, IOutputService, IChannelService


class MainWindow(QMainWindow):
    def __init__(self, voltage_service, output_service, channel_service):
        super().__init__()
        self.voltage_service = voltage_service
        self.output_service = output_service
        self.channel_service = channel_service

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.set_voltage_button = QPushButton("Set Voltage")
        self.set_voltage_button.clicked.connect(self.set_voltage)
        layout.addWidget(self.set_voltage_button)

        self.set_output_button = QPushButton("Set Output")
        self.set_output_button.clicked.connect(self.set_output)
        layout.addWidget(self.set_output_button)

        self.set_channels_button = QPushButton("Set Channels")
        self.set_channels_button.clicked.connect(self.set_channels)
        layout.addWidget(self.set_channels_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    @Slot()
    def set_voltage(self):
        self.voltage_service.set_voltage(5)
        print("Voltage set to 5")

    @Slot()
    def set_output(self):
        self.output_service.set_output(True)
        print("Output enabled")

    @Slot()
    def set_channels(self):
        channels = self.channel_service.get_channels()
        print("Channels:", channels)


class FrontendPlugin(Plugin):
    id = 'app.frontend.plugin'
    name = 'Frontend Plugin'
    service_offers = List(contributes_to='envisage.service_offers')

    def start(self):
        super().start()
        self._register_services()

    def _register_services(self):
        voltage_service = self.application.get_service(IVoltageService)
        output_service = self.application.get_service(IOutputService)
        channel_service = self.application.get_service(IChannelService)

        if voltage_service and output_service and channel_service:
            main_window = self._create_main_window(voltage_service, output_service, channel_service)
            self.application.register_service(QMainWindow, main_window)
        else:
            print("One or more services not found")

    def _service_offers_default(self):
        return []

    def _create_main_window(self, voltage_service, output_service, channel_service):
        print("Creating main window service")
        main_window = MainWindow(voltage_service, output_service, channel_service)
        print("Main window service created:", main_window)
        return main_window
