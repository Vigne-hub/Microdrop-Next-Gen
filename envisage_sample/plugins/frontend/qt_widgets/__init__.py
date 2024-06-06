import os
import time
import logging
from pathlib import Path

from PySide6.QtCore import QCoreApplication, QSettings

APP_LEVEl_LOGFILE = f"application_logs{os.sep}application.log.{time.strftime('%Y-%m-%d_%H-%M-%S')}"


def get_id(name):
    return ".".join(name.split(".")[:-1])

def initialize_logger(name, level="DEBUG", log_file_path=APP_LEVEl_LOGFILE):
    levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }

    Path(log_file_path).parent.mkdir(parents=True, exist_ok=True)
    # Configure logging with more detailed output
    logging.basicConfig(
        format='%(asctime)s.%(msecs)03d [%(levelname)s:%('
               'name)s]: %(message)s File "%(pathname)s", line %(lineno)d',
        datefmt=r'%Y-%m-%d 'r'%H:%M:%S',
        handlers=[
            logging.FileHandler(log_file_path, mode='a'),
            logging.StreamHandler()
        ])

    logger = logging.getLogger(name)
    logger.setLevel(levels[level])

    return logger


def get_settings():
    # Specify the directory where you want to store the settings file
    directory = "settings"  # Change this to the desired path
    filename = "microdrop_qt.ini"
    full_path = os.path.join(directory, filename)

    # Make sure the directory exists
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Set up QSettings to use an INI file at the specified location
    QCoreApplication.setOrganizationName("Sci-Bots Inc.")
    QCoreApplication.setApplicationName("MicroDrop-Qt")

    settings = QSettings(full_path, QSettings.Format.IniFormat)

    return settings
