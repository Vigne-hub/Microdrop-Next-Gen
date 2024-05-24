# dropbot_test_GUI.py
from envisage.api import Plugin
from traits.api import List
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QFormLayout
from refrac_qt_microdrop.interfaces.event_hub_interface import IEventHubService

class DropbotGUI(QWidget):
    def __init__(self, event_hub_service):
        super().__init__()
        self.event_hub_service = event_hub_service
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Dropbot Controller')
        self.setGeometry(100, 100, 300, 200)

        layout = QVBoxLayout()

        form_layout = QFormLayout()

        self.voltage_input = QLineEdit()
        self.frequency_input = QLineEdit()
        self.channel_input = QLineEdit()
        self.state_input = QLineEdit()
        self.threshold_input = QLineEdit()

        form_layout.addRow('Voltage:', self.voltage_input)
        form_layout.addRow('Frequency:', self.frequency_input)
        form_layout.addRow('Channel:', self.channel_input)
        form_layout.addRow('State:', self.state_input)
        form_layout.addRow('Threshold:', self.threshold_input)

        self.status_label = QLabel('Status: Ready')

        self.buttons = {
            "Poll Voltage": QPushButton('Poll Voltage'),
            "Set Voltage": QPushButton('Set Voltage'),
            "Set Frequency": QPushButton('Set Frequency'),
            "Set HV": QPushButton('Set HV'),
            "Get Channels": QPushButton('Get Channels'),
            "Set Channels": QPushButton('Set Channels'),
            "Set Channel Single": QPushButton('Set Channel Single'),
            "Droplet Search": QPushButton('Droplet Search')
        }

        for button_name, button in self.buttons.items():
            layout.addWidget(button)
            button.clicked.connect(lambda _, bn=button_name: self.button_clicked(bn))

        layout.addWidget(self.status_label)
        self.setLayout(layout)

    def button_clicked(self, button_name):
        task_map = {
            "Poll Voltage": ("dropbot_interface.IDropbotControllerService", "poll_voltage", [], {}),
            "Set Voltage": ("dropbot_interface.IDropbotControllerService", "set_voltage", [self.voltage_input.text()], {}),
            "Set Frequency": ("dropbot_interface.IDropbotControllerService", "set_frequency", [self.frequency_input.text()], {}),
            "Set HV": ("dropbot_interface.IDropbotControllerService", "set_hv", [self.state_input.text()], {}),
            "Get Channels": ("dropbot_interface.IDropbotControllerService", "get_channels", [], {}),
            "Set Channels": ("dropbot_interface.IDropbotControllerService", "set_channels", [self.channel_input.text()], {}),
            "Set Channel Single": ("dropbot_interface.IDropbotControllerService", "set_channel_single", [self.channel_input.text(), self.state_input.text()], {}),
            "Droplet Search": ("dropbot_interface.IDropbotControllerService", "droplet_search", [self.threshold_input.text()], {})
        }

        if button_name in task_map:
            plugin_name, task_name, args, kwargs = task_map[button_name]
            self.event_hub_service.send_task(plugin_name, task_name, args, kwargs)
            self.status_label.setText(f'Status: {button_name} clicked...')

class DropbotGUIPlugin(Plugin):
    id = 'refrac_qt_microdrop.gui'
    name = 'Dropbot GUI Plugin'
    service_offers = List(contributes_to='envisage.service_offers')

    def start(self):
        super().start()
        self._register_services()
        self._create_gui()

    def _register_services(self):
        event_hub_service = self.application.get_service(IEventHubService)
        self._gui = DropbotGUI(event_hub_service)

    def _create_gui(self):
        self._gui.show()
