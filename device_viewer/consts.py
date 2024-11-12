from dropbot_controller.consts import CHIP_INSERTED

# This module's package.
PKG = '.'.join(__name__.split('.')[:-1])

# Topics actor declared by plugin subscribes to
ACTOR_TOPIC_DICT = {
    "device_viewer_listener": [
                                 CHIP_INSERTED,
    ]}


# Topics emitted by this plugin
ELECTRODES_STATE_CHANGE = 'dropbot/requests/electrodes_state_change'