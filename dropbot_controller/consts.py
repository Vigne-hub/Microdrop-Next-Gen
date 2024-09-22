# This module's package.
PKG = '.'.join(__name__.split('.')[:-1])

# dropbot DB3-120 hardware id
DROPBOT_DB3_120_HWID = 'VID:PID=16C0:0483'

# publishers
ACTOR_TOPIC_DICT = {
    "dropbot_backend_listener": [
                                 "dropbot/requests/#",
                                 "dropbot/signals/disconnected",
                                 "dropbot/signals/halted"
    ]}

# subscribers
NO_DROPBOT_AVAILABLE = 'dropbot/signals/connection/warnings/no_dropbot_available'
NO_POWER = 'dropbot/signals/connection/warnings/no_power'
CHIP_NOT_INSERTED = 'dropbot/signals/chip_not_inserted'
CHIP_INSERTED = 'dropbot/signals/chip_inserted'
HALTED = 'dropbot/signals/halted'
CAPACITANCE_UPDATED = 'dropbot/signals/capacitance_updated'
SHORTS_DETECTED = 'dropbot/signals/shorts_detected'

# Dropbot Services Topics -- Offered by default from the dropbot monitor mixin in this package
START_DEVICE_MONITORING = "dropbot/requests/start_device_monitoring"
DISCONNECTED = "dropbot/requests/disconnected"
DETECT_SHORTS = "dropbot/requests/detect_shorts"
RETRY_CONNECTION = "dropbot/requests/retry_connection"