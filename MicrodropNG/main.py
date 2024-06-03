# main.py
import sys
from PySide6.QtWidgets import QApplication
from envisage.api import Application

from MicrodropNG.utility_plugins.pub_sub_manager_plugin import PubSubManagerPlugin


def main():
    app = QApplication(sys.argv)

    plugins = [PubSubManagerPlugin()]
    envisage_app = Application(plugins=plugins)
    envisage_app.start()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
