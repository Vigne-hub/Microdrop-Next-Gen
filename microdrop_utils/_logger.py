import os
import time
import logging
from pathlib import Path

LOGFILE = f"application_logs{os.sep}application.log.{time.strftime('%Y-%m-%d_%H-%M-%S')}"


def get_logger(name, level="DEBUG", log_file_path=LOGFILE):
  
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