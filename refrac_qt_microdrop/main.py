import sys
from PySide6.QtWidgets import QApplication
from envisage.api import Application
from backend_plugins.dropbot_controller import DropbotControllerPlugin
from frontend_plugins.dropbot_test_GUI import GUIPlugin

def main():
    app = QApplication(sys.argv)

    plugins = [DropbotControllerPlugin(), GUIPlugin()]
    envisage_app = Application(plugins=plugins)
    envisage_app.start()

    sys.exit(app.exec())

if __name__ == '__main__':
    main()
