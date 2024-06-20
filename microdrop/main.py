# main.py
import sys
from PySide6.QtWidgets import QApplication
from envisage.api import Application

from .plugins.backend_plugins.dropbot_controller import DropbotControllerPlugin


def main():
    app = QApplication(sys.argv)

    plugins = [DropbotControllerPlugin()]
    envisage_app = Application(plugins=plugins)
    envisage_app.start()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
