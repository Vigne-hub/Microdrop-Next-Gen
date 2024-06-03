# main.py
import sys
from PySide6.QtWidgets import QApplication
from envisage.api import Application
from MicroDropNG.plugins.backend_plugins.dropbot_controller import DropbotControllerPlugin
from MicroDropNG.plugins.frontend_plugins.dropbot_test_GUI import DropbotGUIPlugin
from MicroDropNG.plugins.control_plugins.event_hub import EventHubPlugin


def main():
    app = QApplication(sys.argv)

    plugins = [DropbotControllerPlugin(), EventHubPlugin(), DropbotGUIPlugin()]
    envisage_app = Application(plugins=plugins)
    envisage_app.start()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
