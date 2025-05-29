# This module's package.
import os

PKG = '.'.join(__name__.split('.')[:-1])
PKG_name = PKG.title().replace("_", " ")

# Topics actor declared by plugin subscribes to
ACTOR_TOPIC_DICT = {
    f"{PKG}_listener": ["dropbot/signals/setup_success"]}

HELP_PATH = os.path.join(os.path.dirname(__file__), "help")