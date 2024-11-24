from dropbot_controller.consts import SELF_TESTS_PROGRESS

# This module's package.
PKG = '.'.join(__name__.split('.')[:-1])

# Topics this plugin wants some actors to subscribe to:
ACTOR_TOPIC_DICT = {
    "device_viewer_listener": [
                                 SELF_TESTS_PROGRESS,
    ]}


# Topics emitted by this plugin
ELECTRODES_STATE_CHANGE = 'dropbot/requests/electrodes_state_change'
