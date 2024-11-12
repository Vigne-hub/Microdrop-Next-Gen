# This module's package.
PKG = '.'.join(__name__.split('.')[:-1])

# dropbot DB3-120 hardware id
DROPBOT_DB3_120_HWID = 'VID:PID=16C0:0483'

# Chip may have been inserted before connecting, so `chip-inserted`
# event may have been missed.
# Explicitly check if chip is inserted by reading **active low**
# `OUTPUT_ENABLE_PIN`.
OUTPUT_ENABLE_PIN = 22

# Topics actor declared by plugin subscribes to
ACTOR_TOPIC_DICT = {
    "dropbot_controller_listener": [
        "dropbot/requests/#",
        "dropbot/signals/disconnected"
    ]}

# Topics published by this plugin
NO_DROPBOT_AVAILABLE = 'dropbot/signals/warnings/no_dropbot_available'
NO_POWER = 'dropbot/signals/warnings/no_power'
HALTED = 'dropbot/signals/halted'
CHIP_NOT_INSERTED = 'dropbot/signals/chip_not_inserted'
CHIP_INSERTED = 'dropbot/signals/chip_inserted'
SHORTS_DETECTED = 'dropbot/signals/shorts_detected'
CAPACITANCE_UPDATED = 'dropbot/signals/capacitance_updated'

# Dropbot Services Topics -- Offered by default from the dropbot monitor mixin in this package
START_DEVICE_MONITORING = "dropbot/requests/start_device_monitoring"
DETECT_SHORTS = "dropbot/requests/detect_shorts"
RETRY_CONNECTION = "dropbot/requests/retry_connection"
HALT = "dropbot/signals/halt"