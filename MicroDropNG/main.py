# main.py
import sys
from PySide6.QtWidgets import QApplication
from envisage.api import Application
from envisage.core_plugin import CorePlugin

from plugins.control_plugins.event_hub import EventHubPlugin
from plugins.backend_plugins.dropbot_controller import DropbotControllerPlugin
from plugins.frontend_plugins.dropbot_test_GUI import DropbotGUIPlugin
from plugins.utility_plugins.pub_sub_manager_plugin import PubSubManagerPlugin


def main():
    app = QApplication(sys.argv)

    plugins = [CorePlugin(), PubSubManagerPlugin(), DropbotControllerPlugin(), EventHubPlugin(), DropbotGUIPlugin()]
    envisage_app = Application(plugins=plugins)
    envisage_app.start()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
