# main.py
import sys
from PySide6.QtWidgets import QApplication
from envisage.api import Application

from .plugins.backend_plugins.dropbot_controller import DropbotControllerPlugin
from microdrop_utils.rmq_purger import RmqPurger


def main():
    app = QApplication(sys.argv)

    purger = RmqPurger()
    app.aboutToQuit.connect(purger.purge_all_queues)

    plugins = [DropbotControllerPlugin()]
    envisage_app = Application(plugins=plugins)
    envisage_app.start()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
