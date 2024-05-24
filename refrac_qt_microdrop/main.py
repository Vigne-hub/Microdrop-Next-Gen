# main.py
import sys
from PySide6.QtWidgets import QApplication
from envisage.api import Application
from backend_plugins.dropbot_controller import DropbotControllerPlugin
from frontend_plugins.dropbot_test_GUI import GUIPlugin
from backend_plugins.electrode_plugin import ElectrodeControllerPlugin
from event_hub import EventHubPlugin

def main():
    app = QApplication(sys.argv)

    plugins = [DropbotControllerPlugin(), ElectrodeControllerPlugin(), EventHubPlugin(), GUIPlugin()]
    envisage_app = Application(plugins=plugins)
    envisage_app.start()

    sys.exit(app.exec())

if __name__ == '__main__':
    main()
