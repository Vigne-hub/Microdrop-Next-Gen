# main.py
import sys
from PySide6.QtWidgets import QApplication
from envisage.api import Application



def main():
    app = QApplication(sys.argv)

    plugins = []
    envisage_app = Application(plugins=plugins)
    envisage_app.start()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
