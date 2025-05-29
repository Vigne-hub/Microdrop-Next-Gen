# This module's package.
import os
from dropbot_controller.consts import DROPBOT_SETUP_SUCCESS

PKG = '.'.join(__name__.split('.')[:-1])
PKG_name = PKG.title().replace("_", " ")

# Topics actor declared by plugin subscribes to
ACTOR_TOPIC_DICT = {
    f"{PKG}_listener": [DROPBOT_SETUP_SUCCESS]}

HELP_PATH = os.path.join(os.path.dirname(__file__), "help")