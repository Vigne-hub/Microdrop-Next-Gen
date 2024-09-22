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

# Dropbot Services Offered
DROPBOT_SERVICES_OFFERED = ["start_device_monitoring", "disconnected", "detect_shorts"]